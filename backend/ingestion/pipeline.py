"""Ingestion pipeline - parse, chunk, embed, store."""
import hashlib
import json
import logging
from datetime import datetime
from typing import Optional
from backend.ingestion.document_parser import document_parser
from backend.ingestion.chunker import legal_chunker
from backend.storage.vector_store import vector_store
from backend.storage.knowledge_graph import knowledge_graph
from backend.database import async_session
from backend.models.law_registry import LawRegistry

logger = logging.getLogger(__name__)


class IngestionPipeline:
    """Orchestrates the full ingestion: parse → chunk → embed → store."""
    
    def ingest_file(self, file_path: str, metadata: Optional[dict] = None) -> dict:
        """Ingest a file into the vector store."""
        metadata = metadata or {}
        
        # Step 1: Parse
        parsed = document_parser.parse_file(file_path)
        if not parsed.get("text"):
            return {"status": "error", "message": parsed.get("error", "No text extracted")}
        
        # Extract metadata from text
        auto_meta = document_parser.extract_metadata_from_text(parsed["text"])
        full_metadata = {**auto_meta, **metadata}
        
        # Step 2: Chunk
        chunks = legal_chunker.chunk_text(parsed["text"], full_metadata)
        
        if not chunks:
            return {"status": "error", "message": "No chunks generated"}
        
        # Step 3 & 4: Embed and Store
        return self._store_chunks(chunks)
    
    async def ingest_text(self, text: str, metadata: Optional[dict] = None) -> dict:
        """Ingest raw text into the vector store with law-registry aware dedup."""
        metadata = metadata or {}

        # Extract metadata
        auto_meta = document_parser.extract_metadata_from_text(text)
        full_metadata = {**auto_meta, **metadata}

        # Optional: law-aware registry handling (only when we have act/jurisdiction/year)
        try:
            act_name = full_metadata.get("act_name") or full_metadata.get("title")
            jurisdiction = full_metadata.get("jurisdiction", "central")
            year_raw = full_metadata.get("year")
            year = int(year_raw) if year_raw not in (None, "", "0") else None
            act_number = full_metadata.get("act_number")

            if act_name:
                normalized = " ".join(act_name.split()).lower()
                content_hash = hashlib.sha256(
                    " ".join(text.split()).lower().encode("utf-8")
                ).hexdigest()

                async with async_session() as session:
                    existing = None
                    try:
                        existing = (
                            await session.execute(
                                LawRegistry.__table__.select().where(
                                    LawRegistry.jurisdiction == jurisdiction,
                                    LawRegistry.act_number == act_number,
                                    LawRegistry.year == year,
                                )
                            )
                        ).first()
                    except Exception as e:
                        logger.warning(f"LawRegistry lookup failed: {e}")

                    # If we found an entry and hash is unchanged, skip heavy work
                    if existing and existing[0].content_hash == content_hash:
                        logger.info(
                            "Skipping ingestion; law content unchanged in LawRegistry."
                        )
                        return {
                            "status": "skipped",
                            "reason": "unchanged_law_content",
                        }

                    # Upsert registry entry
                    if existing:
                        law: LawRegistry = existing[0]
                        law.title = normalized
                        law.content_hash = content_hash
                        law.last_seen_at = datetime.utcnow()
                        law.last_ingested_at = datetime.utcnow()
                        # Merge URLs if provided
                        url = full_metadata.get("source_url")
                        urls = []
                        if law.source_urls:
                            try:
                                urls = json.loads(law.source_urls)
                            except Exception:
                                urls = []
                        if url and url not in urls:
                            urls.append(url)
                        law.source_urls = json.dumps(urls) if urls else law.source_urls
                    else:
                        url = full_metadata.get("source_url")
                        urls = [url] if url else []
                        law = LawRegistry(
                            title=normalized,
                            jurisdiction=jurisdiction,
                            act_number=act_number,
                            year=year,
                            source_primary=full_metadata.get("source_name"),
                            source_urls=json.dumps(urls) if urls else None,
                            last_seen_at=datetime.utcnow(),
                            last_ingested_at=datetime.utcnow(),
                            content_hash=content_hash,
                        )
                        session.add(law)

                    try:
                        await session.commit()
                    except Exception as e:
                        logger.warning(f"LawRegistry commit failed: {e}")
        except Exception as e:
            logger.warning(f"LawRegistry integration error during ingest_text: {e}")

        # Chunk
        chunks = legal_chunker.chunk_text(text, full_metadata)

        if not chunks:
            return {"status": "error", "message": "No chunks generated"}

        return self._store_chunks(chunks)
    
    def ingest_structured_law(
        self,
        act_name: str,
        sections: list[dict],
        year: int = None,
        content_type: str = "statute",
    ) -> dict:
        """Ingest structured legal data (act with sections)."""
        all_chunks = []
        
        # Add act to knowledge graph
        act_id = act_name.lower().replace(" ", "_")
        knowledge_graph.add_act(act_id, act_name, year=year)
        
        for section in sections:
            section_text = section.get("text", "")
            section_num = section.get("number", "")
            section_title = section.get("title", "")
            
            metadata = {
                "act_name": act_name,
                "section_number": str(section_num),
                "content_type": content_type,
                "source_name": "seed_data",
                "year": year or 0,
            }
            
            chunks = legal_chunker.chunk_text(section_text, metadata)
            all_chunks.extend(chunks)
            
            # Add to knowledge graph
            if section_num:
                section_id = f"{act_id}_s{section_num}"
                knowledge_graph.add_section(section_id, section_title, act_id, str(section_num))
        
        if not all_chunks:
            return {"status": "error", "message": "No chunks generated"}
        
        return self._store_chunks(all_chunks)
    
    def ingest_case(
        self,
        title: str,
        content: str,
        court: str = "",
        judge: str = "",
        year: int = None,
        citation: str = "",
        cited_sections: list[str] = None,
    ) -> dict:
        """Ingest a case judgment."""
        metadata = {
            "act_name": title,
            "content_type": "judgment",
            "court": court,
            "judge": judge,
            "year": year or 0,
            "citation": citation,
            "source_name": "seed_data",
        }
        
        chunks = legal_chunker.chunk_text(content, metadata)
        
        # Add to knowledge graph
        case_id = title.lower().replace(" ", "_")[:50]
        knowledge_graph.add_case(case_id, title, year=year, court=court)
        
        if judge:
            judge_id = judge.lower().replace(" ", "_")[:50]
            knowledge_graph.add_judge(judge_id, judge, court=court)
            knowledge_graph.add_judgment(case_id, judge_id)
        
        if cited_sections:
            for section in cited_sections:
                knowledge_graph.add_citation(case_id, section)
        
        if not chunks:
            return {"status": "error", "message": "No chunks generated"}
        
        return self._store_chunks(chunks)
    
    def _store_chunks(self, chunks: list[dict]) -> dict:
        """Store chunks in the vector store."""
        try:
            documents = [c["text"] for c in chunks]
            metadatas = []
            for c in chunks:
                meta = {k: str(v) if v is not None else "" for k, v in c["metadata"].items()}
                metadatas.append(meta)
            ids = [c["id"] for c in chunks]
            
            count = vector_store.add_documents(documents, metadatas, ids)
            
            return {
                "status": "success",
                "chunks_stored": count,
                "total_chunks": len(chunks),
            }
        except Exception as e:
            logger.error(f"Error storing chunks: {e}")
            return {"status": "error", "message": str(e)}


ingestion_pipeline = IngestionPipeline()
