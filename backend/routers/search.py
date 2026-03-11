"""Search router - semantic, statute, citation, and case similarity search."""
from typing import Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel
from backend.ai.rag_pipeline import rag_pipeline
from backend.storage.vector_store import vector_store
from backend.storage.knowledge_graph import knowledge_graph

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("/semantic")
async def semantic_search(
    q: str = Query(..., description="Search query"),
    n: int = Query(10, description="Number of results"),
    content_type: Optional[str] = Query(None, description="Filter by: statute, judgment, article"),
):
    """Semantic search across all legal documents."""
    results = await rag_pipeline.semantic_search(q, n_results=n, content_type=content_type)
    return {"query": q, "results": results, "total": len(results)}


@router.get("/statutes")
async def search_statutes(
    q: str = Query(..., description="Search query for statutes"),
    n: int = Query(10, description="Number of results"),
):
    """Search specifically for statutes and acts."""
    results = await rag_pipeline.semantic_search(q, n_results=n, content_type="statute")
    return {"query": q, "results": results, "total": len(results)}


@router.get("/cases")
async def search_cases(
    q: str = Query(..., description="Search query for cases"),
    n: int = Query(10, description="Number of results"),
):
    """Search specifically for court judgments."""
    results = await rag_pipeline.semantic_search(q, n_results=n, content_type="judgment")
    return {"query": q, "results": results, "total": len(results)}


@router.get("/graph")
async def search_knowledge_graph(
    q: str = Query(..., description="Search query"),
    node_type: Optional[str] = Query(None, description="Filter by: act, section, case, judge"),
    limit: int = Query(20, description="Number of results"),
):
    """Search the legal knowledge graph."""
    results = knowledge_graph.search_nodes(q, node_type=node_type, limit=limit)
    return {"query": q, "results": results, "total": len(results)}


@router.get("/graph/sections/{act_id}")
async def get_act_sections(act_id: str):
    """Get all sections of a specific act from the knowledge graph."""
    sections = knowledge_graph.get_sections_of_act(act_id)
    return {"act_id": act_id, "sections": sections, "total": len(sections)}


@router.get("/graph/cases-citing/{section_id}")
async def get_cases_citing_section(section_id: str):
    """Get all cases that cite a specific section."""
    cases = knowledge_graph.get_cases_citing_section(section_id)
    return {"section_id": section_id, "cases": cases, "total": len(cases)}


@router.get("/stats")
async def get_search_stats():
    """Get vector store and knowledge graph statistics."""
    vs_stats = vector_store.get_collection_stats()
    kg_stats = knowledge_graph.get_graph_stats()
    return {
        "vector_store": vs_stats,
        "knowledge_graph": kg_stats,
    }
