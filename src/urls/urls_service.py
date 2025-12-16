from sqlalchemy import select
from urls.urls_model import UrlModel
import random
import string
import os


SHORT_LEN = int(os.getenv("SHORT_LEN", "6"))


async def gen_unique_short(session):
    while True:
        s = random_short_url_id()
        result = await session.execute(select(UrlModel).where(UrlModel.short_url == s))

        if not result.scalars().first():
            return s


async def create_shortened_url(session, short_url, long_url, customer_id, expiration_date):
    url_record = UrlModel(
        short_url=short_url,
        long_url=str(long_url),
        customer_id=customer_id,
        expiration_date=expiration_date,
        clicks=0,
    )

    session.add(url_record)
    await session.commit()

    return url_record


async def get_url_by_short(session, short):
    urls = await session.execute(select(UrlModel).where(UrlModel.short_url == short))
    return urls.scalars().first()


def random_short_url_id():
    return "".join(random.choices(string.ascii_letters + string.digits, k=SHORT_LEN))