"""Prediction Agent - estimates case win probability."""
from backend.ai.llm_client import llm_client
from backend.ai.prompts import SYSTEM_PROMPT, WIN_PROBABILITY_PROMPT
from backend.storage.vector_store import vector_store


class PredictionAgent:
    """Agent specialized in estimating case success probability."""
    
    async def predict(self, case_details: str, n_results: int = 5) -> dict:
        """Analyze case and estimate win probability."""
        # Retrieve relevant laws
        statute_results = vector_store.search(
            query_text=case_details,
            n_results=3,
            metadata_filter={"content_type": "statute"},
        )
        
        # Retrieve similar cases  
        case_results = vector_store.search(
            query_text=case_details,
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
        
        precedent_context = "\n\n".join([
            f"[{m.get('act_name', 'Case')} ({m.get('year', '')}) - Outcome: {m.get('case_type', 'N/A')}]\n{d[:400]}"
            for d, m in zip(
                case_results.get("documents", [[]])[0],
                case_results.get("metadatas", [[]])[0],
            )
        ]) if case_results.get("documents", [[]])[0] else "No precedent cases found."
        
        prompt = WIN_PROBABILITY_PROMPT.format(
            case_details=case_details,
            context=statute_context,
            precedents=precedent_context,
        )
        
        response = await llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        return {
            "agent": "prediction",
            "analysis": response,
            "similar_cases_analyzed": len(case_results.get("documents", [[]])[0]),
        }


prediction_agent = PredictionAgent()
