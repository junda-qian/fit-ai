import os
import json
import pickle
from typing import List, Dict, Optional
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth
import numpy as np


class VectorStore:
    """Unified vector store interface for local (FAISS) and AWS (OpenSearch)"""

    def __init__(self, use_opensearch: bool = False):
        self.use_opensearch = use_opensearch
        self.dimension = 1536  # Bedrock Titan V1 embedding dimension

        if use_opensearch:
            self._init_opensearch()
        else:
            self._init_faiss()

    def _init_faiss(self):
        """Initialize FAISS for local development"""
        import faiss

        self.index_path = "./faiss_index.pkl"
        self.metadata_path = "./faiss_metadata.json"

        if os.path.exists(self.index_path):
            with open(self.index_path, 'rb') as f:
                self.index = pickle.load(f)
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
            print(f"Loaded FAISS index with {self.index.ntotal} vectors")
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            print("Created new FAISS index")

    def _init_opensearch(self):
        """Initialize OpenSearch Serverless"""
        self.region = os.getenv("DEFAULT_AWS_REGION", "us-east-1")
        self.collection_endpoint = os.getenv("OPENSEARCH_ENDPOINT")
        self.index_name = "health-docs"

        if not self.collection_endpoint:
            raise ValueError("OPENSEARCH_ENDPOINT environment variable not set")

        # AWS authentication
        credentials = boto3.Session().get_credentials()
        auth = AWSV4SignerAuth(credentials, self.region, 'aoss')

        self.client = OpenSearch(
            hosts=[{'host': self.collection_endpoint.replace('https://', ''), 'port': 443}],
            http_auth=auth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            timeout=30
        )

        # Create index if it doesn't exist
        self._create_index_if_not_exists()

    def _create_index_if_not_exists(self):
        """Create OpenSearch index with proper mapping"""
        if not self.client.indices.exists(index=self.index_name):
            index_body = {
                "settings": {
                    "index.knn": True
                },
                "mappings": {
                    "properties": {
                        "vector": {
                            "type": "knn_vector",
                            "dimension": self.dimension,
                            "method": {
                                "name": "hnsw",
                                "engine": "faiss",
                                "parameters": {
                                    "ef_construction": 512,
                                    "m": 16
                                }
                            }
                        },
                        "text": {"type": "text"},
                        "metadata": {
                            "properties": {
                                "source": {"type": "keyword"},
                                "page": {"type": "integer"},
                                "chunk_id": {"type": "integer"}
                            }
                        }
                    }
                }
            }
            self.client.indices.create(index=self.index_name, body=index_body)
            print(f"Created OpenSearch index: {self.index_name}")

    def add_documents(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict]):
        """Add documents to the vector store"""
        if self.use_opensearch:
            self._add_to_opensearch(texts, embeddings, metadatas)
        else:
            self._add_to_faiss(texts, embeddings, metadatas)

    def _add_to_faiss(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict]):
        """Add to FAISS index"""
        import faiss

        embeddings_array = np.array(embeddings).astype('float32')

        # Check if we need to recreate the index with correct dimension
        if self.index.ntotal == 0 and embeddings_array.shape[1] != self.dimension:
            print(f"Recreating FAISS index with dimension {embeddings_array.shape[1]}")
            self.dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(self.dimension)

        self.index.add(embeddings_array)

        # Store metadata
        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            self.metadata.append({
                "text": text,
                "metadata": metadata,
                "id": len(self.metadata)
            })

        # Save index and metadata
        with open(self.index_path, 'wb') as f:
            pickle.dump(self.index, f)
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f)

        print(f"Added {len(texts)} documents to FAISS. Total: {self.index.ntotal}")

    def _add_to_opensearch(self, texts: List[str], embeddings: List[List[float]], metadatas: List[Dict]):
        """Add to OpenSearch"""
        for text, embedding, metadata in zip(texts, embeddings, metadatas):
            doc = {
                "text": text,
                "vector": embedding,
                "metadata": metadata
            }
            self.client.index(index=self.index_name, body=doc)

        print(f"Added {len(texts)} documents to OpenSearch")

    def search(self, query_embedding: List[float], k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        if self.use_opensearch:
            return self._search_opensearch(query_embedding, k)
        else:
            return self._search_faiss(query_embedding, k)

    def _search_faiss(self, query_embedding: List[float], k: int) -> List[Dict]:
        """Search FAISS index"""
        if self.index.ntotal == 0:
            return []

        query_vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))

        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['score'] = float(distance)
                results.append(result)

        return results

    def _search_opensearch(self, query_embedding: List[float], k: int) -> List[Dict]:
        """Search OpenSearch index"""
        query = {
            "size": k,
            "query": {
                "knn": {
                    "vector": {
                        "vector": query_embedding,
                        "k": k
                    }
                }
            }
        }

        response = self.client.search(index=self.index_name, body=query)

        results = []
        for hit in response['hits']['hits']:
            results.append({
                "text": hit['_source']['text'],
                "metadata": hit['_source']['metadata'],
                "score": hit['_score']
            })

        return results

    def clear(self):
        """Clear all documents from the vector store"""
        if self.use_opensearch:
            self.client.indices.delete(index=self.index_name, ignore=[400, 404])
            self._create_index_if_not_exists()
        else:
            import faiss

            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.metadata_path):
                os.remove(self.metadata_path)

        print("Vector store cleared")

    def get_stats(self) -> Dict:
        """Get statistics about the vector store"""
        if self.use_opensearch:
            stats = self.client.indices.stats(index=self.index_name)
            return {
                "type": "opensearch",
                "total_docs": stats['indices'][self.index_name]['total']['docs']['count']
            }
        else:
            return {
                "type": "faiss",
                "total_docs": self.index.ntotal
            }
