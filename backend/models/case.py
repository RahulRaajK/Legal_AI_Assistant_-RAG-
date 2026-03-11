"""Case and CaseDocument models for case management."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Float
from sqlalchemy.orm import relationship
from backend.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Case identifiers
    case_number = Column(String, index=True, nullable=True)
    fir_number = Column(String, index=True, nullable=True)
    case_code = Column(String, index=True, nullable=True)
    case_title = Column(String, nullable=False)
    case_type = Column(String, nullable=True)  # civil, criminal, constitutional, etc.
    act = Column(String, nullable=True)
    
    # Parties & Representation
    petitioner = Column(String, nullable=True)
    respondent = Column(String, nullable=True)
    advocate_name = Column(String, nullable=True)
    
    # Court info
    court_name = Column(String, nullable=True)
    registration_number = Column(String, nullable=True)
    judge_name = Column(String, nullable=True)
    
    # Core Data (Stored as JSON text logs for flexibility)
    petitioner_witnesses = Column(Text, default="[]") 
    respondent_witnesses = Column(Text, default="[]")
    case_history = Column(Text, default="[]")       # List of {date, judge, purpose}
    process_details = Column(Text, default="[]")    # List of {id, date, title, issued}
    final_orders = Column(Text, default="[]")       # List of {number, date, details}
    
    # Text Analysis
    description = Column(Text, nullable=True)
    facts = Column(Text, nullable=True)
    status = Column(String, default="active")  # active, pending, closed
    priority = Column(String, default="medium")
    
    # AI Analysis
    ai_summary = Column(Text, nullable=True)
    win_probability = Column(Float, nullable=True) 
    ai_arguments = Column(Text, nullable=True)  # JSON string
    relevant_acts = Column(Text, nullable=True) # JSON string
    relevant_precedents = Column(Text, nullable=True) # JSON string
    
    # Dates
    filing_date = Column(DateTime, nullable=True)
    next_hearing_date = Column(DateTime, nullable=True)
    hearing_time = Column(String, nullable=True) # e.g. "10:30 AM"
    
    # Hearing Attendance
    petitioner_attendance = Column(String, nullable=True) # present, absent
    respondent_attendance = Column(String, nullable=True) # present, absent
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="cases")
    documents = relationship("CaseDocument", back_populates="case", lazy="selectin")


class CaseDocument(Base):
    __tablename__ = "case_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)
    
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)  # pdf, docx, image, etc.
    file_size = Column(Integer, nullable=True)
    
    document_type = Column(String, nullable=True)  # fir, witness_statement, contract, court_filing, evidence
    submitted_by = Column(String, nullable=True)  # petitioner, respondent, court, neutral
    description = Column(Text, nullable=True)
    
    # Judge Admissibility validation
    admissibility_status = Column(String, default="pending") # pending, valid, invalid
    
    # RAG processing
    is_processed = Column(String, default="pending")  # pending, processing, completed, failed
    chunk_count = Column(Integer, default=0)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    case = relationship("Case", back_populates="documents")
