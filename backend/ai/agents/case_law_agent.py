"""Case Law Agent - retrieves and analyzes similar cases."""
from backend.ai.llm_client import llm_client
from backend.ai.prompts import SYSTEM_PROMPT, CASE_ANALYSIS_PROMPT
from backend.storage.vector_store import vector_store
from backend.storage.knowledge_graph import knowledge_graph


class CaseLawAgent:
    """Agent specialized in case law retrieval and analysis."""
    
    async def find_similar_cases(self, query: str, n_results: int = 5) -> dict:
        """Find cases similar to the described situation."""
        results = vector_store.search(
            query_text=query,
            n_results=n_results,
            metadata_filter={"content_type": "judgment"},
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        
        cases = []
        for doc, meta in zip(docs, metas):
            cases.append({
                "title": meta.get("act_name", "Unknown Case"),
                "court": meta.get("court", ""),
                "year": meta.get("year", ""),
                "judge": meta.get("judge", ""),
                "summary": doc[:300],
                "citation": meta.get("citation", ""),
            })
        
        return {
            "agent": "case_law",
            "cases": cases,
            "total_found": len(cases),
        }
    
    async def analyze_case(self, facts: str, n_results: int = 5) -> dict:
        """Analyze a case by finding precedents and providing legal analysis."""
        # Find relevant statutes
        statute_results = vector_store.search(
            query_text=facts,
            n_results=3,
            metadata_filter={"content_type": "statute"},
        )
        
        # Find relevant judgments
        case_results = vector_store.search(
            query_text=facts,
            n_results=n_results,
            metadata_filter={"content_type": "judgment"},
        )
        
        statute_context = "\n\n".join([
            f"[{m.get('act_name', '')} - Section {m.get('section_number', '')}]\n{d}"
            for d, m in zip(
                statute_results.get("documents", [[]])[0],
                statute_results.get("metadatas", [[]])[0],
            )
        ]) if statute_results.get("documents", [[]])[0] else "No specific statutes found."
        
        case_context = "\n\n".join([
            f"[{m.get('act_name', 'Case')} ({m.get('year', '')})]\n{d[:400]}"
            for d, m in zip(
                case_results.get("documents", [[]])[0],
                case_results.get("metadatas", [[]])[0],
            )
        ]) if case_results.get("documents", [[]])[0] else "No precedent cases found."
        
        prompt = CASE_ANALYSIS_PROMPT.format(
            facts=facts,
            context=statute_context,
            precedents=case_context,
        )
        
        response = await llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        return {
            "agent": "case_law",
            "analysis": response,
            "precedents": [
                {
                    "title": m.get("act_name", ""),
                    "year": m.get("year", ""),
                    "court": m.get("court", ""),
                }
                for m in case_results.get("metadatas", [[]])[0]
            ],
        }


case_law_agent = CaseLawAgent()
