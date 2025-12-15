import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy import select
from db import AsyncSessionLocal
from customers.customers_model import CustomerModel

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

security = HTTPBearer()


class TokenData(BaseModel):
    customer_id: str


class Token(BaseModel):
    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(customer_id: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "customer_id": str(customer_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id: str = payload.get("customer_id")
        
        if customer_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(customer_id=customer_id) 
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CustomerModel).where(
                CustomerModel.id == token_data.customer_id,
                CustomerModel.deleted_at.is_(None),
            )
        )
        customer = result.scalars().first()
        
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Customer not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return customer


async def get_current_customer_optional(request: Request) -> Optional[CustomerModel]:
    """Get the current authenticated customer from the JWT token, or None if not authenticated."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header[7:]  # Remove "Bearer " prefix
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        customer_id: str = payload.get("customer_id")
        
        if customer_id is None:
            return None
        
        token_data = TokenData(customer_id=customer_id)
    except jwt.InvalidTokenError:
        return None
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CustomerModel).where(
                CustomerModel.id == token_data.customer_id,
                CustomerModel.deleted_at.is_(None),
            )
        )
        customer = result.scalars().first()
        return customer
