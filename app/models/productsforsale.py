from flask import current_app as app

class ProductsForSale:
    def __init__(self, productid, uid, quantity):
        self.productid = productid
        self.uid = uid
        self.quantity = quantity