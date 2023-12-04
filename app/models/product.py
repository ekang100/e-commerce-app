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
<<<<<<< HEAD
    def get_paginated(available=True, page=1, per_page=10, sort_by=None):
        offset = (page - 1) * per_page
        #if type(sort_by) is str and sort_by == "priceLow":
        #    sort_by_column = "price ASC"
        #elif type(sort_by) is str and sort_by == "priceHigh":
        #    sort_by_column = "price DESC"
        #else:
        #    sort_by_column = None
            
=======
    def get_num_products(rating):
>>>>>>> origin/ellie-productguru
        rows = app.db.execute('''
SELECT COUNT(*)
FROM Products
WHERE avg_rating >= :rating
''', rating=rating)
        total = rows[0][0] if rows else 0
        return total
    
    @staticmethod
    def get_paginated(sort_by_column, page, rating):
        per_page = 10
        offset = (page - 1) * per_page
        rows = app.db.execute(f'''
SELECT productid, name, price, description, category, image_path, available, avg_rating
FROM Products
<<<<<<< HEAD
WHERE available = :available
ORDER BY

    case when :sort_by = 'priceHigh' THEN  price end DESC,
    case when :sort_by = 'priceLow' THEN  price end ASC

LIMIT :per_page
OFFSET :offset
''',
                            available=available, per_page=per_page, offset=offset, sort_by=sort_by)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def search_product(query, page=1,per_page=10, sort_by=None, available=True):
        offset = (page - 1) * per_page
        # implement sort by later
        #if type(sort_by) is str and sort_by.find(';') != -1:
            #sort_by = None
        if type(sort_by) is str and sort_by == "None":
            sort_by = None
        if type(sort_by) is str and sort_by == "Price: Low to High":
            sort_by = "price ASC"
=======
WHERE avg_rating >= :rating
{("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
LIMIT :per_page
OFFSET :offset
''',
                            per_page=per_page, offset=offset, rating=rating)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def search_count(query, rating):
        rows = app.db.execute(f'''
            SELECT COUNT(*)
            FROM Products
            WHERE name LIKE :query OR description LIKE :query AND avg_rating >= :rating
        ''', query='%' + query + '%', rating=rating)
        total = rows[0][0] if rows else 0
        return total
    
    @staticmethod
    def search_product(sort_by_column, query, page, rating, per_page=10):
        offset = (page - 1) * per_page
>>>>>>> origin/ellie-productguru
        try:
            rows = app.db.execute(f'''
                SELECT *
                FROM Products
<<<<<<< HEAD
                WHERE name LIKE :query OR description LIKE :query AND available =: available
                {("ORDER BY " + sort_by) if sort_by is not None else ""}
                LIMIT :per_page
                OFFSET :offset
            ''', query='%' + query + '%', per_page=per_page, offset=offset, sort_by=sort_by, available=available)
=======
                WHERE name LIKE :query OR description LIKE :query AND avg_rating >= :rating
                {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
                LIMIT :per_page
                OFFSET :offset
            ''', query='%' + query + '%', per_page=per_page, offset=offset, rating=rating)
>>>>>>> origin/ellie-productguru
            return rows
        except Exception as e:
            print(str(e))
            return None
        
    @staticmethod
    def category_search_count(category, rating):
        rows = app.db.execute('''
            SELECT COUNT(*)
            FROM Products
            WHERE category LIKE :category AND avg_rating >= :rating
        ''', category='%' + category + '%', rating=rating)
        total = rows[0][0] if rows else 0
        return total
    
    @staticmethod
    def get_categories():
        rows = app.db.execute('''
SELECT DISTINCT category
FROM Products
''',
                            )
        return [str(row) for row in rows]
    
    @staticmethod
    def search_categories(sort_by_column, category, page, rating, per_page=10):
        offset = (page - 1) * per_page
        try:
            rows = app.db.execute(f'''
                SELECT *
                FROM Products
                WHERE category LIKE :category AND avg_rating >= :rating
                {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
                LIMIT :per_page
                OFFSET :offset
            ''', category='%' + category + '%', per_page=per_page, offset=offset, rating=rating)
            return rows
        except Exception as e:
            print(str(e))
<<<<<<< HEAD
            return None
=======
            return None
        
    @staticmethod
    def get_purchases_by_uid(uid, sid):
        rows = app.db.execute('''
SELECT P.productid
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.sellerid = :sid
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
''',
                              uid=uid, sid=sid
                              )
        pid = rows[0][0] if rows else 0
        return pid
>>>>>>> origin/ellie-productguru
