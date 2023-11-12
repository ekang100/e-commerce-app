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
