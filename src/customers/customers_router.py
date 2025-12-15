from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID as UUIDType
from datetime import datetime, timezone
from sqlalchemy import select
from customers.customers_dto import Customer, CustomerCreate, CustomerUpdate
from customers.customers_model import CustomerModel
from db import AsyncSessionLocal
from auth import (
    get_current_customer,
    create_access_token,
    verify_password,
    hash_password,
    Token,
)
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


customers_router = APIRouter(prefix="/api/customers", tags=["customers"])


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@customers_router.post("/login", response_model=Token)
async def login(payload: LoginRequest, session=Depends(get_session)):
    customers = await session.execute(
        select(CustomerModel).where(CustomerModel.email == payload.email, CustomerModel.deleted_at.is_(None))
    )
    customer = customers.scalars().first()

    if not customer or not verify_password(payload.password, customer.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(customer_id=customer.id)
    return Token(access_token=access_token, token_type="bearer")


@customers_router.post("/", response_model=Customer)
async def create_customer(payload: CustomerCreate, session=Depends(get_session)):
    hashed_password = hash_password(payload.password)
    customer = CustomerModel(email=str(payload.email), password=hashed_password)
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    
    return Customer(
        id=customer.id,
        email=customer.email,
        type=customer.type,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        deleted_at=customer.deleted_at,
    )


@customers_router.get("/", response_model=List[Customer])
async def list_customers(with_deleted: bool = False, session=Depends(get_session), current_customer=Depends(get_current_customer)):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query = select(CustomerModel)
    if not with_deleted:
        query = query.where(CustomerModel.deleted_at.is_(None))
    customers = await session.execute(query)
    customers = customers.scalars().all()

    return [
        Customer(
            id=customer.id,
            email=customer.email,
            type=customer.type,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            deleted_at=customer.deleted_at,
        )
        for customer in customers
    ]


@customers_router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: UUIDType, with_deleted: bool = False, session=Depends(get_session), current_customer=Depends(get_current_customer)):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    query = select(CustomerModel).where(CustomerModel.id == customer_id)
    if not with_deleted:
        query = query.where(CustomerModel.deleted_at.is_(None))
    customers = await session.execute(query)
    customer = customers.scalars().first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return Customer(
        id=customer.id,
        email=customer.email,
        type=customer.type,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        deleted_at=customer.deleted_at,
    )


@customers_router.put("/{customer_id}", response_model=Customer)
async def update_customer(customer_id: UUIDType, payload: CustomerUpdate, session=Depends(get_session), current_customer=Depends(get_current_customer)):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    customers = await session.execute(
        select(CustomerModel).where(CustomerModel.id == customer_id, CustomerModel.deleted_at.is_(None))
    )
    customer = customers.scalars().first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    if payload.email is not None:
        customer.email = str(payload.email)
    if payload.password is not None:
        customer.password = hash_password(payload.password)
    if payload.type is not None:
        customer.type = payload.type

    customer.updated_at = datetime.now(timezone.utc)
    session.add(customer)
    await session.commit()
    await session.refresh(customer)

    return Customer(
        id=customer.id,
        email=customer.email,
        type=customer.type,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
        deleted_at=customer.deleted_at,
    )


@customers_router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: UUIDType, session=Depends(get_session), current_customer=Depends(get_current_customer)):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    customers = await session.execute(
        select(CustomerModel).where(CustomerModel.id == customer_id, CustomerModel.deleted_at.is_(None))
    )
    customer = customers.scalars().first()

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    customer.deleted_at = datetime.now(timezone.utc)
    session.add(customer)
    await session.commit()

    return None
