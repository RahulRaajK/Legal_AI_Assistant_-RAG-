"""Evidence Analysis Agent - analyzes uploaded documents via RAG."""
from backend.ai.llm_client import llm_client
from backend.ai.prompts import SYSTEM_PROMPT, DOCUMENT_QA_PROMPT


class EvidenceAgent:
    """Agent specialized in analyzing uploaded legal documents."""
    
    async def analyze_document(self, document_text: str, question: str = None) -> dict:
        """Analyze an uploaded legal document."""
        if not question:
            question = "Provide a comprehensive analysis of this legal document, including key parties, legal issues, important clauses, and potential concerns."
        
        prompt = DOCUMENT_QA_PROMPT.format(
            context=document_text[:6000],
            query=question,
        )
        
        response = await llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        return {
            "agent": "evidence_analysis",
            "analysis": response,
            "document_length": len(document_text),
        }
    
    async def extract_key_facts(self, document_text: str) -> dict:
        """Extract key facts from a legal document (FIR, petition, complaint)."""
        prompt = f"""Extract all key facts from this legal document in a structured format.

DOCUMENT:
{document_text[:6000]}

Provide:
## Key Facts Extracted

### Parties Involved
- Names, roles, addresses

### Important Dates
- List all dates mentioned with their significance

### Key Events
- Chronological list of events

### Legal Issues
- What legal questions arise

### Evidence Mentioned
- Documents, witnesses, physical evidence referenced

### Relief/Remedy Sought
- What is being requested
"""
        
        response = await llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        return {
            "agent": "evidence_analysis",
            "facts": response,
            "document_length": len(document_text),
        }


evidence_agent = EvidenceAgent()
