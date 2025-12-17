from sqlalchemy import select
from urls.urls_model import UrlModel


async def find_by_short(session, short):
    res = await session.execute(select(UrlModel).where(UrlModel.short_url == short))
    return res.scalars().first()


async def create(session, short_url, long_url, customer_id, expiration_date):
    url_record = UrlModel(
        short_url=short_url,
        long_url=str(long_url),
        customer_id=customer_id,
        expiration_date=expiration_date,
        clicks=0,
    )

    session.add(url_record)
    await session.commit()
    await session.refresh(url_record)
    
    return url_record


async def exists_short(session, short):
    res = await session.execute(select(UrlModel).where(UrlModel.short_url == short))
    return bool(res.scalars().first())
