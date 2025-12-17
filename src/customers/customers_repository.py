from sqlalchemy import select
from datetime import datetime, timezone
from customers.customers_model import CustomerModel


async def find_by_email(session, email):
    res = await session.execute(
        select(CustomerModel).where(CustomerModel.email == email, CustomerModel.deleted_at.is_(None))
    )

    return res.scalars().first()


async def create(session, email, password):
    customer = CustomerModel(email=str(email), password=password)

    session.add(customer)
    await session.commit()
    await session.refresh(customer)
    
    return customer


async def list_customers(session, with_deleted: bool = False):
    query = select(CustomerModel)

    if not with_deleted:
        query = query.where(CustomerModel.deleted_at.is_(None))

    res = await session.execute(query)
    return res.scalars().all()


async def get_by_id(session, customer_id, with_deleted: bool = False):
    query = select(CustomerModel).where(CustomerModel.id == customer_id)

    if not with_deleted:
        query = query.where(CustomerModel.deleted_at.is_(None))

    res = await session.execute(query)
    return res.scalars().first()


async def update(session, customer):
    customer.updated_at = datetime.now(timezone.utc)

    session.add(customer)
    await session.commit()
    await session.refresh(customer)

    return customer


async def soft_delete(session, customer):
    customer.deleted_at = datetime.now(timezone.utc)

    session.add(customer)
    await session.commit()
    
    return customer
