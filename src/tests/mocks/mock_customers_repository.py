from datetime import datetime, timezone


class MockCustomerRepository:
    def __init__(self):
        self.customers = {}
        self._id_seq = 1

    async def find_by_email(self, email):
        return next(
            (
                c for c in self.customers.values()
                if c["email"] == email and c["deleted_at"] is None
            ),
            None,
        )

    async def create(self, email, password):
        customer = {
            "id": self._id_seq,
            "email": str(email),
            "password": password,
            "type": "FREE",
            "deleted_at": None,
            "updated_at": None,
        }
        self.customers[self._id_seq] = customer
        self._id_seq += 1
        return customer

    async def list_customers(self, with_deleted: bool = False):
        if with_deleted:
            return list(self.customers.values())

        return [c for c in self.customers.values() if c["deleted_at"] is None]

    async def get_by_id(self, customer_id, with_deleted: bool = False):
        customer = self.customers.get(customer_id)
        if not customer:
            return None

        if not with_deleted and customer["deleted_at"] is not None:
            return None

        return customer

    async def update(self, customer):
        customer["updated_at"] = datetime.now(timezone.utc)
        return customer

    async def soft_delete(self, customer):
        customer["deleted_at"] = datetime.now(timezone.utc)
        return customer