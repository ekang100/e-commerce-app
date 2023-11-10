from flask import current_app as app


class LineItem:
    def __init__(self, lineid, cartid, productid, quantities, unitPrice, buyStatus, fulfilledStatus, time_purchased, time_fulfilled, orderid, sellerid):
        self.lineid = lineid
        self.cartid = cartid
        self.productid = productid
        self.quantities = quantities
        self.unitPrice = unitPrice
        self.buyStatus = buyStatus
        self.fulfilledStatus = fulfilledStatus
        self.time_purchased = time_purchased
        self.time_fulfilled = time_fulfilled
        self.orderid = orderid
        self.sellerid = sellerid


    @staticmethod
    def get(lineid):
        rows = app.db.execute('''
SELECT *
FROM LineItem
WHERE lineid = :lineid
''',
                              lineid=lineid)
        return LineItem(*(rows[0])) if rows else None


#     @staticmethod
#     def get_all_by_cartid_not_bought(cartid, status=False):
#         rows = app.db.execute('''
# SELECT cartid, lineid,productid, quantities, unitPrice, status, date
# FROM LineItem
# WHERE cartid = :cartid
# AND status = :status
# ''',
#                               cartid=cartid,
#                               status=status)
#         return [LineItem(*row) for row in rows]


    @staticmethod
    def get_productName(productid):
        rows = app.db.execute('''
SELECT name
FROM Products
WHERE productid = :productid
''',
                              productid=productid)
        return ((rows[0])) if rows is not None else None
    
    @staticmethod
    def get_all_by_cartid_not_bought(cartid,buyStatus = False):
        rows = app.db.execute('''
SELECT P.name, unitPrice, quantities,  LineItem.lineid, LineItem.orderid, LineItem.fulfilledStatus
FROM LineItem, Products P
WHERE P.productid = LineItem.productid
AND LineItem.cartid = :cartid
AND LineItem.buyStatus = False
''',
                              cartid=cartid)
        return [{"name": row[0], "price": row[1], "quantities": row[2], "lineid":row[3]} for row in rows]

    @staticmethod
    def get_all_by_cartid_bought(cartid,buyStatus = True):
        rows = app.db.execute('''
SELECT P.name, unitPrice, quantities,  LineItem.lineid, LineItem.orderid, fulfilledStatus
FROM LineItem, Products P
WHERE P.productid = LineItem.productid
AND LineItem.cartid = :cartid
AND LineItem.buyStatus = :buyStatus
''',
                              cartid=cartid, buyStatus = buyStatus)
        return [{"name": row[0], "price": row[1], "quantities": row[2], "lineid":row[3], "orderid":row[4], "fulfilledStatus":row[5]} for row in rows]
    



    @staticmethod
    def remove_lineitem(lineid): 
        rows = app.db.execute('''
DELETE FROM LineItem 
WHERE lineid = :lineid 
''',
            lineid = lineid)
        return None
    
    @staticmethod
    def change_quantity(lineid, newquantity):
        rows = app.db.execute('''
UPDATE LineItem 
SET quantities = :newquantity
WHERE lineid = :lineid 
''',
            newquantity = newquantity,
            lineid = lineid)
        return None


#this is new
    @staticmethod
    def get_all_lineitems_by_orderid(orderid):
                rows = app.db.execute('''
SELECT *
FROM LineItem
WHERE LineItem.orderid := orderid
''',
            orderid=orderid) 
                return LineItem(*(rows[0])) if rows else None