"""Core RAG pipeline - Retrieval Augmented Generation for legal queries."""
import json
from typing import Optional
from backend.ai.llm_client import llm_client
from backend.ai.embeddings import embedding_engine
from backend.storage.vector_store import vector_store
from backend.ai.prompts import (
    SYSTEM_PROMPT,
    LAW_SUMMARIZATION_PROMPT,
    DOCUMENT_QA_PROMPT,
    CITIZEN_EXPLAIN_PROMPT,
    JUDGE_SUMMARY_PROMPT,
)


class RAGPipeline:
    """Retrieval Augmented Generation pipeline for Indian legal queries."""
    
    def __init__(self):
        self.llm = llm_client
        self.embeddings = embedding_engine
        self.vector_store = vector_store
    
    async def query(
        self,
        question: str,
        user_role: str = "citizen",
        n_results: int = 5,
        case_context: Optional[str] = None,
        metadata_filter: Optional[dict] = None,
    ) -> dict:
        """
        Full RAG pipeline:
        1. Embed the question
        2. Retrieve relevant chunks from ChromaDB
        3. Augment prompt with retrieved context
        4. Generate response via Ollama
        """
        # Step 1 & 2: Retrieve relevant documents
        results = self.vector_store.search(
            query_text=question,
            n_results=n_results,
            metadata_filter=metadata_filter,
        )
        
        # Step 3: Build context from retrieved documents
        context_parts = []
        sources = []
        for i, (doc, meta) in enumerate(zip(
            results.get("documents", [[]])[0],
            results.get("metadatas", [[]])[0],
        )):
            source_info = {
                "act_name": meta.get("act_name", "Unknown"),
                "section": meta.get("section_number", ""),
                "source": meta.get("source_name", ""),
                "content_type": meta.get("content_type", ""),
            }
            sources.append(source_info)
            context_parts.append(
                f"[Source {i+1}: {source_info['act_name']} "
                f"{'Section ' + source_info['section'] if source_info['section'] else ''}]\n{doc}"
            )
        
        context = "\n\n---\n\n".join(context_parts) if context_parts else "No specific legal context found in database."
        
        # Add case context if provided
        if case_context:
            context = f"CASE SPECIFIC CONTEXT:\n{case_context}\n\n---\n\nLEGAL DATABASE CONTEXT:\n{context}"
        
        # Step 4: Choose prompt template based on role
        if user_role == "citizen":
            prompt = CITIZEN_EXPLAIN_PROMPT.format(context=context, query=question)
        elif user_role == "judge":
            prompt = JUDGE_SUMMARY_PROMPT.format(
                case_details=case_context or question,
                context=context,
                precedents="See case references in context above."
            )
        else:
            prompt = LAW_SUMMARIZATION_PROMPT.format(
                context=context, query=question, title=question[:80]
            )
        
        # Step 5: Generate response
        response = await self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        return {
            "answer": response,
            "sources": sources,
            "query": question,
            "context_used": len(context_parts),
        }
    
    async def document_qa(self, question: str, document_text: str) -> dict:
        """Answer questions about uploaded documents."""
        prompt = DOCUMENT_QA_PROMPT.format(context=document_text[:4000], query=question)
        response = await self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)
        return {
            "answer": response,
            "query": question,
        }
    
    async def semantic_search(
        self,
        query: str,
        n_results: int = 10,
        content_type: Optional[str] = None,
    ) -> list[dict]:
        """Semantic search over the legal corpus."""
        metadata_filter = {}
        if content_type:
            metadata_filter["content_type"] = content_type
        
        results = self.vector_store.search(
            query_text=query,
            n_results=n_results,
            metadata_filter=metadata_filter if metadata_filter else None,
        )
        
        search_results = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        
        for doc, meta, dist in zip(docs, metas, distances):
            search_results.append({
                "content": doc[:500],
                "act_name": meta.get("act_name", ""),
                "section_number": meta.get("section_number", ""),
                "content_type": meta.get("content_type", ""),
                "source": meta.get("source_name", ""),
                "relevance_score": round(1 - dist, 4) if dist else 0,
            })
        
        return search_results


# Singleton
rag_pipeline = RAGPipeline()
