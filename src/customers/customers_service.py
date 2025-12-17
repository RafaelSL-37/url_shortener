import customers.customers_repository as customers_repository


async def find_customer_by_email(session, email):
    return await customers_repository.find_by_email(session, email)


async def create_customer(session, email, hashed_password):
    return await customers_repository.create(session, email, hashed_password)


async def list_customers(session, with_deleted: bool = False):
    return await customers_repository.list_customers(session, with_deleted)


async def get_customer_by_id(session, customer_id, with_deleted: bool = False):
    return await customers_repository.get_by_id(session, customer_id, with_deleted)


async def update_customer(session, customer, email=None, password_hash=None, type=None):
    if email is not None:
        customer.email = str(email)
    if password_hash is not None:
        customer.password = password_hash
    if type is not None:
        customer.type = type

    return await customers_repository.update(session, customer)


async def soft_delete_customer(session, customer):
    return await customers_repository.soft_delete(session, customer)
