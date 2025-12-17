from sqlalchemy import select
from urls.urls_model import UrlModel


async def find_by_short(session, short):
    return await UrlRepository(session).find_by_short(short)


async def create(session, short_url, long_url, customer_id, expiration_date):
    return await UrlRepository(session).create(short_url, long_url, customer_id, expiration_date)


async def exists_short(session, short):
    return await UrlRepository(session).exists_short(short)


class UrlRepository:
    def __init__(self, session):
        self.session = session
    async def find_by_short(self, short):
        res = await self.session.execute(select(UrlModel).where(UrlModel.short_url == short))
        return res.scalars().first()

    async def create(self, short_url, long_url, customer_id, expiration_date):
        url_record = UrlModel(
            short_url=short_url,
            long_url=str(long_url),
            customer_id=customer_id,
            expiration_date=expiration_date,
            clicks=0,
        )
        self.session.add(url_record)
        await self.session.commit()
        await self.session.refresh(url_record)
        return url_record

    async def exists_short(self, short):
        res = await self.session.execute(select(UrlModel).where(UrlModel.short_url == short))
        return bool(res.scalars().first())
