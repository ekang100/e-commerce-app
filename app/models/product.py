from flask import current_app as app


class Product:
    def __init__(self, productid, name, price, description, category, image_path, available, avg_rating):
        self.productid = productid
        self.name = name
        self.price = price
        self.description = description
        self.category = category
        self.image_path = image_path
        self.available = available
        self.avg_rating = avg_rating
        #self.seller_id = seller_id

    @staticmethod
    def get(productid):
        rows = app.db.execute('''
SELECT productid, name, price, description, category, image_path, available, avg_rating
FROM Products
WHERE productid = :productid
''',
                              productid=productid)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT productid, name, price, description, category, image_path, available, avg_rating
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_num_products(available=True):
        rows = app.db.execute('''
SELECT COUNT(*)
FROM Products
WHERE available=:available''', available=available)
        total = rows[0][0] if rows else 0
        return total
    
    @staticmethod
    def get_paginated(sort_by, page, available=True):
        per_page = 10
        offset = (page - 1) * per_page
        if type(sort_by) is str and sort_by == "priceLow":
            sort_by_column = "price ASC"
        elif type(sort_by) is str and sort_by == "priceHigh":
            sort_by_column = "price DESC"
        else:
            sort_by_column = None
            
        rows = app.db.execute(f'''
SELECT productid, name, price, description, category, image_path, available, avg_rating
FROM Products
WHERE available = :available
{("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
LIMIT :per_page
OFFSET :offset
''',
                            available=available, per_page=per_page, offset=offset)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def search_count(query):
        rows = app.db.execute(f'''
            SELECT COUNT(*)
            FROM Products
            WHERE name LIKE :query OR description LIKE :query
        ''', query='%' + query + '%')
        total = rows[0][0] if rows else 0
        return total
    
    @staticmethod
    def search_product(query, page, per_page=10):
        offset = (page - 1) * per_page
        # implement sort by later
        #if type(sort_by) is str and sort_by.find(';') != -1:
            #sort_by = None
        #if type(sort_by) is str and sort_by == "None":
        #    sort_by = None
        #if type(sort_by) is str and sort_by == "Price: Low to High":
        #    sort_by = "price ASC"
        try:
            rows = app.db.execute(f'''
                SELECT *
                FROM Products
                WHERE name LIKE :query OR description LIKE :query
                LIMIT :per_page
                OFFSET :offset
            ''', query='%' + query + '%', per_page=per_page, offset=offset)
            return rows
        except Exception as e:
            print(str(e))
            return None
    
    @staticmethod
    def get_categories(available=True):
        rows = app.db.execute('''
SELECT DISTINCT category
FROM Products
WHERE available = :available
''',
                            available=available)
        return [str(row) for row in rows]
    
    @staticmethod
    def search_categories(category, page=1, per_page=10):
        offset = (page - 1) * per_page
        # implement sort by later
        #if type(sort_by) is str and sort_by.find(';') != -1:
            #sort_by = None
        try:
            rows = app.db.execute('''
                SELECT *
                FROM Products
                WHERE category LIKE :category
                LIMIT :per_page
                OFFSET :offset
            ''', category='%' + category + '%', per_page=per_page, offset=offset)
            return rows
        except Exception as e:
            print(str(e))
            return None