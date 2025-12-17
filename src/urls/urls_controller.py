from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timezone, timedelta
import os
from urls.urls_dto import UrlShortenRequest
from unit_of_work import UnitOfWork
from urls.urls_service import UrlService
from auth import get_current_customer


urls_router = APIRouter(prefix="/api/urls", tags=["urls"])
async def get_uow():
    async with UnitOfWork() as uow:
        yield uow


@urls_router.post("/shorten")
async def shorten(req: UrlShortenRequest, uow: UnitOfWork = Depends(get_uow), request: Request = None, current_customer=Depends(get_current_customer)):
    svc = UrlService()
    short_url = await svc.gen_unique_short(uow)

    if current_customer is None:
        expiration_date = datetime.now(timezone.utc) + timedelta(days=7)
    elif current_customer.type == "PREMIUM":
        expiration_date = None
    else:
        expiration_date = datetime.now(timezone.utc) + timedelta(days=30)

    await svc.create_shortened(uow, short_url, req.longUrl, current_customer.id if current_customer else None, expiration_date)

    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    return {"shortUrl": f"{base_url}/r/{short_url}"}


@urls_router.get("/{short}")
async def get_shortened_url_mapping(short: str, uow: UnitOfWork = Depends(get_uow), request: Request = None, current_customer=Depends(get_current_customer)):
    svc = UrlService()
    url = await svc.get_url_by_short(uow, short)

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"longUrl": url.long_url, "clicks": url.clicks}