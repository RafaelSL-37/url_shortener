from datetime import datetime, timezone
from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, String
from models.base import Base


class UrlModel(Base):
    __tablename__ = "urls"
    short_url = Column(String(10), primary_key=True)
    long_url = Column(String(2048), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"))
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))