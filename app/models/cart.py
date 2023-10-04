from flask import current_app as app


class Cart:
    def __init__(self, buyerid, cartid, uniqueItemCount):
        self.buyerid = buyerid
        self.cartid = cartid
        self.uniqueItemCount = uniqueItemCount

    @staticmethod
    def get_cartID_from_buyerid(buyerid):
        rows = app.db.execute('''
SELECT cartid, buyerid, uniqueItemCount
FROM Cart
WHERE buyerid = :buyerid
''', 
                              buyerid = buyerid)
        return Cart(*(rows[0])) if rows else None
    
    @staticmethod
    def get_unique_item_count(cartid):
        rows = app.db.execute('''
SELECT buyerid, cartid, uniqueItemCount
FROM Cart
WHERE cartid = :cartid
''', 
                              cartid = cartid)
        return Cart(*(rows[0])) if rows else None

    #increase cart size by 1
    @staticmethod
    def incrementCartSize (cartid):
        rows = app.db.execute('''
UPDATE Cart
SET uniqueItemCount  = uniqueItemCount + 1
WHERE cartid = :cartid
''', 
                              cartid=cartid)
        return Cart(*(rows[0])) if rows else None

#also need to create a method that will decrement cart size by 1
