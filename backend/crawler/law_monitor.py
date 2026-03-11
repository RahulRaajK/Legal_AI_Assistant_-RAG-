"""
Live Law Monitor — APScheduler-based background service.
Polls IndiaCode every hour for new acts and constitutional amendments.
Auto-ingests changed content into the FAISS vector store.
"""
import asyncio
import logging
import aiohttp
from datetime import datetime
from typing import List, Dict

logger = logging.getLogger(__name__)

# ─── Global state for monitoring results ─────────────────────────────────────
_monitor_state = {
    "last_run": None,
    "next_run": None,
    "is_running": False,
    "total_checks": 0,
    "total_new_laws": 0,
    "recent_updates": [],   # last 20 newly detected laws
}

INDIACODE_BASE = "https://www.indiacode.nic.in"
RECENT_ACTS_URL = f"{INDIACODE_BASE}/handle/123456789/1362/browse?type=dateissued&sort_by=2&order=DESC&rpp=20&offset=0"
RECENT_AMENDMENTS_URL = f"{INDIACODE_BASE}/handle/123456789/1362/browse?type=actno&sort_by=2&order=DESC&rpp=20&offset=0"


async def _fetch_recent_acts(session: aiohttp.ClientSession) -> List[Dict]:
    """Fetch the latest acts from IndiaCode What's New section."""
    from bs4 import BeautifulSoup

    headers = {"User-Agent": "Mozilla/5.0 LegalAI Monitor/1.0"}
    results = []
    for url in [RECENT_ACTS_URL]:
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    for link in soup.select(".artifact-title a")[:20]:
                        href = link.get("href", "")
                        title = link.get_text(strip=True)
                        if href and title:
                            results.append({
                                "title": title,
                                "url": f"{INDIACODE_BASE}{href}" if href.startswith("/") else href,
                                "detected_at": datetime.now().isoformat(),
                                "source": "indiacode",
                                "type": "act"
                            })
        except Exception as e:
            logger.warning(f"Monitor fetch failed: {e}")
    return results


async def run_monitor_check():
    """Core monitoring job — detects new/changed laws and re-ingests them."""
    if _monitor_state["is_running"]:
        logger.info("Monitor already running, skipping this cycle.")
        return

    _monitor_state["is_running"] = True
    _monitor_state["last_run"] = datetime.now().isoformat()
    _monitor_state["total_checks"] += 1
    logger.info(f"🔍 Law Monitor Check #{_monitor_state['total_checks']} started...")

    new_laws = []
    try:
        from backend.crawler.bulk_extract import BulkCrawlerManager, compute_hash, process_document
        manager = BulkCrawlerManager()

        connector = aiohttp.TCPConnector(limit=5)
        async with aiohttp.ClientSession(connector=connector) as session:
            # Fetch recently published acts
            recent = await _fetch_recent_acts(session)

            for item in recent:
                # Check if this URL is new or content has changed
                if manager.is_content_changed(item["url"], ""):
                    manager.add_target(item["url"], item["title"], item["source"], item["type"])
                    # Process it immediately
                    doc = {"url": item["url"], "title": item["title"],
                           "source": item["source"], "content_type": item["type"]}
                    await process_document(session, manager, doc)
                    new_laws.append(item)
                    logger.info(f"  ✅ New law ingested: {item['title']}")

        # Flush vector store to disk
        from backend.storage.vector_store import vector_store
        vector_store.flush()

    except Exception as e:
        logger.error(f"Monitor error: {e}")
    finally:
        _monitor_state["is_running"] = False
        _monitor_state["total_new_laws"] += len(new_laws)
        if new_laws:
            _monitor_state["recent_updates"] = (new_laws + _monitor_state["recent_updates"])[:20]

    logger.info(f"✅ Monitor check complete. Found {len(new_laws)} new/updated laws.")
    return new_laws


def get_monitor_status() -> Dict:
    """Return the current monitoring state (for the API endpoint)."""
    return {
        "last_run": _monitor_state["last_run"],
        "next_run": _monitor_state["next_run"],
        "is_running": _monitor_state["is_running"],
        "total_checks": _monitor_state["total_checks"],
        "total_new_laws_detected": _monitor_state["total_new_laws"],
        "recent_updates": _monitor_state["recent_updates"],
    }


def get_recent_updates(limit: int = 20) -> List[Dict]:
    """Return the most recently detected law updates."""
    from backend.crawler.bulk_extract import BulkCrawlerManager
    manager = BulkCrawlerManager()
    return manager.get_recently_updated(limit)


def start_scheduler():
    """Start the APScheduler background scheduler to run every hour."""
    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            run_monitor_check,
            trigger="interval",
            hours=1,
            id="law_monitor",
            name="Indian Law Amendment Monitor",
            replace_existing=True,
            next_run_time=datetime.now(),  # Run immediately on startup too
        )
        scheduler.start()
        _monitor_state["next_run"] = "Hourly"
        logger.info("✅ Law Monitor Scheduler started (runs every hour).")
        return scheduler
    except ImportError:
        logger.warning("APScheduler not installed. Law monitor disabled. Run: pip install apscheduler")
        return None
    except Exception as e:
        logger.error(f"Scheduler start failed: {e}")
        return None
