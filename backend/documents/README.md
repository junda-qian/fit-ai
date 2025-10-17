# Health Documents Directory

This directory contains the PDF health textbooks and medical documents that the chatbot uses to answer questions.

## How to Add Documents

1. Place your PDF files in this directory
2. Run the ingestion script to process and index them:
   ```bash
   python ingest_documents.py
   ```

## Current Documents

After adding PDFs, they will be listed here automatically.

## Document Guidelines

- **Format**: PDF only
- **Content**: Health textbooks, medical guidelines, research papers
- **Quantity**: Recommended 20-30 PDFs for optimal coverage
- **Size**: Keep individual files under 50MB for best performance

## Processing

The ingestion script will:
1. Extract text from each PDF page
2. Split text into manageable chunks (1000 chars with 200 char overlap)
3. Generate embeddings using AWS Bedrock Titan
4. Store vectors in FAISS (local) or OpenSearch (production)

## Notes

- Documents are chunked to preserve context while fitting in model limits
- Page numbers and source files are tracked for reference
- URLs within documents are extracted for potential research links
