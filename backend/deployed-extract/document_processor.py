from pypdf import PdfReader
from typing import List, Dict
import os
import re


class DocumentProcessor:
    """Process PDF documents for RAG system"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def load_pdf(self, pdf_path: str) -> List[Dict]:
        """
        Load and process a PDF file into chunks

        Returns:
            List of dicts with keys: text, metadata (source, page, chunk_id)
        """
        try:
            reader = PdfReader(pdf_path)
            filename = os.path.basename(pdf_path)
            chunks = []

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    # Split page text into chunks
                    page_chunks = self._chunk_text(text, page_num + 1, filename)
                    chunks.extend(page_chunks)

            return chunks

        except Exception as e:
            print(f"Error loading PDF {pdf_path}: {str(e)}")
            return []

    def load_all_pdfs(self, documents_dir: str) -> List[Dict]:
        """Load all PDFs from a directory"""
        all_chunks = []

        if not os.path.exists(documents_dir):
            print(f"Documents directory not found: {documents_dir}")
            return []

        pdf_files = [f for f in os.listdir(documents_dir) if f.endswith('.pdf')]

        if not pdf_files:
            print(f"No PDF files found in {documents_dir}")
            return []

        for pdf_file in pdf_files:
            pdf_path = os.path.join(documents_dir, pdf_file)
            print(f"Processing: {pdf_file}")
            chunks = self.load_pdf(pdf_path)
            all_chunks.extend(chunks)

        print(f"Total chunks created: {len(all_chunks)}")
        return all_chunks

    def _chunk_text(self, text: str, page_num: int, filename: str) -> List[Dict]:
        """
        Split text into overlapping chunks

        Args:
            text: The text to chunk
            page_num: Page number
            filename: Source filename

        Returns:
            List of chunk dictionaries
        """
        # Clean text
        text = self._clean_text(text)

        # Simple chunking by character count with overlap
        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                sentence_end = self._find_sentence_boundary(text, end)
                if sentence_end > start:
                    end = sentence_end

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "metadata": {
                        "source": filename,
                        "page": page_num,
                        "chunk_id": chunk_id
                    }
                })
                chunk_id += 1

            # Move start position with overlap
            start = end - self.chunk_overlap

        return chunks

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and headers/footers (simple heuristic)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        return text.strip()

    def _find_sentence_boundary(self, text: str, pos: int) -> int:
        """Find the nearest sentence boundary after position"""
        # Look ahead for sentence endings
        search_text = text[pos:pos + 100]
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']

        min_pos = len(text)
        for ending in sentence_endings:
            idx = search_text.find(ending)
            if idx != -1 and idx < min_pos:
                min_pos = idx + len(ending)

        if min_pos < len(text):
            return pos + min_pos
        return pos

    def extract_urls_from_text(self, text: str) -> List[str]:
        """Extract URLs from text (for research paper links)"""
        url_pattern = r'https?://[^\s\)\]>]+'
        urls = re.findall(url_pattern, text)
        return urls
