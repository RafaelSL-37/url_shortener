from datetime import datetime
from uuid import uuid4
from sqlalchemy import UUID, Column, DateTime, Integer, String
from base import Base


class CustomerModel(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.now(datetime.timezone.utc), nullable=True)
    deleted_at = Column(DateTime, nullable=True)