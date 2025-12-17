from sqlalchemy import select
from datetime import datetime, timezone
from customers.customers_model import CustomerModel


async def find_by_email(session, email):
    return await CustomerRepository(session).find_by_email(email)


async def create(session, email, password):
    return await CustomerRepository(session).create(email, password)


async def list_customers(session, with_deleted: bool = False):
    return await CustomerRepository(session).list_customers(with_deleted)


async def get_by_id(session, customer_id, with_deleted: bool = False):
    return await CustomerRepository(session).get_by_id(customer_id, with_deleted)


async def update(session, customer):
    return await CustomerRepository(session).update(customer)


async def soft_delete(session, customer):
    return await CustomerRepository(session).soft_delete(customer)


class CustomerRepository:
    def __init__(self, session):
        self.session = session
    async def find_by_email(self, email):
        res = await self.session.execute(
            select(CustomerModel).where(CustomerModel.email == email, CustomerModel.deleted_at.is_(None))
        )
        return res.scalars().first()

    async def create(self, email, password):
        customer = CustomerModel(email=str(email), password=password)
        self.session.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)
        return customer

    async def list_customers(self, with_deleted: bool = False):
        query = select(CustomerModel)
        if not with_deleted:
            query = query.where(CustomerModel.deleted_at.is_(None))
        res = await self.session.execute(query)
        return res.scalars().all()

    async def get_by_id(self, customer_id, with_deleted: bool = False):
        query = select(CustomerModel).where(CustomerModel.id == customer_id)
        if not with_deleted:
            query = query.where(CustomerModel.deleted_at.is_(None))
        res = await self.session.execute(query)
        return res.scalars().first()

    async def update(self, customer):
        customer.updated_at = datetime.now(timezone.utc)
        self.session.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)
        return customer

    async def soft_delete(self, customer):
        customer.deleted_at = datetime.now(timezone.utc)
        self.session.add(customer)
        await self.session.commit()
        return customer
