#!/usr/bin/env python3
"""Delete OpenSearch index only (not the collection)"""

from upload_to_opensearch import get_opensearch_client, INDEX_NAME, OPENSEARCH_ENDPOINT

def main():
    print(f"Connecting to OpenSearch at {OPENSEARCH_ENDPOINT}...")
    client = get_opensearch_client()

    if client.indices.exists(index=INDEX_NAME):
        print(f"Deleting index: {INDEX_NAME}...")
        client.indices.delete(index=INDEX_NAME)
        print(f"✓ Deleted index: {INDEX_NAME}")
    else:
        print(f"Index {INDEX_NAME} does not exist")

if __name__ == "__main__":
    main()
