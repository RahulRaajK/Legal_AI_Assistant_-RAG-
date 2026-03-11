"""Legal document, Chat session, and Chat message models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from backend.database import Base


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Document identification
    title = Column(String, nullable=False, index=True)
    act_name = Column(String, nullable=True, index=True)
    section_number = Column(String, nullable=True)
    
    # Source info
    source_url = Column(String, nullable=True)
    source_name = Column(String, nullable=True)  # indiacode, indiankanoon, etc.
    
    # Content
    content = Column(Text, nullable=False)
    content_type = Column(String, default="statute")  # statute, judgment, amendment, article
    
    # Metadata
    court = Column(String, nullable=True)
    judge = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    citation = Column(String, nullable=True)
    case_type = Column(String, nullable=True)
    keywords = Column(Text, nullable=True)  # comma-separated
    
    # Processing
    is_indexed = Column(String, default="no")  # no, yes
    chunk_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Chat")
    context_mode = Column(String, default="general")  # general, case_specific, document_qa
    case_id = Column(String, nullable=True)  # If chat is about a specific case
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", lazy="selectin")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Structured response fields (stored as JSON strings)
    relevant_acts = Column(Text, nullable=True)
    relevant_sections = Column(Text, nullable=True)
    case_references = Column(Text, nullable=True)
    legal_reasoning = Column(Text, nullable=True)
    key_points = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
