import random
import string
import os


SHORT_LEN = int(os.getenv("SHORT_LEN", "6"))


def random_short_url_id():
    return "".join(random.choices(string.ascii_letters + string.digits, k=SHORT_LEN))


class UrlService:
    def __init__(self):
        pass

    async def gen_unique_short(self, uow):
        while True:
            s = random_short_url_id()
            if not await uow.urls_repository.exists_short(s):
                return s

    async def create_shortened(self, uow, short_url, long_url, customer_id, expiration_date):
        return await uow.urls_repository.create(short_url, long_url, customer_id, expiration_date)

    async def get_url_by_short(self, uow, short):
        return await uow.urls_repository.find_by_short(short)