class MockUnitOfWork:
    def __init__(self, urls_repository=None, customers_repository=None):
        self.urls_repository = urls_repository
        self.customers_repository = customers_repository