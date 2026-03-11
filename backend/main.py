"""Legal AI Assistant for Indian Law - FastAPI Main Application."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import get_settings
from backend.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    print("🏛️ Legal AI Assistant for Indian Law - Starting up...")
    
    # Create upload directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    
    # Initialize database
    await init_db()
    print("✅ Database initialized.")
    
    # Seed data on first run
    from backend.storage.vector_store import vector_store
    stats = vector_store.get_collection_stats()
    if stats["total_documents"] == 0:
        print("📚 First run detected - seeding legal database...")
        from backend.data.seed_laws import seed_all_laws
        from backend.data.seed_cases import seed_landmark_cases
        seed_all_laws()
        seed_landmark_cases()
        print("✅ Legal database seeded with Indian laws and landmark cases!")
    else:
        print(f"📊 Vector store has {stats['total_documents']} documents.")

    # Start Live Law Monitor (hourly background scheduler)
    try:
        from backend.crawler.law_monitor import start_scheduler
        scheduler = start_scheduler()
        app.state.scheduler = scheduler
        print("✅ Live Law Monitor started (checks IndiaCode every hour for new laws/amendments).")
    except Exception as e:
        print(f"⚠️  Law Monitor could not start: {e}")
        
    # Seed Mock Users
    from backend.database import async_session
    from backend.models.user import User, UserRole
    from backend.routers.auth import pwd_context
    from sqlalchemy import select
    
    async with async_session() as db:
        for mock_user in [
            {
                "email": "judge@india.gov.in", 
                "username": "judge", 
                "full_name": "Honorable Judge", 
                "role": UserRole.JUDGE.value, 
                "court_name": "Supreme Court of India"
            },
            {
                "email": "lawyer@india.gov.in", 
                "username": "lawyer", 
                "full_name": "Advocate Sharma", 
                "role": UserRole.LAWYER.value, 
                "bar_council_id": "D/123/2026",
                "specialization": "Criminal Defense, Cyber Crime",
                "about": "Advocate Sharma is a seasoned criminal defense lawyer with over 15 years of experience practicing in the High Courts and Supreme Court of India. He specializes in white-collar crimes and cyber law."
            }
        ]:
            existing = await db.execute(select(User).where(User.email == mock_user["email"]))
            if not existing.scalar_one_or_none():
                user = User(
                    email=mock_user["email"],
                    username=mock_user["username"],
                    full_name=mock_user["full_name"],
                    hashed_password=pwd_context.hash("1234"),
                    role=mock_user["role"],
                    bar_council_id=mock_user.get("bar_council_id"),
                    court_name=mock_user.get("court_name"),
                    specialization=mock_user.get("specialization"),
                    about=mock_user.get("about")
                )
                db.add(user)
                await db.commit()
                print(f"✅ Seeded mock user: {mock_user['email']} (Password: 1234)")
                
        # Seed Mock Court Holidays
        from backend.models.calendar import CourtHoliday
        from datetime import date
        existing_holidays = await db.execute(select(CourtHoliday))
        if len(existing_holidays.scalars().all()) == 0:
            mock_holidays = [
                CourtHoliday(holiday_date=date(2026, 3, 3), description="Maha Shivaratri", is_working_day=False),
                CourtHoliday(holiday_date=date(2026, 3, 14), description="Second Saturday", is_working_day=False),
                CourtHoliday(holiday_date=date(2026, 3, 24), description="Holi", is_working_day=False),
                CourtHoliday(holiday_date=date(2026, 3, 28), description="Fourth Saturday", is_working_day=False),
                CourtHoliday(holiday_date=date(2026, 4, 3), description="Good Friday", is_working_day=False),
                CourtHoliday(holiday_date=date(2026, 4, 11), description="Second Saturday", is_working_day=False),
                CourtHoliday(holiday_date=date(2026, 4, 14), description="Dr. B.R. Ambedkar's Birthday", is_working_day=False),
                CourtHoliday(holiday_date=date(2026, 4, 25), description="Fourth Saturday", is_working_day=False),
            ]
            db.add_all(mock_holidays)
            await db.commit()
            print("✅ Seeded mock court holidays for 2026.")
            
        # Seed Mock Domain Data (Cases, Chats)
        from backend.data.seed_mock_data import seed_mock_domain_data
        await seed_mock_domain_data(db)
    
    # Check Ollama
    from backend.ai.llm_client import llm_client
    if await llm_client.is_available():
        models = await llm_client.list_models()
        print(f"🤖 Ollama connected. Available models: {models}")
    else:
        print("⚠️ Ollama not available. Start with: ollama serve")
    
    yield
    
    print("👋 Legal AI Assistant shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered legal assistant for Indian law - helps judges, lawyers, and citizens understand statutes, case histories, and legal reasoning.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
from backend.routers import auth, chat, cases, documents, search, crawler, calendar

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(cases.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(crawler.router)
app.include_router(calendar.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from backend.storage.vector_store import vector_store
    from backend.storage.knowledge_graph import knowledge_graph
    from backend.ai.llm_client import llm_client
    
    vs_stats = vector_store.get_collection_stats()
    kg_stats = knowledge_graph.get_graph_stats()
    ollama_ok = await llm_client.is_available()
    
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ollama_connected": ollama_ok,
        "ollama_model": settings.OLLAMA_MODEL,
        "vector_store": vs_stats,
        "knowledge_graph": kg_stats,
    }


@app.get("/api/models")
async def list_models():
    """List available Ollama models."""
    from backend.ai.llm_client import llm_client
    models = await llm_client.list_models()
    return {"models": models, "current": settings.OLLAMA_MODEL}
