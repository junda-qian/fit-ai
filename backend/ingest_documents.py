#!/usr/bin/env python3
"""
Document Ingestion Script for Evidence-Based Health Chatbot

This script processes PDF documents and creates a vector database
for semantic search and retrieval.
"""

import os
import sys
from dotenv import load_dotenv
from document_processor import DocumentProcessor
from embeddings import BedrockEmbeddings
from vector_store import VectorStore
import time
import pickle
import json

# Load environment variables
load_dotenv()


def main():
    print("=" * 60)
    print("Evidence-Based Health Chatbot - Document Ingestion")
    print("=" * 60)

    # Configuration
    documents_dir = "./documents"
    use_opensearch = os.getenv("USE_OPENSEARCH", "false").lower() == "true"
    batch_size = 10  # Process 10 chunks at a time
    max_workers = 1  # Sequential processing (no parallelism to avoid throttling)

    # Initialize components
    print("\n1. Initializing document processor...")
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)

    print("2. Initializing embeddings (AWS Bedrock Titan with parallel processing)...")
    embeddings = BedrockEmbeddings(max_workers=max_workers)

    print(f"3. Initializing vector store ({'OpenSearch' if use_opensearch else 'FAISS'})...")
    vector_store = VectorStore(use_opensearch=use_opensearch)

    # Load and process documents
    print(f"\n4. Loading PDFs from {documents_dir}...")
    chunks = processor.load_all_pdfs(documents_dir)

    if not chunks:
        print("\n❌ No documents found or processed!")
        print(f"Please add PDF files to: {os.path.abspath(documents_dir)}")
        sys.exit(1)

    print(f"\n✓ Processed {len(chunks)} text chunks from PDFs")

    # Generate embeddings in batches
    print(f"\n5. Generating embeddings in batches of {batch_size} ({max_workers} parallel calls per batch)...")
    print(f"   Total chunks: {len(chunks)}")
    # With parallelization: ~10x faster
    estimated_minutes = (len(chunks) / batch_size) * 0.3  # Much faster with parallel processing
    print(f"   Estimated time: ~{estimated_minutes:.1f} minutes (with parallel processing)")

    texts = [chunk["text"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    # Check for resume file
    progress_file = "ingestion_progress.pkl"
    start_index = 0
    all_embeddings = []

    if os.path.exists(progress_file):
        print(f"\n   📁 Found progress file - resuming from previous run...")
        with open(progress_file, 'rb') as f:
            progress_data = pickle.load(f)
            start_index = progress_data['next_index']
            all_embeddings = progress_data['embeddings']
        print(f"   ✓ Resuming from chunk {start_index} ({len(all_embeddings)} embeddings already processed)")

    total_batches = (len(texts) + batch_size - 1) // batch_size

    for i in range(start_index, len(texts), batch_size):
        batch_num = i // batch_size + 1
        batch_texts = texts[i:i + batch_size]

        print(f"   Batch {batch_num}/{total_batches}: Processing {len(batch_texts)} chunks...", end=" ", flush=True)

        try:
            start_time = time.time()
            batch_embeddings = embeddings.embed_documents(batch_texts)
            elapsed = time.time() - start_time

            all_embeddings.extend(batch_embeddings)
            chunks_per_second = len(batch_texts) / elapsed if elapsed > 0 else 0
            print(f"✓ ({elapsed:.1f}s - {chunks_per_second:.1f} chunks/sec)")

            # Save progress after each batch
            with open(progress_file, 'wb') as f:
                pickle.dump({
                    'next_index': i + batch_size,
                    'embeddings': all_embeddings
                }, f)

            # Delay to respect AWS rate limits
            if i + batch_size < len(texts):
                time.sleep(0.2)  # Small delay between chunks

        except Exception as e:
            print(f"✗ Error: {str(e)}")
            print(f"\n❌ Failed at batch {batch_num}")
            print(f"Processed {len(all_embeddings)} embeddings before failure")
            print(f"\n💾 Progress saved! Run the script again to resume from batch {batch_num + 1}")
            sys.exit(1)

    print(f"\n   ✓ Generated {len(all_embeddings)} embeddings total")

    # Store in vector database
    print("\n6. Storing in vector database...")
    vector_store.add_documents(texts, all_embeddings, metadatas)

    # Clean up progress file on success
    if os.path.exists(progress_file):
        os.remove(progress_file)
        print("   ✓ Cleaned up progress file")

    # Summary
    print("\n" + "=" * 60)
    print("✅ Document Ingestion Complete!")
    print("=" * 60)

    stats = vector_store.get_stats()
    print(f"\nVector Store Stats:")
    print(f"  Type: {stats['type']}")
    print(f"  Total Documents: {stats['total_docs']}")

    if not use_opensearch:
        print(f"\nLocal files created:")
        print(f"  - faiss_index.pkl")
        print(f"  - faiss_metadata.json")

    print(f"\nYour health chatbot is now ready to answer questions!")
    print(f"Start the server with: uvicorn server:app --reload")


if __name__ == "__main__":
    main()
