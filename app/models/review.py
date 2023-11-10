from datetime import datetime
from flask import current_app as app


class Reviews:
    def __init__(self, type, entity_name, uid, rating, comments, date):
        self.type = type
        self.entity_name = entity_name
        self.uid = uid
        self.rating = rating
        self.comments = comments
        self.date = date


    @staticmethod
    def get_most_recent_by_uid(uid):
        rows = app.db.execute('''
SELECT R.type,
       CASE 
           WHEN R.type = 'product' THEN (SELECT name FROM Products WHERE productid = R.entity_id)
           WHEN R.type = 'seller' THEN (SELECT firstname || ' ' || lastname FROM Users WHERE id = R.seller_id)
       END as entity_name,
       R.uid, R.rating, R.comments, R.date
FROM Reviews R
WHERE R.uid = :uid
ORDER BY R.date DESC
''',
                              uid=uid)
        if not rows:
            raise ValueError(f"No reviews found for user_id: {uid}")
        return [Reviews(type=row[0], 
                        entity_name=row[1], 
                        uid=row[2], 
                        rating=row[3], 
                        comments=row[4], 
                        date=row[5]) for row in rows]

# class Reviews:
#     def __init__(self, type, entity_id, uid, rating, comments, date):
#         self.type = type  # 'product' or 'seller'
#         self.entity_id = entity_id  # either productid or sellerid
#         self.uid = uid
#         self.rating = rating
#         self.comments = comments
#         self.date = date

#     @staticmethod
#     def get(type, entity_id, uid):
#         try:
#             rows = app.db.execute('''
# SELECT type, entity_id, uid, rating, comments, date
# FROM Reviews
# WHERE type = :type AND entity_id = :entity_id AND uid = :uid
# ''',
#                                   type=type,
#                                   entity_id=entity_id,
#                                   uid=uid)
#             return Reviews(*(rows[0])) if rows else None
#         except Exception as e:
#             # You can log the error here for further debugging
#             raise ValueError(f"Error fetching review: {str(e)}") from e
        
#     @staticmethod
#     def get_most_recent_by_uid(uid, limit=5):
#             rows = app.db.execute('''
#     SELECT type, entity_id, uid, rating, comments, date
#     FROM Reviews
#     WHERE uid = :uid
#     ORDER BY date DESC
#     LIMIT :limit
#     ''',
#                                 uid=uid,
#                                 limit=limit)
#             if not rows:
#                 raise ValueError(f"No reviews found for user_id: {uid}")
#             return [Reviews(*row) for row in rows]
    
#     @staticmethod
#     def post_review(type, entity_id, uid, rating, comments):
#         try:
#             # Check if the review already exists for the user
#             existing_review = Reviews.get(type, entity_id, uid)
#             if existing_review:
#                 return "You have already reviewed this item."

#             # Construct the SQL query based on the review type
#             params = {
#                 'product_id': entity_id if type == 'product' else None,
#                 'seller_id': entity_id if type == 'seller' else None,
#                 'uid': uid,
#                 'type': type,
#                 'rating': rating,
#                 'comments': comments,
#                 'date': datetime.now()
#             }

#             query = '''
# INSERT INTO Reviews (product_id, seller_id, uid, type, rating, comments, date)
# VALUES (:product_id, :seller_id, :uid, :type, :rating, :comments, :date)
# '''

#             app.db.execute(query, **params)

#             return "Review posted successfully."
#         except Exception as e:
#             raise ValueError(f"Error posting review: {str(e)}") from e