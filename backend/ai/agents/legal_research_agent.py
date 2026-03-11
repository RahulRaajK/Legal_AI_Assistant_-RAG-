"""Legal Research Agent - searches statutes and acts."""
from backend.ai.llm_client import llm_client
from backend.ai.prompts import SYSTEM_PROMPT, LAW_SUMMARIZATION_PROMPT
from backend.storage.vector_store import vector_store
from backend.storage.knowledge_graph import knowledge_graph


class LegalResearchAgent:
    """Agent specialized in statute lookup and legal summarization."""
    
    async def research(self, query: str, n_results: int = 5) -> dict:
        """Search for relevant statutes and provide summary."""
        # Search vector store for relevant legal text
        results = vector_store.search(
            query_text=query,
            n_results=n_results,
            metadata_filter={"content_type": "statute"},
        )
        
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        
        context = "\n\n".join([
            f"[{m.get('act_name', 'Unknown')} - Section {m.get('section_number', 'N/A')}]\n{d}"
            for d, m in zip(docs, metas)
        ]) if docs else "No statutes found in the database for this query."
        
        # Search knowledge graph
        graph_results = knowledge_graph.search_nodes(query, node_type="act")
        graph_context = ""
        if graph_results:
            graph_context = "\n\nKnowledge Graph Results:\n" + "\n".join([
                f"- {r.get('name', r['id'])} ({r.get('year', 'N/A')})" for r in graph_results[:5]
            ])
        
        prompt = LAW_SUMMARIZATION_PROMPT.format(
            context=context + graph_context,
            query=query,
            title=query[:80],
        )
        
        response = await llm_client.generate(prompt, system_prompt=SYSTEM_PROMPT)
        
        return {
            "agent": "legal_research",
            "response": response,
            "sources": [
                {"act_name": m.get("act_name", ""), "section": m.get("section_number", "")}
                for m in metas
            ],
            "graph_matches": graph_results[:5],
        }


legal_research_agent = LegalResearchAgent()
