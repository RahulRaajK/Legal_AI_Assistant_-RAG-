"""Chat router - AI legal assistant conversations."""
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.user import User
from backend.models.document import ChatSession, ChatMessage
from backend.routers.auth import get_current_user
from backend.ai.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context_mode: str = "general"  # general, case_specific, document_qa
    case_id: Optional[str] = None
    user_role: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    message: str
    sources: list = []
    intents: list = []
    agent_results: list = []


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Send a message to the legal AI assistant."""
    user_role = request.user_role or (current_user.role if current_user else "citizen")
    
    # Get or create session
    session = None
    if request.session_id:
        result = await db.execute(
            select(ChatSession).where(ChatSession.id == request.session_id)
        )
        session = result.scalar_one_or_none()
    
    if not session:
        session = ChatSession(
            user_id=current_user.id if current_user else "anonymous",
            title=request.message[:50],
            context_mode=request.context_mode,
            case_id=request.case_id,
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
    
    # Save user message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    
    # Process through multi-agent orchestrator
    result = await orchestrator.process_query(
        query=request.message,
        user_role=user_role,
        case_context=None,
    )
    
    # Build response text from agent results
    response_text = ""
    sources = []
    agent_results_summary = []
    
    for agent_result in result.get("results", []):
        agent_name = agent_result.get("agent", "unknown")
        
        if "response" in agent_result:
            response_text += agent_result["response"] + "\n\n"
        elif "analysis" in agent_result:
            response_text += agent_result["analysis"] + "\n\n"
        elif "arguments" in agent_result:
            response_text += agent_result["arguments"] + "\n\n"
        elif "cases" in agent_result:
            response_text += "## Related Cases Found\n\n"
            for case in agent_result["cases"]:
                response_text += f"- **{case['title']}** ({case.get('year', 'N/A')}) - {case.get('court', '')}\n"
                response_text += f"  {case.get('summary', '')[:200]}...\n\n"
        
        if "sources" in agent_result:
            sources.extend(agent_result["sources"])
        
        agent_results_summary.append({
            "agent": agent_name,
            "has_response": bool(agent_result.get("response") or agent_result.get("analysis")),
        })
    
    if not response_text:
        response_text = "I apologize, but I couldn't find relevant legal information for your query. Please try rephrasing or provide more specific details."
    
    # Save assistant message
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_text.strip(),
        relevant_acts=json.dumps(sources[:5]) if sources else None,
    )
    db.add(assistant_msg)
    await db.commit()
    
    return ChatResponse(
        session_id=session.id,
        message=response_text.strip(),
        sources=sources[:10],
        intents=result.get("intents", []),
        agent_results=agent_results_summary,
    )


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """List chat sessions for the current user."""
    user_id = current_user.id if current_user else "anonymous"
    result = await db.execute(
        select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "context_mode": s.context_mode,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in sessions
    ]


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get all messages in a chat session."""
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    )
    messages = result.scalars().all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in messages
    ]
