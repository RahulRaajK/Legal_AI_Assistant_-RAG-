"""Case management router."""
import json
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.user import User, UserRole
from backend.models.case import Case
from backend.routers.auth import get_current_user
from backend.ai.agents.prediction_agent import prediction_agent
from backend.ai.agents.argument_agent import argument_agent
from backend.ingestion.document_parser import document_parser
import os

router = APIRouter(prefix="/api/cases", tags=["Cases"])


class CaseCreate(BaseModel):
    case_title: str
    case_number: Optional[str] = None
    fir_number: Optional[str] = None
    case_code: Optional[str] = None
    case_type: Optional[str] = None
    act: Optional[str] = None
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    advocate_name: Optional[str] = None
    court_name: Optional[str] = None
    registration_number: Optional[str] = None
    judge_name: Optional[str] = None
    
    # Text logs (stored as JSON strings)
    petitioner_witnesses: Optional[str] = "[]"
    respondent_witnesses: Optional[str] = "[]"
    case_history: Optional[str] = "[]"
    process_details: Optional[str] = "[]"
    final_orders: Optional[str] = "[]"
    
    description: Optional[str] = None
    facts: Optional[str] = None
    status: str = "active"
    priority: str = "medium"
    filing_date: Optional[str] = None
    next_hearing_date: Optional[str] = None

class CaseUpdate(BaseModel):
    case_title: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    facts: Optional[str] = None
    next_hearing_date: Optional[str] = None
    hearing_time: Optional[str] = None
    judge_name: Optional[str] = None
    petitioner_attendance: Optional[str] = None
    respondent_attendance: Optional[str] = None
    
    # Appending logs through updates
    petitioner_witnesses: Optional[str] = None
    respondent_witnesses: Optional[str] = None
    case_history: Optional[str] = None
    process_details: Optional[str] = None
    final_orders: Optional[str] = None


@router.post("/")
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Create a new case."""
    case = Case(
        user_id=current_user.id if current_user else "anonymous",
        case_title=case_data.case_title,
        case_number=case_data.case_number,
        fir_number=case_data.fir_number,
        case_code=case_data.case_code,
        case_type=case_data.case_type,
        act=case_data.act,
        petitioner=case_data.petitioner,
        respondent=case_data.respondent,
        advocate_name=case_data.advocate_name,
        court_name=case_data.court_name,
        registration_number=case_data.registration_number,
        judge_name=case_data.judge_name,
        
        petitioner_witnesses=case_data.petitioner_witnesses,
        respondent_witnesses=case_data.respondent_witnesses,
        case_history=case_data.case_history,
        process_details=case_data.process_details,
        final_orders=case_data.final_orders,
        
        description=case_data.description,
        facts=case_data.facts,
        status=case_data.status,
        priority=case_data.priority,
        filing_date=datetime.fromisoformat(case_data.filing_date) if case_data.filing_date else None,
        next_hearing_date=datetime.fromisoformat(case_data.next_hearing_date) if case_data.next_hearing_date else None,
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    return {"id": case.id, "case_title": case.case_title, "status": case.status}


@router.get("/")
async def list_cases(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """List all cases with strict data isolation."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    query = select(Case)
    
    # Enforce Role-Based Data Isolation
    if current_user.role == UserRole.CITIZEN.value:
        query = query.where(Case.user_id == current_user.id)
    elif current_user.role == UserRole.LAWYER.value:
        query = query.where((Case.user_id == current_user.id) | (Case.advocate_name == current_user.full_name))
    elif current_user.role == UserRole.JUDGE.value:
        query = query.where((Case.court_name == current_user.court_name) | (Case.judge_name == current_user.full_name))

    if status:
        query = query.where(Case.status == status)
    query = query.order_by(Case.next_hearing_date.asc().nulls_last()) # Prioritize upcoming hearings
    
    result = await db.execute(query)
    cases = result.scalars().all()
    return [
        {
            "id": c.id,
            "case_title": c.case_title,
            "case_number": c.case_number,
            "fir_number": c.fir_number,
            "case_type": c.case_type,
            "petitioner": c.petitioner,
            "respondent": c.respondent,
            "court_name": c.court_name,
            "status": c.status,
            "priority": c.priority,
            "win_probability": c.win_probability,
            "next_hearing_date": c.next_hearing_date.isoformat() if c.next_hearing_date else None,
            "hearing_time": c.hearing_time,
            "created_at": c.created_at.isoformat(),
        }
        for c in cases
    ]


@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db)):
    """Get case details."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return {
        "id": case.id,
        "case_title": case.case_title,
        "case_number": case.case_number,
        "fir_number": case.fir_number,
        "case_code": case.case_code,
        "case_type": case.case_type,
        "act": case.act,
        "petitioner": case.petitioner,
        "respondent": case.respondent,
        "advocate_name": case.advocate_name,
        "court_name": case.court_name,
        "registration_number": case.registration_number,
        "judge_name": case.judge_name,
        
        "petitioner_witnesses": json.loads(case.petitioner_witnesses) if case.petitioner_witnesses else [],
        "respondent_witnesses": json.loads(case.respondent_witnesses) if case.respondent_witnesses else [],
        "case_history": json.loads(case.case_history) if case.case_history else [],
        "process_details": json.loads(case.process_details) if case.process_details else [],
        "final_orders": json.loads(case.final_orders) if case.final_orders else [],
        
        "description": case.description,
        "facts": case.facts,
        "status": case.status,
        "priority": case.priority,
        "ai_summary": case.ai_summary,
        "win_probability": case.win_probability,
        "ai_arguments": json.loads(case.ai_arguments) if case.ai_arguments else None,
        "relevant_acts": json.loads(case.relevant_acts) if case.relevant_acts else None,
        "relevant_precedents": json.loads(case.relevant_precedents) if case.relevant_precedents else None,
        "filing_date": case.filing_date.isoformat() if case.filing_date else None,
        "next_hearing_date": case.next_hearing_date.isoformat() if case.next_hearing_date else None,
        "documents": [
            {
                "id": d.id, 
                "filename": d.filename, 
                "document_type": d.document_type, 
                "submitted_by": d.submitted_by,
                "is_processed": d.is_processed,
                "admissibility_status": d.admissibility_status
            }
            for d in case.documents
        ],
        "created_at": case.created_at.isoformat(),
    }


@router.put("/{case_id}")
async def update_case(case_id: str, update: CaseUpdate, db: AsyncSession = Depends(get_db)):
    """Update a case."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    for field, value in update.model_dump(exclude_unset=True).items():
        if value is not None:
            if field == "next_hearing_date":
                value = datetime.fromisoformat(value)
            setattr(case, field, value)
    
    await db.commit()
    return {"status": "updated", "id": case_id}


@router.post("/{case_id}/analyze")
async def analyze_case(case_id: str, db: AsyncSession = Depends(get_db)):
    """Run AI analysis on a case (win probability, arguments, etc)."""
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Extract text from all attached documents
    petitioner_evidence = []
    respondent_evidence = []
    
    for doc in case.documents:
        if os.path.exists(doc.file_path):
            parsed = document_parser.parse_file(doc.file_path)
            text = parsed.get("text", "")
            if len(text) > 100:  # Valid text
                # Truncate to avoid exploding context windows
                preview = text[:5000] + ("..." if len(text) > 5000 else "")
                formatted_doc = f"Document '{doc.filename}':\n{preview}"
                
                if doc.submitted_by == "petitioner":
                    petitioner_evidence.append(formatted_doc)
                elif doc.submitted_by == "respondent":
                    respondent_evidence.append(formatted_doc)
                else:
                    # Neutral or court docs go to both for context
                    petitioner_evidence.append(formatted_doc)
                    respondent_evidence.append(formatted_doc)
    
    # Build a massive context payload for DeepSeek
    pet_ev_str = "\n\n".join(petitioner_evidence) if petitioner_evidence else "No petitioner documents uploaded."
    res_ev_str = "\n\n".join(respondent_evidence) if respondent_evidence else "No respondent documents uploaded."
    
    case_details = f"""
    Title: {case.case_title}
    Type: {case.case_type or 'Not specified'}
    Petitioner: {case.petitioner or 'Not specified'}
    Respondent: {case.respondent or 'Not specified'}
    Facts: {case.facts or case.description or 'No facts provided'}
    
    === EVIDENCE SUBMITTED BY PETITIONER ===
    {pet_ev_str}
    
    === EVIDENCE SUBMITTED BY RESPONDENT ===
    {res_ev_str}
    """
    
    # Run prediction
    prediction = await prediction_agent.predict(case_details)
    
    # Generate arguments for both sides
    pet_args = await argument_agent.generate_arguments(case_details, "petitioner")
    res_args = await argument_agent.generate_arguments(case_details, "respondent")
    
    # Update case with AI analysis
    case.ai_summary = prediction.get("analysis", "")
    case.ai_arguments = json.dumps({
        "petitioner": pet_args.get("arguments", ""),
        "respondent": res_args.get("arguments", ""),
    })
    
    await db.commit()
    
    return {
        "case_id": case_id,
        "prediction": prediction,
        "petitioner_arguments": pet_args,
        "respondent_arguments": res_args,
    }
