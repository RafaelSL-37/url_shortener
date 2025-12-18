class MockUrlRepository:
    def __init__(self):
        self.urls = {}

    async def find_by_short(self, short):
        return self.urls.get(short)

    async def create(self, short_url, long_url, customer_id, expiration_date):
        url = {
            "short_url": short_url,
            "long_url": str(long_url),
            "customer_id": customer_id,
            "expiration_date": expiration_date,
            "clicks": 0,
        }
        self.urls[short_url] = url
        return url

    async def exists_short(self, short):
        return short in self.urls