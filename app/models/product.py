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
    def get_num_products(rating):
        rows = app.db.execute('''
SELECT COUNT(*)
FROM Products
WHERE avg_rating >= :rating
''', rating=rating)
        total = rows[0][0] if rows else 0
        return total
    
    @staticmethod
    def get_num_products_avail(rating, available):
        rows = app.db.execute('''
SELECT COUNT(*)
FROM Products
WHERE avg_rating >= :rating
AND available =:available
''', rating=rating, available=available)
        total = rows[0][0] if rows else 0
        return total

    
    @staticmethod
    def get_paginated(sort_by_column, page, rating):
        per_page = 10
        offset = (page - 1) * per_page
        if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE Products.avg_rating >= :rating
                    GROUP BY Products.productid
                    ORDER BY avg_rating {sort_by_column}, total_quantity {sort_by_column}
                    LIMIT :per_page
                    OFFSET :offset
                ''', per_page=per_page, offset=offset, rating=rating)
                return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7], "total_sales": row[8]} for row in rows]
        else:
            rows = app.db.execute(f'''
        SELECT productid, name, price, description, category, image_path, available, avg_rating
        FROM Products
        WHERE avg_rating >= :rating
        {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
        LIMIT :per_page
        OFFSET :offset
        ''',
                                per_page=per_page, offset=offset, rating=rating)
            return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7]} for row in rows]
    
    @staticmethod
    def get_paginated_avail(sort_by_column, page, rating, available):
        per_page = 10
        offset = (page - 1) * per_page
        if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE Products.avg_rating >= :rating
                    AND available =:available
                    GROUP BY Products.productid
                    ORDER BY avg_rating {sort_by_column}, total_quantity {sort_by_column}
                    LIMIT :per_page
                    OFFSET :offset
                ''', per_page=per_page, offset=offset, rating=rating, available=available)
                return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7], "total_sales": row[8]} for row in rows]
        else:
            rows = app.db.execute(f'''
        SELECT productid, name, price, description, category, image_path, available, avg_rating
        FROM Products
        WHERE avg_rating >= :rating
        AND available =:available
        {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
        LIMIT :per_page
        OFFSET :offset
        ''',
                                per_page=per_page, offset=offset, rating=rating, available=available)
            return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7]} for row in rows]


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
        try:
            if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE (Products.name LIKE :query OR Products.description LIKE :query)
                    AND Products.avg_rating >= :rating
                    GROUP BY Products.productid
                    ORDER BY avg_rating {sort_by_column}, total_quantity {sort_by_column}
                    LIMIT :per_page
                    OFFSET :offset
                ''', query='%' + query + '%', per_page=per_page, offset=offset, rating=rating)
            else:
                rows = app.db.execute(f'''
                    SELECT *
                    FROM Products
                    WHERE name LIKE :query OR description LIKE :query AND avg_rating >= :rating
                    {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
                    LIMIT :per_page
                    OFFSET :offset
                ''', query='%' + query + '%', per_page=per_page, offset=offset, rating=rating)
            return rows
        except Exception as e:
            print(str(e))
            return None
    
    @staticmethod
    def search_count_avail(query, rating, available):
        rows = app.db.execute(f'''
            SELECT COUNT(*)
            FROM Products
            WHERE name LIKE :query OR description LIKE :query AND avg_rating >= :rating AND available=:available
        ''', query='%' + query + '%', rating=rating, available=available)
        total = rows[0][0] if rows else 0
        return total
    
    @staticmethod
    def search_product_avail(sort_by_column, query, page, rating, available, per_page=10):
        offset = (page - 1) * per_page
        try:
            if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE (Products.name LIKE :query OR Products.description LIKE :query)
                    AND Products.avg_rating >= :rating
                    AND available =:available
                    GROUP BY Products.productid
                    ORDER BY avg_rating {sort_by_column}, total_quantity {sort_by_column}
                    LIMIT :per_page
                    OFFSET :offset
                ''', query='%' + query + '%', per_page=per_page, offset=offset, rating=rating, available=available)
            else:
                rows = app.db.execute(f'''
                    SELECT *
                    FROM Products
                    WHERE name LIKE :query OR description LIKE :query AND avg_rating >= :rating AND available =:available
                    {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
                    LIMIT :per_page
                    OFFSET :offset
                ''', query='%' + query + '%', per_page=per_page, offset=offset, rating=rating, available=available)
            return rows
        except Exception as e:
            print(str(e))
            return None
        
    @staticmethod
    def count_total_sales(productid):
        rows = app.db.execute('''
                            SELECT productid, SUM(quantity) AS total_sales
                            FROM LineItem
                            WHERE buyStatus = TRUE AND productid=:productid
                            GROUP BY productid''', productid=productid)
        total = rows[0][0] if rows else 0
        return total
        
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
            if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE Products.category LIKE :category
                    AND Products.avg_rating >= :rating
                    GROUP BY Products.productid
                    ORDER BY avg_rating {sort_by_column}, total_quantity {sort_by_column}
                    LIMIT :per_page
                    OFFSET :offset
                ''', category='%' + category + '%', per_page=per_page, offset=offset, rating=rating)
            else:
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
