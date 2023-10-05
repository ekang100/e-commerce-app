from flask import current_app as app


class SellerReview:
    def __init__(self, sellerid, uid, rating, comments, date):
        self.sellerid = sellerid
        self.uid = uid
        self.rating = rating
        self.comments = comments
        self.date = date

    @staticmethod
    def get(sellerid, uid):
        rows = app.db.execute('''
SELECT sellerid, uid, rating, comments, date
FROM SellerReviews
WHERE sellerid = :sellerid AND uid = :uid
''',
                              sellerid=sellerid,
                              uid=uid)
        return SellerReview(*(rows[0])) if rows else None

    @staticmethod
    def get_most_recent_by_uid(uid, limit=5):
        rows = app.db.execute('''
SELECT sellerid, uid, rating, comments, date
FROM SellerReviews
WHERE uid = :uid
ORDER BY date DESC
LIMIT :limit
''',
                              uid=uid,
                              limit=limit)
        return [SellerReview(*row) for row in rows]
