from flask import current_app as app


class Product:
    def __init__(self, productid, name, price, description, category, image_path, available, avg_rating, seller_id):
        self.productid = productid
        self.name = name
        self.price = price
        self.description = description
        self.category = category
        self.image_path = image_path
        self.available = available
        self.avg_rating = avg_rating
        self.seller_id = seller_id

    @staticmethod
    def get(productid):
        rows = app.db.execute('''
SELECT productid, name, price, description, category, image_path, available, avg_rating, seller_id
FROM Products
WHERE productid = :productid
''',
                              productid=productid)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT productid, name, price, description, category, image_path, available, avg_rating, seller_id
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_paginated(available=True, page=1, per_page=10):
        offset = (page - 1) * per_page
        rows = app.db.execute('''
SELECT productid, name, price, description, category, image_path, available, avg_rating, seller_id
FROM Products
WHERE available = :available
LIMIT :per_page
OFFSET :offset
''',
                            available=available, per_page=per_page, offset=offset)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def search(query: str, sort_by=None):
        # implement sort by later
        if type(sort_by) is str and sort_by.find(';') != -1:
            sort_by = None
        rows = app.db.execute('''
            SELECT productid, name, price, description, category, image_path, available, avg_rating, seller_id
            FROM Products
            WHERE Products.name LIKE :query OR Products.description LIKE :query
            {("ORDER BY " + sort_by) if sort_by is not None else ""};
        ''', query='%' + query + '%')
        return [Product(*row) for row in rows]
