from flask import current_app as app


class Orders:
    def __init__(self, orderid, buyerid, entireOrderFulfillmentStatus):
        self.orderid = orderid
        self.buyerid = buyerid
        self.entireOrderFulfillmentStatus = entireOrderFulfillmentStatus


    @staticmethod
    def get_all_orderIDs_by_buyerid(buyerid):
        rows = app.db.execute('''
SELECT orderid
FROM OrdersInProgress
WHERE buyerid = :buyerid
''',
                              buyerid=buyerid)
        return [row[0] for row in rows]

    @staticmethod
    def add_order_to_orders_table(buyerid):
                rows = app.db.execute('''
INSERT INTO OrdersInProgress(buyerid, entireOrderFulfillmentStatus)
VALUES (:buyerid, False)
RETURNING orderid
''', 
                              buyerid = buyerid)
                return ((rows[0][0])) if rows is not None else None
    

