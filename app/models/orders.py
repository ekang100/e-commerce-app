from flask import current_app as app


class Orders:
    def __init__(self, orderid, buyerid, entireOrderFulfillmentStatus, tipAmount):
        self.orderid = orderid
        self.buyerid = buyerid
        self.entireOrderFulfillmentStatus = entireOrderFulfillmentStatus
        self.tipAmount = tipAmount



    @staticmethod
    def get_all_orderIDs_by_buyerid(buyerid):
        rows = app.db.execute('''
SELECT orderid, entireOrderFulfillmentStatus, tipAmount
FROM OrdersInProgress
WHERE buyerid = :buyerid
''',
                              buyerid=buyerid)
        return [{"orderid": row[0], "entireOrderFulfillmentStatus": row[1], "tipAmount": row[2]} for row in rows]

    @staticmethod
    def add_order_to_orders_table(buyerid):
                rows = app.db.execute('''
INSERT INTO OrdersInProgress(buyerid, entireOrderFulfillmentStatus)
VALUES (:buyerid, False)
RETURNING orderid
''', 
                              buyerid = buyerid)
                return ((rows[0][0])) if rows is not None else None
    

    @staticmethod
    def update_entireOrderFulfillmentStatus(orderid):
                  rows = app.db.execute('''
UPDATE OrdersInProgress
SET entireOrderFulfillmentStatus = True
WHERE orderid = :orderid
''',
                              orderid=orderid)
                  return None
    
    @staticmethod
    def update_tipAmount(orderid, tipAmount):
                  rows = app.db.execute('''
UPDATE OrdersInProgress
SET tipAmount = :tipAmount
WHERE orderid = :orderid
''',
                              orderid=orderid, tipAmount=tipAmount)
                  return None
    
