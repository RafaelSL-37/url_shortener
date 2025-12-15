from http.client import HTTPException
from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy import select
from datetime import datetime, timezone
from base_model import Base
from db import AsyncSessionLocal, engine
from customers.customers_router import customers_router
from urls.urls_model import UrlModel
from urls.urls_router import urls_router

app = FastAPI()


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

#This endpoint is not referenced on the urls_router as to reduce the link size.
@app.get("/r/{short}")
async def redirect_short(short: str, session=Depends(get_session)):
    urls = await session.execute(select(UrlModel).where(UrlModel.short_url == short))
    url = urls.scalars().first()

    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if url.expiration_date is not None and datetime.now(timezone.utc) > url.expiration_date:
        raise HTTPException(status_code=404, detail="URL has expired")
    
    url.clicks += 1
    await session.commit()

    return {"redirect": url.long_url}


app.include_router(customers_router)
app.include_router(urls_router)