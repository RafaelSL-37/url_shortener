import random
import string
import os
import urls.urls_repository as urls_repository


SHORT_LEN = int(os.getenv("SHORT_LEN", "6"))


async def gen_unique_short(session):
    while True:
        s = random_short_url_id()
        if not await urls_repository.exists_short(session, s):
            return s


async def create_shortened_url(session, short_url, long_url, customer_id, expiration_date):
    return await urls_repository.create(session, short_url, long_url, customer_id, expiration_date)


async def get_url_by_short(session, short):
    return await urls_repository.find_by_short(session, short)


def random_short_url_id():
    return "".join(random.choices(string.ascii_letters + string.digits, k=SHORT_LEN))


class UrlService:
    def __init__(self):
        pass

    async def gen_unique_short(self, uow):
        while True:
            s = random_short_url_id()
            if not await uow.urls.exists_short(s):
                return s

    async def create_shortened(self, uow, short_url, long_url, customer_id, expiration_date):
        return await uow.urls.create(short_url, long_url, customer_id, expiration_date)

    async def get_url_by_short(self, uow, short):
        return await uow.urls.find_by_short(short)