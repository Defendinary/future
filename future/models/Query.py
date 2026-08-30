

class Query:
    def __init__(self, model):
        self.model = model
        self.wheres = []
        self.orders = []
        self.limit_value = None

    def where(self, column, *args):
        if len(args) == 1:
            operator, value = "=", args[0]
        else:
            operator, value = args[0], args[1]
        self.wheres.append((column, operator, value))
        return self

    def order_by(self, column, direction="asc"):
        self.orders.append((column, direction))
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    async def get(self):
        return await (await self.model.connection()).get(self.model, self.wheres, limit=self.limit_value, orders=self.orders)

    async def first(self):
        results = await (await self.model.connection()).get(self.model, self.wheres, limit=1, orders=self.orders)
        return results[0] if results else None

    def __repr__(self):
        return "<Query; call .get() or .first() to execute>"

    def __len__(self):
        raise TypeError("Query has no len(); call .get() or .first() first")

    def __iter__(self):
        raise TypeError("Query is not iterable; call .get() or .first() first")
