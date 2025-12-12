import os
import string
import random
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from models.base import Base
from models.url import UrlModel
from dto.short_url import ShortenRequest

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres:5432/url_shortener")
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