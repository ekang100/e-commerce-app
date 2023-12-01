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
SELECT P.name, L.quantities, P.price, L.time_purchased, L.fulfilledStatus, P.category
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.time_purchased >= :since
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
ORDER BY L.time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [{"name": row[0], "quantities": row[1], "price": row[2], "time_purchased": row[3], "fulfilledStatus": row[4], "category": row[5]} for row in rows]

    @staticmethod
    def get_all_by_uid_since_asc(uid, since):
        rows = app.db.execute('''
SELECT P.name, L.quantities, P.price, L.time_purchased, L.fulfilledStatus, P.category
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.time_purchased >= :since
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
ORDER BY L.time_purchased ASC
''',
                              uid=uid,
                              since=since)
        return [{"name": row[0], "quantities": row[1], "price": row[2], "time_purchased": row[3], "fulfilledStatus": row[4], "category": row[5]} for row in rows]

    @staticmethod
    def get_all_by_uid_since_quantities(uid, since):
        rows = app.db.execute('''
SELECT P.name, L.quantities, P.price, L.time_purchased, L.fulfilledStatus, P.category
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.time_purchased >= :since
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
ORDER BY L.quantities DESC
''',
                              uid=uid,
                              since=since)
        return [{"name": row[0], "quantities": row[1], "price": row[2], "time_purchased": row[3], "fulfilledStatus": row[4], "category": row[5]} for row in rows]
    
    @staticmethod
    def get_all_by_uid_since_price_hl(uid, since):
        rows = app.db.execute('''
SELECT P.name, L.quantities, P.price, L.time_purchased, L.fulfilledStatus, P.category
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.time_purchased >= :since
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
ORDER BY L.quantities * P.price DESC
''',
                              uid=uid,
                              since=since)
        return [{"name": row[0], "quantities": row[1], "price": row[2], "time_purchased": row[3], "fulfilledStatus": row[4], "category": row[5]} for row in rows]

    @staticmethod
    def get_all_by_uid_since_price_lh(uid, since):
        rows = app.db.execute('''
SELECT P.name, L.quantities, P.price, L.time_purchased, L.fulfilledStatus, P.category
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.time_purchased >= :since
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
ORDER BY L.quantities * P.price ASC
''',
                              uid=uid,
                              since=since)
        return [{"name": row[0], "quantities": row[1], "price": row[2], "time_purchased": row[3], "fulfilledStatus": row[4], "category": row[5]} for row in rows]

    @staticmethod
    def get_all_by_uid_since_category(uid, since, category):
        rows = app.db.execute('''
SELECT P.name, L.quantities, P.price, L.time_purchased, L.fulfilledStatus, P.category
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.time_purchased >= :since
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
AND P.category = :category
ORDER BY L.time_purchased DESC
''',
                              uid=uid,
                              since=since,
                              category=category)
        return [{"name": row[0], "quantities": row[1], "price": row[2], "time_purchased": row[3], "fulfilledStatus": row[4], "category": row[5]} for row in rows]

    @staticmethod
    def get_all_by_uid_price_since(uid, since):
        rows = app.db.execute('''
SELECT P.price
FROM Cart C, Products P, LineItem L
WHERE C.buyerid = :uid
AND L.time_purchased >= :since
AND C.cartid = L.cartid
AND L.buyStatus = TRUE
AND L.productid = P.productid
ORDER BY L.time_purchased DESC
''',
                              uid=uid,
                              since=since)
        return [{"price": row[0]} for row in rows]