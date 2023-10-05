from flask import current_app as app

class Seller:

    def __init__(self, uid):
        self.uid = uid

    @staticmethod
    def get_products(self):
        rows = app.db.execute('''
SELECT id, name, price, description, category, available, avg_rating, seller_id
FROM Products
WHERE seller_id = :seller_id
''',
                              seller_id=self.uid)
        return [Product(*row) for row in rows]


