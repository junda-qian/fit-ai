from typing import List, Dict, Optional
from embeddings import BedrockEmbeddings
from vector_store import VectorStore
import re


class HealthRAG:
    """RAG system for evidence-based health chatbot"""

    def __init__(self, use_opensearch: bool = False):
        self.embeddings = BedrockEmbeddings()
        self.vector_store = VectorStore(use_opensearch=use_opensearch)

    def retrieve_context(self, query: str, top_k: int = 5) -> tuple[str, List[Dict]]:
        """
        Retrieve relevant context for a query

        Returns:
            tuple: (formatted_context_string, list of source documents)
        """
        # Embed the query
        query_embedding = self.embeddings.embed_query(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, k=top_k)

        if not results:
            return "", []

        # Format context for LLM
        context_parts = []
        sources = []

        for i, result in enumerate(results):
            text = result['text']
            metadata = result['metadata']

            # Extract any URLs from the text
            urls = self._extract_urls(text)

            # Format context piece
            context_parts.append(
                f"[Source {i+1}: {metadata['source']}, Page {metadata['page']}]\n{text}\n"
            )

            # Track source for potential display
            source_info = {
                "source": metadata['source'],
                "page": metadata['page'],
                "text": text,
                "urls": urls
            }
            sources.append(source_info)

        context_str = "\n".join(context_parts)
        return context_str, sources

    def is_health_related(self, query: str) -> bool:
        """
        Simple heuristic to check if query is health-related

        You can make this more sophisticated with ML classification
        """
        health_keywords = [
            'health', 'medical', 'disease', 'symptom', 'treatment', 'medication',
            'diagnosis', 'condition', 'patient', 'doctor', 'clinic', 'hospital',
            'pain', 'fever', 'infection', 'therapy', 'surgery', 'prescription',
            'vitamin', 'nutrition', 'diet', 'exercise', 'wellness', 'chronic',
            'acute', 'cancer', 'diabetes', 'heart', 'blood', 'pressure'
        ]

        query_lower = query.lower()
        return any(keyword in query_lower for keyword in health_keywords)

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s\)\]\>]+'
        urls = re.findall(url_pattern, text)
        return urls

    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        return self.vector_store.get_stats()
