import pytest
from customers.customers_service import CustomerService
from tests.mocks.mock_customers_repository import MockCustomerRepository
from mocks.mock_unit_of_work import MockUnitOfWork


@pytest.mark.asyncio
async def test_create_customer():
    repo = MockCustomerRepository()
    uow = MockUnitOfWork(customers_repository=repo)
    service = CustomerService()

    customer = await service.create_customer(
        uow, None, "test@example.com", "hashed_pw"
    )

    assert customer["email"] == "test@example.com"
    assert customer["id"] == 1


@pytest.mark.asyncio
async def test_find_customer_by_email():
    repo = MockCustomerRepository()
    uow = MockUnitOfWork(customers_repository=repo)
    service = CustomerService()

    await service.create_customer(uow, None, "a@test.com", "pw")

    customer = await service.find_customer_by_email(
        uow, None, "a@test.com"
    )

    assert customer is not None
    assert customer["email"] == "a@test.com"


@pytest.mark.asyncio
async def test_soft_delete_customer():
    repo = MockCustomerRepository()
    uow = MockUnitOfWork(customers_repository=repo)
    service = CustomerService()

    customer = await service.create_customer(uow, None, "b@test.com", "pw")
    await service.soft_delete_customer(uow, None, customer)

    found = await service.get_customer_by_id(
        uow, None, customer["id"]
    )

    assert found is None