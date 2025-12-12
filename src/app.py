from ast import List
from datetime import datetime
import os
import string
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from dto.customer import Customer, CustomerCreate, CustomerUpdate
from models.base import Base
from models.customer import CustomerModel
from models.url import UrlModel
from dto.short_url import ShortenRequest
from uuid import UUID as UUIDType

USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
DATABASE = os.getenv('POSTGRES_DATABASE')
HOST = os.getenv('POSTGRES_HOST')
PORT = os.getenv('POSTGRES_PORT')
DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
SHORT_LEN = 6

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def gen_unique_short():
    async with AsyncSessionLocal() as session:
        while True:
            s = "".join(random.choices(string.ascii_letters + string.digits, k=SHORT_LEN))
            result = await session.execute(select(UrlModel).where(UrlModel.short == s))
            if not result.scalars().first():
                return s

@app.post("/api/urls/shorten")
async def shorten(req: ShortenRequest):
    async with AsyncSessionLocal() as session:
        short = await gen_unique_short()
        url_record = UrlModel(short=short, longUrl=str(req.longUrl), clicks=0)
        session.add(url_record)
        await session.commit()
        
        base = os.getenv("BASE_URL", "http://localhost:8000")
        return {"shortUrl": f"{base}/{short}"}

@app.get("/api/urls/{short}")
async def get_mapping(short: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UrlModel).where(UrlModel.short == short))
        doc = result.scalars().first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")
        return {"longUrl": doc.longUrl, "clicks": doc.clicks}

@app.get("/{short}")
async def redirect_short(short_url: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UrlModel).where(UrlModel.short == short_url))
        doc = result.scalars().first()
        
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")
        
        doc.clicks += 1
        await session.commit()
        return RedirectResponse(doc.longUrl)
    
@app.post("/api/customers", response_model=Customer)
async def create_customer(payload: CustomerCreate):
    async with AsyncSessionLocal() as session:
        customer = CustomerModel(email=str(payload.email), password=payload.password)
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
        return Customer(
            id=customer.id,
            email=customer.email,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            deleted_at=customer.deleted_at,
        )

@app.get("/api/customers", response_model=List[Customer])
async def list_customers(with_deleted: bool = False):
    async with AsyncSessionLocal() as session:
        stmt = select(CustomerModel)
        if not with_deleted:
            stmt = stmt.where(CustomerModel.deleted_at.is_(None))
        result = await session.execute(stmt)
        customers = result.scalars().all()
        return [
            Customer(
                id=c.id,
                email=c.email,
                created_at=c.created_at,
                updated_at=c.updated_at,
                deleted_at=c.deleted_at,
            )
            for c in customers
        ]

@app.get("/api/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: UUIDType, with_deleted: bool = False):
    async with AsyncSessionLocal() as session:
        stmt = select(CustomerModel).where(CustomerModel.id == customer_id)
        if not with_deleted:
            stmt = stmt.where(CustomerModel.deleted_at.is_(None))
        result = await session.execute(stmt)
        customer = result.scalars().first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return Customer(
            id=customer.id,
            email=customer.email,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            deleted_at=customer.deleted_at,
        )

@app.put("/api/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: UUIDType, payload: CustomerUpdate):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CustomerModel).where(CustomerModel.id == customer_id, CustomerModel.deleted_at.is_(None))
        )
        customer = result.scalars().first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        if payload.email is not None:
            customer.email = str(payload.email)
        if payload.password is not None:
            customer.password = payload.password
        customer.updated_at = datetime.now(datetime.timezone.utc)
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
        return Customer(
            id=customer.id,
            email=customer.email,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            deleted_at=customer.deleted_at,
        )

@app.delete("/api/customers/{customer_id}", status_code=204)
async def delete_customer(customer_id: UUIDType):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(CustomerModel).where(CustomerModel.id == customer_id, CustomerModel.deleted_at.is_(None))
        )
        customer = result.scalars().first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        customer.deleted_at = datetime.now(datetime.timezone.utc)  # soft delete
        session.add(customer)
        await session.commit()
        return None