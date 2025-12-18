class CustomerService:
    def __init__(self):
        pass

    async def find_customer_by_email(self, uow, session, email):
        return await uow.customers_repository.find_by_email(session, email)


    async def create_customer(self, uow, session, email, hashed_password):
        return await uow.customers_repository.create(session, email, hashed_password)


    async def list_customers(self, uow, session, with_deleted: bool = False):
        return await uow.customers_repository.list_customers(session, with_deleted)


    async def get_customer_by_id(self, uow, session, customer_id, with_deleted: bool = False):
        return await uow.customers_repository.get_by_id(session, customer_id, with_deleted)


    async def update_customer(self, uow, session, customer, email=None, password_hash=None, type=None):
        if email is not None:
            customer.email = str(email)
        if password_hash is not None:
            customer.password = password_hash
        if type is not None:
            customer.type = type

        return await uow.customers_repository.update(session, customer)


    async def soft_delete_customer(self, uow, session, customer):
        return await uow.customers_repository.soft_delete(session, customer)
