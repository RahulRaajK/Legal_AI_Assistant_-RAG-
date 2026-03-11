"""Document upload and analysis router."""
import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from backend.database import get_db
from backend.models.user import User, UserRole
from backend.models.case import Case, CaseDocument
from backend.routers.auth import get_current_user
from backend.ingestion.pipeline import ingestion_pipeline
from backend.ai.agents.evidence_agent import evidence_agent
from backend.ingestion.document_parser import document_parser
from backend.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    case_id: Optional[str] = Form(None),
    document_type: Optional[str] = Form(None),
    submitted_by: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Upload and process a legal document."""
    # Validate file
    allowed_types = [".pdf", ".txt", ".docx", ".doc"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported. Allowed: {allowed_types}")
    
    # Save file
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(upload_dir, f"{file_id}{ext}")
    
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create DB record
    doc = CaseDocument(
        case_id=case_id or "general",
        filename=file.filename,
        file_path=file_path,
        file_type=ext,
        file_size=len(content),
        document_type=document_type,
        submitted_by=submitted_by,
        description=description,
        is_processed="processing",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    # Parse and ingest
    try:
        metadata = {
            "content_type": "uploaded_document",
            "document_type": document_type or "general",
            "source_name": "user_upload",
            "act_name": file.filename,
        }
        result = ingestion_pipeline.ingest_file(file_path, metadata)
        
        doc.is_processed = "completed"
        doc.chunk_count = result.get("chunks_stored", 0)
        await db.commit()
        
        return {
            "id": doc.id,
            "filename": file.filename,
            "status": "processed",
            "chunks": result.get("chunks_stored", 0),
        }
    except Exception as e:
        doc.is_processed = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: str,
    question: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Analyze an uploaded document with the Evidence Agent."""
    result = await db.execute(select(CaseDocument).where(CaseDocument.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Parse document
    parsed = document_parser.parse_file(doc.file_path)
    if not parsed.get("text"):
        raise HTTPException(status_code=400, detail="Could not extract text from document")
    
    # Analyze
    if question:
        analysis = await evidence_agent.analyze_document(parsed["text"], question)
    else:
        analysis = await evidence_agent.extract_key_facts(parsed["text"])
    
    return {
        "document_id": document_id,
        "filename": doc.filename,
        "analysis": analysis,
    }

from backend.ai.agents.argument_agent import argument_agent

@router.post("/{document_id}/build-arguments")
async def build_arguments(
    document_id: str,
    side: str = Form("petitioner"),
    context: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Generate legal arguments based on an uploaded document and context."""
    result = await db.execute(select(CaseDocument).where(CaseDocument.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    parsed = document_parser.parse_file(doc.file_path)
    text = parsed.get("text", "")
    
    if not text and not context:
        raise HTTPException(status_code=400, detail="No readable text found in document or context provided")
    
    # Truncate text to avoid context limits
    preview = text[:8000] + ("..." if len(text) > 8000 else "")
    
    case_details = f"Context provided by lawyer:\n{context or 'None'}\n\nDocument Contents:\n{preview}"
    
    args = await argument_agent.generate_arguments(case_details, side)
    
    return {
        "document_id": document_id,
        "arguments": args.get("arguments", ""),
    }


@router.get("/")
async def list_documents(
    case_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """List uploaded documents."""
    query = select(CaseDocument)
    if case_id:
        query = query.where(CaseDocument.case_id == case_id)
    query = query.order_by(CaseDocument.uploaded_at.desc())
    
    result = await db.execute(query)
    docs = result.scalars().all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_type": d.file_type,
            "file_size": d.file_size,
            "document_type": d.document_type,
            "submitted_by": d.submitted_by,
            "is_processed": d.is_processed,
            "chunk_count": d.chunk_count,
            "admissibility_status": d.admissibility_status,
            "uploaded_at": d.uploaded_at.isoformat(),
        }
        for d in docs
    ]

class AdmissibilityUpdate(BaseModel):
    status: str

@router.put("/{document_id}/admissibility")
async def update_admissibility(
    document_id: str,
    update: AdmissibilityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user),
):
    """Judge endpoint to mark evidence as valid or invalid."""
    if not current_user or current_user.role != UserRole.JUDGE.value:
        raise HTTPException(status_code=403, detail="Only judges can validate evidence")
        
    result = await db.execute(select(CaseDocument).where(CaseDocument.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    doc.admissibility_status = update.status
    await db.commit()
    
    return {"status": "updated", "admissibility_status": doc.admissibility_status}
