from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID as UUIDType


class CustomerCreate(BaseModel):
    email: EmailStr
    password: str


class CustomerUpdate(BaseModel):
    email: EmailStr
    password: Optional[str] = None


class Customer(BaseModel):
    id: UUIDType
    email: EmailStr
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None