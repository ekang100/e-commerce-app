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

    # all sort_by columns are checked against a dictionary of allowed columns before being passed to the query to prevent injection attacks

    # get product information for a given productid
    @staticmethod
    def get(productid):
        rows = app.db.execute('''
SELECT productid, name, price, description, category, image_path, available, avg_rating
FROM Products
WHERE productid = :productid
''',
                              productid=productid)
        return Product(*(rows[0])) if rows is not None else None

    # get all available products
    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
SELECT productid, name, price, description, category, image_path, available, avg_rating
FROM Products
WHERE available = :available
''',
                              available=available)
        return [Product(*row) for row in rows]
    
    # get the number of products with avg_rating greater than or equal to input
    @staticmethod
    def get_num_products(rating):
        rows = app.db.execute('''
SELECT COUNT(*)
FROM Products
WHERE avg_rating >= :rating
''', rating=rating)
        total = rows[0][0] if rows else 0
        return total
    
    # get number of products with avg_rating greater than or equal to input and depending on available
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

    # get paginated product information with avg_rating greater than or equal to input and sorted by input
    @staticmethod
    def get_paginated(sort_by_column, page, rating):
        per_page = 10
        offset = (page - 1) * per_page
        if sort_by_column == "ASC" or sort_by_column == "DESC": # columns for sorting by popularity, named for ease of use in query
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
    
    # same as above, but take into account availability status
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

    # count how many products are returned by a given search query
    @staticmethod
    def search_count(query, rating):
        rows = app.db.execute(f'''
            SELECT COUNT(*)
            FROM Products
            WHERE (LOWER(name) LIKE LOWER(:query) OR LOWER(description) LIKE LOWER(:query)) AND avg_rating >= :rating
        ''', query='%' + query + '%', rating=rating)
        total = rows[0][0] if rows else 0
        return total
    
    # search for a product given a query, sort and filter as needed
    @staticmethod
    def search_product(sort_by_column, query, page, rating, per_page=10):
        offset = (page - 1) * per_page
        try:
            if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE (LOWER(Products.name) LIKE LOWER(:query) OR LOWER(Products.description) LIKE LOWER(:query))
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
                    WHERE (LOWER(name) LIKE LOWER(:query) OR LOWER(description) LIKE LOWER(:query)) AND avg_rating >= :rating
                    {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
                    LIMIT :per_page
                    OFFSET :offset
                ''', query='%' + query + '%', per_page=per_page, offset=offset, rating=rating)
            return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7]} for row in rows]
        except Exception as e:
            print(str(e))
            return None
    
    # count how many products are returned for a given search query, taking into account availability status
    @staticmethod
    def search_count_avail(query, rating, available):
        rows = app.db.execute(f'''
            SELECT COUNT(*)
            FROM Products
            WHERE (LOWER(name) LIKE LOWER(:query) OR LOWER(description) LIKE LOWER(:query)) AND avg_rating >= :rating AND available =:available
        ''', query='%' + query + '%', rating=rating, available=available)
        total = rows[0][0] if rows else 0
        return total
    
    # search for products that meet a given query, sort and filter as needed, and take into account availability status
    @staticmethod
    def search_product_avail(sort_by_column, query, page, rating, available, per_page=10):
        offset = (page - 1) * per_page
        try:
            if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE (LOWER(Products.name) LIKE LOWER(:query) OR LOWER(Products.description) LIKE LOWER(:query))
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
                    WHERE (LOWER(name) LIKE LOWER(:query) OR LOWER(description) LIKE LOWER(:query)) AND avg_rating >= :rating AND available =:available
                    {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
                    LIMIT :per_page
                    OFFSET :offset
                ''', query='%' + query + '%', per_page=per_page, offset=offset, rating=rating, available=available)
            return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7]} for row in rows]
        except Exception as e:
            print(str(e))
            return None
    
    # count the total sales made (across all sellers) for a given productid
    @staticmethod
    def count_total_sales(productid):
        rows = app.db.execute('''
                            SELECT productid, SUM(quantity) AS total_sales
                            FROM LineItem
                            WHERE buyStatus = TRUE AND productid=:productid
                            GROUP BY productid''', productid=productid)
        total = rows[0][0] if rows else 0
        return total
    
    # count how many products are returned for a certain category
    @staticmethod
    def category_search_count(category, rating):
        rows = app.db.execute('''
            SELECT COUNT(*)
            FROM Products
            WHERE category LIKE :category AND avg_rating >= :rating
        ''', category='%' + category + '%', rating=rating)
        total = rows[0][0] if rows else 0
        return total
    
    # return a list of categories for the dropdown menu
    @staticmethod
    def get_categories():
        rows = app.db.execute('''
SELECT DISTINCT category
FROM Products
''',
                            )
        return [str(row) for row in rows]
    
    # search for products that are in a given category, sort and filter as needed
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
            return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7]} for row in rows]
        except Exception as e:
            print(str(e))
            return None
        
    # count how many products are returned for a certain category, taking into account availability status
    @staticmethod
    def category_search_count_avail(category, rating, available):
        rows = app.db.execute('''
            SELECT COUNT(*)
            FROM Products
            WHERE category LIKE :category AND avg_rating >= :rating AND available =:available
        ''', category='%' + category + '%', rating=rating, available=available)
        total = rows[0][0] if rows else 0
        return total
        
    # search products that are within given category, taking into account availability status - filter and sort as needed
    @staticmethod
    def search_categories_avail(sort_by_column, category, page, rating, available, per_page=10):
        offset = (page - 1) * per_page
        try:
            if sort_by_column == "ASC" or sort_by_column == "DESC":
                rows = app.db.execute(f'''
                    SELECT Products.*, SUM(LineItem.quantities) AS total_quantity
                    FROM Products
                    LEFT JOIN LineItem ON Products.productid = LineItem.productid
                    WHERE Products.category LIKE :category
                    AND Products.avg_rating >= :rating
                    AND available =:available
                    GROUP BY Products.productid
                    ORDER BY avg_rating {sort_by_column}, total_quantity {sort_by_column}
                    LIMIT :per_page
                    OFFSET :offset
                ''', category='%' + category + '%', per_page=per_page, offset=offset, rating=rating, available=available)
            else:
                rows = app.db.execute(f'''
                    SELECT *
                    FROM Products
                    WHERE category LIKE :category AND avg_rating >= :rating AND available =:available
                    {("ORDER BY " + sort_by_column) if sort_by_column is not None else ""}
                    LIMIT :per_page
                    OFFSET :offset
                ''', category='%' + category + '%', per_page=per_page, offset=offset, rating=rating, available=available)
            return [{"productid": row[0], "name": row[1], "price": row[2], "description": row[3], "category": row[4], "image_path": row[5], "available": row[6], "avg_rating": row[7]} for row in rows]
        except Exception as e:
            print(str(e))
            return None
        
    # determine if a user has bought a product before but only display "buy again" if product is in stock
    @staticmethod
    def get_purchases_by_uid(uid, available=True):
        rows = app.db.execute('''
SELECT P.productid
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
AND P.available = :available
''',
                              uid=uid, available=available
                              )
        return [{"productid": row[0]} for row in rows]
    

    # update availability of a product (ex: seller decrements quantity, buyer purchases all of them)
    @staticmethod
    def update_availability(productid, available):
     rows = app.db.execute('''
UPDATE Products
SET available = :available
WHERE productid = :productid
''',
                              productid=productid, available=available)
     return None
    