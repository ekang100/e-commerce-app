from flask import current_app as app


class ProductReview:
    def __init__(self, productid, uid, rating, comments, date):
        self.productid = productid
        self.uid = uid
        self.rating = rating
        self.comments = comments
        self.date = date

    @staticmethod
    def get(productid, uid):
        rows = app.db.execute('''
SELECT productid, uid, rating, comments, date
FROM ProductReviews
WHERE productid = :productid AND uid = :uid
''',
                              productid=productid,
                              uid=uid)
        return ProductReview(*(rows[0])) if rows else None

    @staticmethod
    def get_most_recent_by_uid(uid, limit=5):
        rows = app.db.execute('''
SELECT productid, uid, rating, comments, date
FROM ProductReviews
WHERE uid = :uid
ORDER BY date DESC
LIMIT :limit
''',
                              uid=uid,
                              limit=limit)
        return [ProductReview(*row) for row in rows]
