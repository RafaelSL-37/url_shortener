from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator
from uuid import UUID as UUIDType


class CustomerCreate(BaseModel):
    email: EmailStr
    password: str


class CustomerUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    type: Optional[str] = None

    @field_validator('type')
    def validate_type(cls, v):
        if v is not None and v not in ["DEFAULT", "PREMIUM"]:
            raise ValueError('type must be either "DEFAULT" or "PREMIUM"')
        return v


class Customer(BaseModel):
    id: UUIDType
    email: EmailStr
    type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None