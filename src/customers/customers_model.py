from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, String
from base_model import Base



class CustomerModel(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)