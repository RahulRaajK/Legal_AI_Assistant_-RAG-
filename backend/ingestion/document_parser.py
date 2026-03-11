"""Document parser for PDFs, DOCX, and text files."""
import os
import re
from typing import Optional
from PyPDF2 import PdfReader


class DocumentParser:
    """Parses various document formats into plain text."""
    
    def parse_file(self, file_path: str) -> dict:
        """Parse a file and return text with metadata."""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            return self.parse_pdf(file_path)
        elif ext == ".txt":
            return self.parse_text(file_path)
        elif ext in (".doc", ".docx"):
            return self.parse_docx(file_path)
        else:
            return {"text": "", "pages": 0, "error": f"Unsupported format: {ext}"}
    
    def parse_pdf(self, file_path: str) -> dict:
        """Extract text from a PDF file."""
        try:
            reader = PdfReader(file_path)
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            
            full_text = "\n\n".join(pages)
            return {
                "text": full_text,
                "pages": len(reader.pages),
                "file_name": os.path.basename(file_path),
            }
        except Exception as e:
            return {"text": "", "pages": 0, "error": str(e)}
    
    def parse_text(self, file_path: str) -> dict:
        """Read a plain text file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            return {
                "text": text,
                "pages": 1,
                "file_name": os.path.basename(file_path),
            }
        except Exception as e:
            return {"text": "", "pages": 0, "error": str(e)}
    
    def parse_docx(self, file_path: str) -> dict:
        """Extract text from a DOCX file."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs)
            return {
                "text": full_text,
                "pages": 1,
                "file_name": os.path.basename(file_path),
            }
        except Exception as e:
            return {"text": "", "pages": 0, "error": str(e)}
    
    def extract_metadata_from_text(self, text: str) -> dict:
        """Try to extract legal metadata from document text."""
        metadata = {}
        
        # Try to find act names
        act_patterns = [
            r'((?:The\s+)?[\w\s]+(?:Act|Sanhita|Adhiniyam|Code|Bill),?\s*(?:19|20)\d{2})',
            r'((?:Indian|Bharatiya)\s+[\w\s]+(?:Act|Sanhita|Adhiniyam|Code))',
        ]
        for pattern in act_patterns:
            match = re.search(pattern, text[:2000], re.IGNORECASE)
            if match:
                metadata["act_name"] = match.group(1).strip()
                break
        
        # Find section numbers
        section_match = re.search(r'Section\s+(\d+[A-Z]?)', text[:2000], re.IGNORECASE)
        if section_match:
            metadata["section_number"] = section_match.group(1)
        
        # Find article numbers
        article_match = re.search(r'Article\s+(\d+[A-Z]?)', text[:2000], re.IGNORECASE)
        if article_match:
            metadata["article_number"] = article_match.group(1)
        
        # Find year
        year_match = re.search(r'\b(19|20)\d{2}\b', text[:1000])
        if year_match:
            metadata["year"] = int(year_match.group())
        
        return metadata


document_parser = DocumentParser()
