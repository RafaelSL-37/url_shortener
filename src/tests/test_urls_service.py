import pytest
from urls.urls_service import UrlService
from tests.mocks.mock_urls_repository import MockUrlRepository
from mocks.mock_unit_of_work import MockUnitOfWork


@pytest.mark.asyncio
async def test_gen_unique_short_returns_unused_short():
    repo = MockUrlRepository()
    repo.urls["ABC123"] = {"short_url": "ABC123"}

    uow = MockUnitOfWork(urls_repository=repo)
    service = UrlService()

    short = await service.gen_unique_short(uow)

    assert short not in repo.urls


@pytest.mark.asyncio
async def test_create_shortened_stores_url():
    repo = MockUrlRepository()
    uow = MockUnitOfWork(urls_repository=repo)
    service = UrlService()

    result = await service.create_shortened(
        uow,
        short_url="abc123",
        long_url="https://example.com",
        customer_id=1,
        expiration_date=None,
    )

    assert repo.urls["abc123"]["long_url"] == "https://example.com"
    assert result["short_url"] == "abc123"


@pytest.mark.asyncio
async def test_get_url_by_short_returns_url():
    repo = MockUrlRepository()
    repo.urls["abc123"] = {
        "short_url": "abc123",
        "long_url": "https://example.com",
        "clicks": 0,
    }

    uow = MockUnitOfWork(urls_repository=repo)
    service = UrlService()

    url = await service.get_url_by_short(uow, "abc123")

    assert url["long_url"] == "https://example.com"