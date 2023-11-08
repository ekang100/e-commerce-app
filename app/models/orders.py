from flask import current_app as app


class Orders:
    def __init__(self, orderid, buyerid):
        self.orderid = orderid
        self.buyerid = buyerid


    @staticmethod
    def get_all_orderIDs_by_buyerid(buyerid):
        rows = app.db.execute('''
SELECT orderid
FROM OrdersInProgress
WHERE buyerid = :buyerid
''',
                              buyerid=buyerid)
        return [row[0] for row in rows]