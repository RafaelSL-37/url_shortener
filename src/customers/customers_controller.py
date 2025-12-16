from fastapi import APIRouter, HTTPException, Depends
from typing import List
from uuid import UUID as UUIDType
from customers.customers_dto import Customer, CustomerCreate, CustomerUpdate
from db import AsyncSessionLocal
from auth import get_current_customer, create_access_token, verify_password, hash_password, Token
from customers.customers_service import (
    find_customer_by_email,
    create_customer,
    list_customers,
    get_customer_by_id,
    update_customer,
    soft_delete_customer,
)
from pydantic import BaseModel


customers_router = APIRouter(prefix="/api/customers", tags=["customers"])


class LoginRequest(BaseModel):
    email: str
    password: str


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@customers_router.post("/login", response_model=Token)
async def login(payload: LoginRequest, session=Depends(get_session)):
    customer = await find_customer_by_email(session, payload.email)

    if not customer or not verify_password(payload.password, customer.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(customer_id=customer.id)
    return Token(access_token=access_token, token_type="bearer")


@customers_router.post("/", response_model=Customer)
async def create_customer(payload: CustomerCreate, session=Depends(get_session)):
    hashed_password = hash_password(payload.password)
    customer = await create_customer(session, payload.email, hashed_password)

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

    customers = await list_customers(session, with_deleted)
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

    customer = await get_customer_by_id(session, customer_id, with_deleted)

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

    customer = await get_customer_by_id(session, customer_id, with_deleted=False)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    password_hash = None
    if payload.password is not None:
        password_hash = hash_password(payload.password)

    updated = await update_customer(
        session, customer, email=payload.email, password_hash=password_hash, type=payload.type
    )

    return Customer(
        id=updated.id,
        email=updated.email,
        type=updated.type,
        created_at=updated.created_at,
        updated_at=updated.updated_at,
        deleted_at=updated.deleted_at,
    )


@customers_router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: UUIDType, session=Depends(get_session), current_customer=Depends(get_current_customer)):
    if not current_customer:
        raise HTTPException(status_code=401, detail="Authentication required")

    customer = await get_customer_by_id(session, customer_id, with_deleted=False)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    await soft_delete_customer(session, customer)

    return None
