from db import AsyncSessionLocal
from customers.customers_repository import CustomerRepository
from urls.urls_repository import UrlRepository


class UnitOfWork:
    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        self.session = None
        self.customers = None
        self.urls = None
        self._session_cm = None

    async def __aenter__(self):
        self._session_cm = self.session_factory()
        self.session = await self._session_cm.__aenter__()
        self.customers_repository = CustomerRepository(self.session)
        self.urls_repository = UrlRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self._session_cm.__aexit__(exc_type, exc, tb)
