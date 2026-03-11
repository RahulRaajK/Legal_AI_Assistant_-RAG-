"""Smart text chunker for legal documents."""
import re
import uuid
from typing import Optional


class LegalChunker:
    """Chunks legal text with section awareness and metadata propagation."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
    ) -> list[dict]:
        """Split text into chunks with metadata."""
        if not text.strip():
            return []
        
        metadata = metadata or {}
        
        # Try section-aware splitting first
        sections = self._split_by_sections(text)
        
        if sections:
            return self._process_sections(sections, metadata)
        
        # Fall back to simple chunking
        return self._simple_chunk(text, metadata)
    
    def _split_by_sections(self, text: str) -> list[dict]:
        """Split by legal section markers."""
        patterns = [
            r'(?=Section\s+\d+[A-Z]?\.?\s)',
            r'(?=Article\s+\d+[A-Z]?\.?\s)',
            r'(?=CHAPTER\s+[IVXLCDM]+)',
            r'(?=PART\s+[IVXLCDM]+)',
            r'(?=\d+\.\s+[A-Z])',
        ]
        
        for pattern in patterns:
            parts = re.split(pattern, text)
            if len(parts) > 1:
                sections = []
                for part in parts:
                    if part.strip():
                        # Extract section number
                        sec_match = re.match(r'(Section|Article)\s+(\d+[A-Z]?)', part, re.IGNORECASE)
                        section_num = sec_match.group(2) if sec_match else ""
                        section_type = sec_match.group(1) if sec_match else ""
                        
                        sections.append({
                            "text": part.strip(),
                            "section_number": section_num,
                            "section_type": section_type,
                        })
                return sections
        
        return []
    
    def _process_sections(self, sections: list[dict], base_metadata: dict) -> list[dict]:
        """Process sections, further chunking large ones."""
        chunks = []
        for section in sections:
            text = section["text"]
            section_meta = {
                **base_metadata,
                "section_number": section.get("section_number", base_metadata.get("section_number", "")),
            }
            
            if len(text) <= self.chunk_size:
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": text,
                    "metadata": section_meta,
                })
            else:
                sub_chunks = self._simple_chunk(text, section_meta)
                chunks.extend(sub_chunks)
        
        return chunks
    
    def _simple_chunk(self, text: str, metadata: dict) -> list[dict]:
        """Simple overlapping window chunking."""
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < text_len:
                last_period = text.rfind('.', start + self.chunk_size // 2, end)
                if last_period > start:
                    end = last_period + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "metadata": {**metadata},
                })
            
            start = end - self.chunk_overlap
            if start >= text_len:
                break
        
        return chunks


legal_chunker = LegalChunker()
