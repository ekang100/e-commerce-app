from flask import current_app as app


class LineItem:
    def __init__(self, lineid, cartid, productid, quantities, unitPrice, status, date):
        self.lineid = lineid
        self.cartid = cartid
        self.productid = productid
        self.quantities = quantities
        self.unitPrice = unitPrice
        self.status = status
        self.date = date


    @staticmethod
    def get(lineid):
        rows = app.db.execute('''
SELECT lineid, cartid, productid, quantities, unitPrice, status, date
FROM LineItem
WHERE lineid = :lineid
''',
                              lineid=lineid)
        return LineItem(*(rows[0])) if rows else None


    @staticmethod
    def get_all_by_cartid_not_fulfilled(cartid, status=False):
        rows = app.db.execute('''
SELECT cartid, lineid,productid, quantities, unitPrice, status, date
FROM LineItem
WHERE cartid = :cartid
AND status = :status
''',
                              cartid=cartid,
                              status=status)
        return [LineItem(*row) for row in rows]


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
    def get_all_by_cartid(cartid,status = False):
        rows = app.db.execute('''
SELECT  P.name, unitPrice, quantities
FROM LineItem, Products P
WHERE P.productid = LineItem.productid
AND LineItem.cartid = :cartid
''',
                              cartid=cartid)
        return [{"name": row[0], "price": row[1], "quantities": row[2]} for row in rows]