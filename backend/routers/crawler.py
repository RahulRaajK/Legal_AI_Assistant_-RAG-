"""Crawler management router."""
from typing import Optional
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from backend.crawler.indiacode_crawler import indiacode_crawler
from backend.crawler.indiankanoon_crawler import indiankanoon_crawler
from backend.ingestion.pipeline import ingestion_pipeline

router = APIRouter(prefix="/api/crawler", tags=["Crawler"])


class CrawlRequest(BaseModel):
    source: str = "indiankanoon"  # indiankanoon, indiacode
    query: str = ""
    max_results: int = 5


class CrawlURLRequest(BaseModel):
    url: str
    source: str = "indiankanoon"


@router.post("/search")
async def crawl_search(request: CrawlRequest):
    """Search and retrieve results from legal sources."""
    results = []

    if request.source == "indiankanoon":
        results = indiankanoon_crawler.search_cases(request.query, max_results=request.max_results)
    elif request.source == "indiacode":
        results = indiacode_crawler.search_acts(request.query, max_results=request.max_results)

    return {"source": request.source, "query": request.query, "results": results}


@router.post("/fetch-and-ingest")
async def fetch_and_ingest(request: CrawlURLRequest, background_tasks: BackgroundTasks):
    """Fetch a page and ingest it into the vector store."""

    async def _fetch_and_ingest():
        if request.source == "indiankanoon":
            data = indiankanoon_crawler.fetch_judgment(request.url)
        elif request.source == "indiacode":
            data = indiacode_crawler.fetch_act_content(request.url)
        else:
            return

        if data and data.get("content"):
            metadata = {
                "act_name": data.get("title", ""),
                "content_type": data.get("content_type", "statute"),
                "source_name": request.source,
                "source_url": request.url,
                "court": data.get("court", ""),
                "judge": data.get("judge", ""),
                "year": str(data.get("year", "")),
            }
            await ingestion_pipeline.ingest_text(data["content"], metadata)

    background_tasks.add_task(_fetch_and_ingest)
    return {"status": "queued", "url": request.url}


@router.get("/law-updates")
async def get_law_updates(limit: int = 20):
    """Get recently ingested/detected legal updates."""
    try:
        from backend.crawler.law_monitor import get_recent_updates
        updates = get_recent_updates(limit=limit)
        return {"status": "ok", "updates": updates, "count": len(updates)}
    except Exception as e:
        return {"status": "error", "updates": [], "count": 0, "error": str(e)}


@router.get("/monitor-status")
async def monitor_status():
    """Get the live law monitor status."""
    try:
        from backend.crawler.law_monitor import get_monitor_status
        return get_monitor_status()
    except Exception as e:
        return {"error": str(e), "is_running": False}


@router.post("/monitor-run-now")
async def trigger_monitor_now(background_tasks: BackgroundTasks):
    """Manually trigger an immediate law monitor check."""
    async def _run():
        from backend.crawler.law_monitor import run_monitor_check
        await run_monitor_check()

    background_tasks.add_task(_run)
    return {"status": "Monitor check triggered in background."}


@router.get("/corpus-stats")
async def corpus_stats():
    """Get current vector store and catalog statistics."""
    from backend.storage.vector_store import vector_store
    vs_stats = vector_store.get_collection_stats()
    total = vs_stats.get("total_documents", 0)

    return {
        "vector_store": vs_stats,
        "crawler_catalog": {},
        "total_cataloged": total,
        "total_embedded": total,
        "total_failed": 0,
        "total_pending": 0,
    }


@router.get("/status")
async def crawler_status():
    """Get crawler and monitor status (delegates to /monitor-status)."""
    try:
        from backend.crawler.law_monitor import get_monitor_status
        return {"law_monitor": get_monitor_status()}
    except Exception as e:
        return {"law_monitor": {"error": str(e)}}
