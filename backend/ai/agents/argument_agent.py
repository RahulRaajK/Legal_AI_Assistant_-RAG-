"""Argument Builder Agent - generates legal arguments with supporting precedents."""
from backend.ai.llm_client import llm_client
from backend.ai.prompts import SYSTEM_PROMPT, ARGUMENT_GENERATION_PROMPT
from backend.storage.vector_store import vector_store


class ArgumentAgent:
    """Agent specialized in generating legal arguments."""
    
    async def generate_arguments(
        self,
        case_details: str,
        side: str = "petitioner",
        n_results: int = 5,
    ) -> dict:
        """Generate legal arguments for a specified side."""
        # Retrieve relevant laws
        statute_results = vector_store.search(
            query_text=case_details,
            n_results=n_results,
            metadata_filter={"content_type": "statute"},
        )
        
        # Retrieve precedents
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
            f"[{m.get('act_name', 'Case')} ({m.get('year', '')})]\n{d[:300]}"
            for d, m in zip(
                case_results.get("documents", [[]])[0],
                case_results.get("metadatas", [[]])[0],
            )
        ]) if case_results.get("documents", [[]])[0] else "No precedent cases found."
        
        prompt = ARGUMENT_GENERATION_PROMPT.format(
            side=side.capitalize(),
            case_details=case_details,
            context=statute_context,
            precedents=precedent_context,
        )
        
        response = await llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        return {
            "agent": "argument_builder",
            "side": side,
            "arguments": response,
            "supporting_acts": [
                m.get("act_name", "") for m in statute_results.get("metadatas", [[]])[0]
            ],
            "supporting_precedents": [
                m.get("act_name", "") for m in case_results.get("metadatas", [[]])[0]
            ],
        }


argument_agent = ArgumentAgent()
