#!/usr/bin/env python3
"""
Upload FAISS vector store to OpenSearch Serverless
"""

import os
import pickle
import json
import boto3
import numpy as np
import time
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from dotenv import load_dotenv

load_dotenv()

# OpenSearch configuration from Terraform outputs
OPENSEARCH_ENDPOINT = os.getenv("OPENSEARCH_ENDPOINT", "https://fxe1hizqsjbtg7kw8es5.us-east-1.aoss.amazonaws.com")
INDEX_NAME = "health-docs"
REGION = "us-east-1"

def get_opensearch_client():
    """Create OpenSearch client with AWS authentication"""
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        'aoss',
        session_token=credentials.token
    )

    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT.replace('https://', ''), 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30
    )

    return client

def create_index(client):
    """Create OpenSearch index with vector search configuration"""
    index_body = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 512
            }
        },
        "mappings": {
            "properties": {
                "vector": {
                    "type": "knn_vector",
                    "dimension": 1536,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "faiss",
                        "parameters": {
                            "ef_construction": 512,
                            "m": 16
                        }
                    }
                },
                "text": {
                    "type": "text"
                },
                "metadata": {
                    "type": "object",
                    "enabled": True
                }
            }
        }
    }

    # Delete existing index if it exists to ensure correct dimension
    try:
        if client.indices.exists(index=INDEX_NAME):
            print(f"⚠ Deleting existing index to recreate with correct dimension...")
            client.indices.delete(index=INDEX_NAME)
            print(f"✓ Deleted old index: {INDEX_NAME}")
    except Exception as e:
        print(f"Note: Could not check/delete existing index: {e}")

    # Create new index
    client.indices.create(index=INDEX_NAME, body=index_body)
    print(f"✓ Created index: {INDEX_NAME} with dimension 1536")

    # Wait for index to be fully initialized in OpenSearch Serverless
    print("⏳ Waiting 10 seconds for index to initialize...")
    time.sleep(10)

def upload_documents(client):
    """Upload documents from FAISS to OpenSearch"""
    # Load FAISS index
    print("\nLoading FAISS index...")
    with open('faiss_index.pkl', 'rb') as f:
        faiss_index = pickle.load(f)

    # Load metadata
    with open('faiss_metadata.json', 'r') as f:
        metadata_list = json.load(f)

    # Extract texts and metadatas from list
    texts = [item['text'] for item in metadata_list]
    metadatas = [item['metadata'] for item in metadata_list]

    # Extract vectors from FAISS index
    import faiss
    n_vectors = faiss_index.ntotal
    vectors = np.zeros((n_vectors, faiss_index.d), dtype=np.float32)
    faiss_index.reconstruct_n(0, n_vectors, vectors)

    print(f"Found {len(texts)} documents to upload")

    # Upload in batches
    batch_size = 100
    total = len(texts)

    for i in range(0, total, batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_vectors = vectors[i:i + batch_size]
        batch_metadatas = metadatas[i:i + batch_size]

        # Prepare bulk upload
        bulk_data = []
        for j, (text, vector, meta) in enumerate(zip(batch_texts, batch_vectors, batch_metadatas)):
            # Index action (no _id for OpenSearch Serverless)
            bulk_data.append(json.dumps({"index": {"_index": INDEX_NAME}}))

            # Document data
            doc = {
                "vector": vector.tolist() if hasattr(vector, 'tolist') else list(vector),
                "text": text,
                "metadata": meta
            }
            bulk_data.append(json.dumps(doc))

        # Upload batch
        body = '\n'.join(bulk_data) + '\n'
        response = client.bulk(body=body)

        if response['errors']:
            print(f"✗ Errors in batch {i // batch_size + 1}")
            for item in response['items']:
                if 'error' in item.get('index', {}):
                    print(f"   Error: {item['index']['error']}")
        else:
            print(f"✓ Uploaded batch {i // batch_size + 1}/{(total + batch_size - 1) // batch_size} ({len(batch_texts)} docs)")

    print(f"\n✓ Successfully uploaded {total} documents to OpenSearch")

def main():
    print("=" * 60)
    print("Upload FAISS Vector Store to OpenSearch Serverless")
    print("=" * 60)

    # Check if FAISS files exist
    if not os.path.exists('faiss_index.pkl'):
        print("\n❌ faiss_index.pkl not found!")
        print("Please run ingest_documents.py first to create the vector store")
        return

    if not os.path.exists('faiss_metadata.json'):
        print("\n❌ faiss_metadata.json not found!")
        print("Please run ingest_documents.py first to create the vector store")
        return

    print(f"\n1. Connecting to OpenSearch at {OPENSEARCH_ENDPOINT}...")
    client = get_opensearch_client()

    print("2. Creating index...")
    create_index(client)

    print("3. Uploading documents...")
    upload_documents(client)

    # Verify
    print("\n4. Verifying upload...")
    count = client.count(index=INDEX_NAME)
    print(f"✓ Total documents in OpenSearch: {count['count']}")

    print("\n" + "=" * 60)
    print("✅ Upload Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
