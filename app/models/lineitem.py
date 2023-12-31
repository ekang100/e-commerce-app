from flask import current_app as app


class LineItem:
    def __init__(self, lineid, cartid, productid, quantities, unitPrice, buyStatus, fulfilledStatus, time_purchased, time_fulfilled, orderid, sellerid, present):
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
        self.present = present


    @staticmethod
    def get(lineid):
        rows = app.db.execute('''
SELECT *
FROM LineItem
WHERE lineid = :lineid
''',
                              lineid=lineid)
        return LineItem(*(rows[0])) if rows else None
    
    @staticmethod
    def get_sellerid(lineid):
            rows = app.db.execute('''
SELECT sellerid
FROM LineItem
WHERE lineid = :lineid
''',
                              lineid=lineid)
            return ((rows[0])) if rows is not None else None
    
    @staticmethod
    def get_productid(lineid):
            rows = app.db.execute('''
SELECT productid
FROM LineItem
WHERE lineid = :lineid
''',
                              lineid=lineid)
            return ((rows[0])) if rows is not None else None
    
    @staticmethod
    def get_sellerid(lineid):
            rows = app.db.execute('''
SELECT sellerid
FROM LineItem
WHERE lineid = :lineid
''',
                              lineid=lineid)
            return ((rows[0])) if rows is not None else None
    
    @staticmethod
    def get_productid(lineid):
            rows = app.db.execute('''
SELECT productid
FROM LineItem
WHERE lineid = :lineid
''',
                              lineid=lineid)
            return ((rows[0])) if rows is not None else None
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
    

    #can change ordering if need to, ordered this way so that the tuples dont flip around the cart when quantites are changed
    @staticmethod
    def get_all_by_cartid_not_bought(cartid,buyStatus = False):
        rows = app.db.execute('''
SELECT P.name, unitPrice, quantities,  LineItem.lineid, LineItem.productid, LineItem.sellerid, U.firstname, U.lastname, LineItem.orderid, LineItem.fulfilledStatus, LineItem.present
FROM LineItem, Products P, Users U
WHERE P.productid = LineItem.productid
AND LineItem.cartid = :cartid
AND LineItem.buyStatus = False
AND U.id = LineItem.sellerid
                    
ORDER BY P.name
''',
                              cartid=cartid)
        return [{"name": row[0], "price": row[1], "quantities": row[2], "lineid":row[3], "productid":row[4], "sellerid":row[5], "firstname":row[6],"lastname":row[7], "fulfilledStatus":row[9], "present":row[10]} for row in rows]

    @staticmethod
    def get_all_by_cartid_bought(cartid,buyStatus = True):
        rows = app.db.execute('''
SELECT P.name, unitPrice, quantities,  LineItem.lineid, LineItem.orderid, fulfilledStatus, time_purchased, U.firstname, U.lastname, LineItem.time_fulfilled, LineItem.present, LineItem.productid
FROM LineItem, Products P, Users U
WHERE P.productid = LineItem.productid
AND LineItem.cartid = :cartid
AND LineItem.buyStatus = :buyStatus
AND U.id = LineItem.sellerid
           
ORDER BY orderid DESC
''',
                              cartid=cartid, buyStatus = buyStatus)
        return [{"name": row[0], "price": row[1], "quantities": row[2], "lineid":row[3], "orderid":row[4], "fulfilledStatus":row[5], "time_purchased":row[6], "firstname":row[7], "lastname":row[8], "time_fulfilled":row[9], "present":row[10], "productid": row[11]} for row in rows]
    
    # make a new line item or update if it already exists when adding to cart
    @staticmethod
    def add_to_cart(cart_id, seller_id, qty, product_id, price, present):
        check = app.db.execute('''SELECT cartid FROM Cart WHERE cartid=:cart_id;''', cart_id=cart_id) # does the user have a cart
        if len(check) == 0: # make a new cart
            new_cart_query = f'''INSERT INTO Cart(buyerid, cartid, uniqueItemCount, totalCartPrice)
                                    VALUES (COALESCE((SELECT MAX(id) FROM Users),0), {cart_id}, {0}, {0.00});'''
            rows = app.db.execute(new_cart_query)
        rows = app.db.execute('''SELECT quantities FROM LineItem WHERE sellerid=:seller_id AND productid=:product_id AND cartid=:cart_id AND buyStatus = False;''', seller_id=seller_id, product_id=product_id, cart_id=cart_id)
        if rows is None or len(rows) == 0:
            query = f'''INSERT INTO LineItem(lineid, cartid, productid, quantities, unitPrice, buyStatus, sellerid, present)
                    VALUES (COALESCE((SELECT MAX(lineid)+1 FROM LineItem),0), {cart_id}, {product_id}, {qty}, {price}, False, {seller_id}, {present});'''
            rows = app.db.execute(query)
        else:
            rows = app.db.execute('''UPDATE LineItem
                        SET quantities=:qty + quantities
                        WHERE productid=:product_id AND sellerid=:seller_id AND cartid=:cart_id AND buyStatus = False;''', qty = qty, product_id=product_id, seller_id=seller_id, cart_id=cart_id, present = False)
               

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


    @staticmethod
    def get_all_lineitems_by_orderid(orderid):
                rows = app.db.execute('''
SELECT LineItem.buyStatus, LineItem.fulFilledStatus
FROM LineItem
WHERE LineItem.orderid = :orderid
''',
            orderid=orderid) 
                return [{"buyStatus": row[0], "fulfilledStatus": row[1]} for row in rows]
    
    @staticmethod
    def get_fulfillment_status(lineitemid):
                         rows = app.db.execute('''
SELECT fulfillmentStatus
FROM LineItem
WHERE LineItem.lineitemid = :lineitemid
''',
            lineitemid=lineitemid) 
                         return ((rows[0])) if rows is not None else None


    @staticmethod
    def change_buystatus(lineid):
        rows = app.db.execute('''
UPDATE LineItem 
SET buyStatus = True
WHERE lineid = :lineid 
''',
            lineid = lineid)
        return None

    @staticmethod
    def get_all_productIDs_by_cartID_not_bought(cartid):
        rows = app.db.execute('''
SELECT productid 
FROM LineItem
WHERE cartid = :cartid
AND buyStatus = False 
''',
            cartid = cartid)
        return ((rows[0])) if rows is not None else None
    
    @staticmethod
    def get_sellerid_from_lineid(lineid):
                  rows = app.db.execute('''
SELECT sellerid 
FROM LineItem
WHERE cartid = :cartid
''',
            lineid = lineid)
                  return ((rows[0])) if rows is not None else None


    @staticmethod 
    def update_time_purchased_from_lineid(lineid):
        rows = app.db.execute('''
UPDATE LineItem 
SET time_purchased = current_timestamp AT TIME ZONE 'UTC'
WHERE lineid = :lineid 
''',
            lineid = lineid)
        return None
           

    @staticmethod
    def update_lineitem_orderid(lineid, orderid):
                   rows = app.db.execute('''
UPDATE LineItem 
SET orderid = :orderid
WHERE lineid = :lineid 
''',
            lineid = lineid, orderid = orderid)
                   return None
    

    @staticmethod
    def update_gift(lineid, present):
        rows = app.db.execute('''
UPDATE LineItem 
SET present = :present
WHERE lineid = :lineid 
''',
            present = present,
            lineid = lineid)
        return None