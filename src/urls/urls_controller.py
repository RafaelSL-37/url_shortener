from fastapi import APIRouter, Depends, HTTPException, Request
from db import AsyncSessionLocal
from datetime import datetime, timezone, timedelta
import os
from urls.urls_dto import UrlShortenRequest
from urls.urls_service import gen_unique_short, create_shortened_url, get_url_by_short
from auth import get_current_customer


urls_router = APIRouter(prefix="/api/urls", tags=["urls"])


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


@urls_router.post("/shorten")
async def shorten(req: UrlShortenRequest, session=Depends(get_session), request: Request = None, current_customer=Depends(get_current_customer)):
    short_url = await gen_unique_short(session)

    if current_customer is None:
        expiration_date = datetime.now(timezone.utc) + timedelta(days=7)
    elif current_customer.type == "PREMIUM":
        expiration_date = None
    else:
        expiration_date = datetime.now(timezone.utc) + timedelta(days=30)

    await create_shortened_url(session, short_url, req.longUrl, current_customer.id if current_customer else None, expiration_date)

    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    return {"shortUrl": f"{base_url}/r/{short_url}"}


@urls_router.get("/{short}")
async def get_shortened_url_mapping(short: str, session=Depends(get_session), request: Request = None, current_customer=Depends(get_current_customer)):
    url = await get_url_by_short(session, short)

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"longUrl": url.long_url, "clicks": url.clicks}