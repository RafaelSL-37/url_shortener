from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from base_model import Base


class UrlModel(Base):
    __tablename__ = "urls"
    short_url = Column(String(10), primary_key=True)
    long_url = Column(String(2048), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), nullable=True)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expiration_date = Column(DateTime(timezone=True), nullable=True)