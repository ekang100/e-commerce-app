from flask import current_app as app


class Product:
    def __init__(self, productid, name, price, available):
        self.productid = productid
        self.name = name
        self.price = price
        self.available = available

    @staticmethod
    def get(productid):
        rows = app.db.execute('''
SELECT productid, name, price, available
FROM Products
WHERE productid = :productid
''',
                              productid=productid)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT productid, name, price, available
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
