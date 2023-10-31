from flask import current_app as app


class Purchase:
    def __init__(self, id, uid, pid, time_purchased):
        self.id = id
        self.uid = uid
        self.pid = pid
        self.time_purchased = time_purchased

    @staticmethod
    def get(id):
        rows = app.db.execute('''
SELECT id, uid, pid, time_purchased
FROM Purchases
WHERE id = :id
''',
                              id=id)
        return Purchase(*(rows[0])) if rows else None

    @staticmethod
    def get_all_by_uid_since(uid, since):
        rows = app.db.execute('''
SELECT P.name, L.quantities, P.price, Pu.time_purchased, L.fulfilledStatus
FROM Purchases Pu, Products P, LineItem L
WHERE Pu.uid = :uid
AND Pu.time_purchased >= :since
AND Pu.lineid = L.lineid
AND L.productid = P.productid
ORDER BY Pu.time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [{"name": row[0], "quantities": row[1], "price": row[2], "time_purchased": row[3], "fulfilledStatus": row[4]} for row in rows]
