from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from db import AsyncSessionLocal
import os
import random
import string
from urls.urls_dto import UrlShortenRequest
from urls.urls_model import UrlModel

urls_router = APIRouter(prefix="/api/urls", tags=["urls"])
SHORT_LEN = int(os.getenv("SHORT_LEN", "6"))


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


async def gen_unique_short(session):
    while True:
        s = "".join(random.choices(string.ascii_letters + string.digits, k=SHORT_LEN))
        result = await session.execute(select(UrlModel).where(UrlModel.short_url == s))

        if not result.scalars().first():
            return s


@urls_router.post("/shorten")
async def shorten(req: UrlShortenRequest, session=Depends(get_session)):
    short_url = await gen_unique_short(session)
    url_record = UrlModel(short_url=short_url, long_url=str(req.longUrl), clicks=0)
    session.add(url_record)
    await session.commit()

    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    return {"shortUrl": f"{base_url}/{short_url}"}


@urls_router.get("/{short}")
async def get_mapping(short: str, session=Depends(get_session)):
    urls = await session.execute(select(UrlModel).where(UrlModel.short_url == short))
    url = urls.scalars().first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"longUrl": url.long_url, "clicks": url.clicks}
