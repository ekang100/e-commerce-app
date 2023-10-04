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
