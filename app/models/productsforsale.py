from flask import current_app as app

class ProductsForSale:
    def __init__(self, productid, uid, quantity):
        self.productid = productid
        self.uid = uid
        self.quantity = quantity

    @staticmethod
    def get_quantity(productid, uid):
        rows = app.db.execute('''
SELECT quantity
FROM ProductsForSale
WHERE productid = :productid AND uid = :uid
''',
                             productid = productid, uid = uid )
        return ((rows[0][0])) if rows is not None else None
    

    @staticmethod
    def update_quantity(productid, uid, quantity):
                rows = app.db.execute('''
UPDATE ProductsForSale
SET quantity = :quantity
WHERE productid = :productid AND uid = :uid
''', 
                              productid = productid, uid = uid, quantity = quantity)
                return None
    
    # get list of sellers to display for a given product
    @staticmethod
    def get_all_sellers_for_product(pid):
        rows = app.db.execute(f'''
           SELECT ProductsForSale.productid AS productid, Products.name AS name, Products.price as price, quantity, ProductsForSale.uid AS sid, Users.firstname AS seller_firstname, Users.lastname AS seller_lastname
           FROM ProductsForSale, Products, Users
           WHERE ProductsForSale.productid = Products.productid AND Users.id = ProductsForSale.uid
           AND ProductsForSale.productid={pid}
           ORDER BY price ASC
           ''')
        return rows


