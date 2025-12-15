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
    def validate_type(cls, value):
        if value is not None and value not in ["DEFAULT", "PREMIUM"]:
            raise ValueError(f'Type must be either "DEFAULT" or "PREMIUM", received {value}')
        return value

class Customer(BaseModel):
    id: UUIDType
    email: EmailStr
    type: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None