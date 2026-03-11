"""Law registry for canonical tracking of statutes across sources."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, UniqueConstraint
from backend.database import Base


class LawRegistry(Base):
    """Canonical registry entry for a law/act (central, state, or UT)."""

    __tablename__ = "law_registry"
    __table_args__ = (
        # Avoid duplicate logical laws per jurisdiction
        UniqueConstraint("jurisdiction", "act_number", "year", name="uq_law_jurisdiction_act_year"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Canonical identification
    canonical_id = Column(String, index=True, nullable=True)  # e.g. INDIA:ACT:1950:CONSTITUTION
    title = Column(String, nullable=False, index=True)
    jurisdiction = Column(String, nullable=False, index=True)  # central, state:KA, ut:DL, etc.
    act_number = Column(String, nullable=True, index=True)
    year = Column(Integer, nullable=True, index=True)

    # Source + ingestion tracking
    source_primary = Column(String, nullable=True)  # e.g. indiacode, state_portal_KA
    source_urls = Column(Text, nullable=True)  # JSON string list of known URLs
    last_seen_at = Column(DateTime, nullable=True)
    last_ingested_at = Column(DateTime, nullable=True)

    # Content hash to detect changes (normalized full text)
    content_hash = Column(String, nullable=True, index=True)

    # Status: active, repealed, unknown, invalid
    status = Column(String, default="active", index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

