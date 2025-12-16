from sqlalchemy import select
from datetime import datetime, timezone
from customers.customers_model import CustomerModel


async def find_customer_by_email(session, email):
    customers = await session.execute(
        select(CustomerModel).where(CustomerModel.email == email, CustomerModel.deleted_at.is_(None))
    )
    return customers.scalars().first()


async def create_customer(session, email, hashed_password):
    customer = CustomerModel(email=str(email), password=hashed_password)
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def list_customers(session, with_deleted: bool = False):
    query = select(CustomerModel)
    if not with_deleted:
        query = query.where(CustomerModel.deleted_at.is_(None))
    customers = await session.execute(query)
    return customers.scalars().all()


async def get_customer_by_id(session, customer_id, with_deleted: bool = False):
    query = select(CustomerModel).where(CustomerModel.id == customer_id)
    if not with_deleted:
        query = query.where(CustomerModel.deleted_at.is_(None))
    customers = await session.execute(query)
    return customers.scalars().first()


async def update_customer(session, customer, email=None, password_hash=None, type=None):
    if email is not None:
        customer.email = str(email)
    if password_hash is not None:
        customer.password = password_hash
    if type is not None:
        customer.type = type

    customer.updated_at = datetime.now(timezone.utc)
    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    return customer


async def soft_delete_customer(session, customer):
    customer.deleted_at = datetime.now(timezone.utc)
    session.add(customer)
    await session.commit()
    return customer
