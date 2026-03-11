"""Multi-Agent Orchestrator - routes queries to appropriate agents."""
from typing import Optional
from backend.ai.agents.legal_research_agent import legal_research_agent
from backend.ai.agents.case_law_agent import case_law_agent
from backend.ai.agents.evidence_agent import evidence_agent
from backend.ai.agents.argument_agent import argument_agent
from backend.ai.agents.prediction_agent import prediction_agent
from backend.ai.rag_pipeline import rag_pipeline
from backend.ai.llm_client import llm_client


class AgentOrchestrator:
    """Routes user queries to the appropriate AI agent(s)."""
    
    INTENT_CLASSIFICATION_PROMPT = """Classify the user's legal query into one or more categories.

USER QUERY: {query}

Categories:
1. LAW_LOOKUP - User wants to understand a specific law, section, or article
2. CASE_SEARCH - User wants to find similar cases or case history
3. CASE_ANALYSIS - User wants analysis of a specific case
4. ARGUMENT_GENERATION - User wants legal arguments for a case
5. WIN_PROBABILITY - User wants to know chances of winning
6. DOCUMENT_ANALYSIS - User wants to analyze an uploaded document
7. GENERAL_LEGAL - General legal question or advice

Return ONLY the category names (comma-separated if multiple apply), nothing else.
Example: LAW_LOOKUP,CASE_SEARCH
"""
    
    async def classify_intent(self, query: str) -> list[str]:
        """Classify the user's query intent."""
        prompt = self.INTENT_CLASSIFICATION_PROMPT.format(query=query)
        response = await llm_client.generate(prompt, temperature=0.1)
        
        valid_intents = {
            "LAW_LOOKUP", "CASE_SEARCH", "CASE_ANALYSIS",
            "ARGUMENT_GENERATION", "WIN_PROBABILITY",
            "DOCUMENT_ANALYSIS", "GENERAL_LEGAL"
        }
        
        intents = [i.strip().upper() for i in response.strip().split(",")]
        intents = [i for i in intents if i in valid_intents]
        
        return intents if intents else ["GENERAL_LEGAL"]
    
    async def process_query(
        self,
        query: str,
        user_role: str = "citizen",
        case_context: Optional[str] = None,
        document_text: Optional[str] = None,
        auto_classify: bool = True,
    ) -> dict:
        """Process a legal query through the appropriate agent(s)."""
        
        # If document text is provided, route to evidence agent
        if document_text:
            result = await evidence_agent.analyze_document(document_text, query)
            return {
                "type": "document_analysis",
                "results": [result],
                "query": query,
            }
        
        # Classify intent
        if auto_classify:
            intents = await self.classify_intent(query)
        else:
            intents = ["GENERAL_LEGAL"]
        
        results = []
        
        for intent in intents[:3]:  # Limit to 3 agents max
            if intent == "LAW_LOOKUP":
                result = await legal_research_agent.research(query)
                results.append(result)
            
            elif intent == "CASE_SEARCH":
                result = await case_law_agent.find_similar_cases(query)
                results.append(result)
            
            elif intent == "CASE_ANALYSIS":
                facts = case_context or query
                result = await case_law_agent.analyze_case(facts)
                results.append(result)
            
            elif intent == "ARGUMENT_GENERATION":
                details = case_context or query
                petitioner_args = await argument_agent.generate_arguments(details, "petitioner")
                respondent_args = await argument_agent.generate_arguments(details, "respondent")
                results.extend([petitioner_args, respondent_args])
            
            elif intent == "WIN_PROBABILITY":
                details = case_context or query
                result = await prediction_agent.predict(details)
                results.append(result)
            
            elif intent in ("GENERAL_LEGAL", "DOCUMENT_ANALYSIS"):
                result = await rag_pipeline.query(query, user_role=user_role, case_context=case_context)
                results.append({
                    "agent": "rag_pipeline",
                    "response": result["answer"],
                    "sources": result["sources"],
                })
        
        # If no results from classification, fall back to RAG
        if not results:
            result = await rag_pipeline.query(query, user_role=user_role, case_context=case_context)
            results.append({
                "agent": "rag_pipeline",
                "response": result["answer"],
                "sources": result["sources"],
            })
        
        return {
            "type": "multi_agent",
            "intents": intents,
            "results": results,
            "query": query,
        }


# Singleton
orchestrator = AgentOrchestrator()
