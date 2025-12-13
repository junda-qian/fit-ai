import boto3
import os
from typing import List
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class BedrockEmbeddings:
    """AWS Bedrock Titan Embeddings wrapper"""

    def __init__(self, region_name: str = None, max_workers: int = 10):
        self.region_name = region_name or os.getenv("AWS_REGION", os.getenv("DEFAULT_AWS_REGION", "us-east-1"))

        # Create Bedrock runtime client with explicit region
        self.bedrock_client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region_name
        )

        self.model_id = "amazon.titan-embed-text-v1"
        self.dimension = 1536  # Bedrock Titan V1 embedding dimension
        self.max_workers = max_workers  # Number of parallel threads

        print(f"Initialized Bedrock embeddings in region: {self.region_name}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using parallel processing"""
        if not texts:
            return []

        # Use ThreadPoolExecutor for parallel API calls
        embeddings = [None] * len(texts)  # Pre-allocate to preserve order

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all embedding tasks
            future_to_index = {
                executor.submit(self._embed_single, text): i
                for i, text in enumerate(texts)
            }

            # Collect results as they complete
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    embeddings[index] = future.result()
                except Exception as e:
                    print(f"Error embedding text at index {index}: {e}")
                    # Retry with longer wait on failure
                    print(f"   Waiting 10 seconds before retry...")
                    time.sleep(10)
                    try:
                        embeddings[index] = self._embed_single(texts[index])
                        print(f"   ✓ Retry successful")
                    except Exception as retry_error:
                        # Try one more time with even longer wait
                        print(f"   Second retry after 30 seconds...")
                        time.sleep(30)
                        try:
                            embeddings[index] = self._embed_single(texts[index])
                            print(f"   ✓ Second retry successful")
                        except:
                            raise Exception(f"Failed to embed text at index {index} after 2 retries: {retry_error}")

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._embed_single(text)

    def _embed_single(self, text: str) -> List[float]:
        """Embed a single text using Bedrock Titan"""
        # Truncate text if too long (max 8000 tokens ~30k chars)
        max_chars = 25000
        if len(text) > max_chars:
            text = text[:max_chars]

        request_body = {
            "inputText": text
        }

        response = self.bedrock_client.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        embedding = response_body.get('embedding')

        return embedding

    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.dimension
