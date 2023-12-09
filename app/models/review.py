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
    
    @staticmethod
    def insert_product_review(review_type, product_id, seller_id, user_id, rating, comments):
        query = '''
        INSERT INTO Reviews (type, product_id, seller_id, uid, rating, comments, date)
        VALUES (:type, :product_id, :seller_id, :uid, :rating, :comments, CURRENT_TIMESTAMP)
        '''
        app.db.execute(query, 
                    type=review_type, 
                    product_id=product_id, 
                    seller_id=seller_id, 
                    uid=user_id, 
                    rating=rating, 
                    comments=comments)
        
    @staticmethod
    def get_review_by_id(review_id):
        try:
            query = '''
                SELECT R.entity_id, R.type, R.product_id, R.seller_id, R.uid, R.rating, R.comments, R.date
                FROM Reviews R
                WHERE R.entity_id = :review_id
            '''
            rows = app.db.execute(query, review_id=review_id)
            row = rows[0]
            if row:
                return {
                    'id': row[0],
                    'type': row[1],
                    'product_id': row[2],
                    'seller_id': row[3],
                    'uid': row[4],
                    'rating': row[5],
                    'comments': row[6],
                    'date': row[7]
                }
            else:
                return None
        except Exception as e:
            raise ValueError(f"Error fetching review by ID: {str(e)}")


    @staticmethod
    def get_reviews_by_product_id(product_id):
        try:
            query = '''
                SELECT R.entity_id, U.firstname, U.lastname, R.rating, R.comments, R.date, R.uid
                FROM Reviews R
                JOIN Users U ON R.uid = U.id
                WHERE R.product_id = :product_id
                ORDER BY R.date DESC
            '''
            rows = app.db.execute(query, product_id=product_id)

            reviews = [{
                'id': row[0], 
                'name': f"{row[1]} {row[2]}", 
                'rating': row[3], 
                'comments': row[4], 
                'date': row[5],
                'user_id': row[6]
            } for row in rows]
            return reviews
        except Exception as e:
            raise ValueError(f"Error fetching reviews for product: {str(e)}")


    @staticmethod
    def update_review(review_id, new_rating, new_comments):
        try:
            query = '''
            UPDATE Reviews
            SET rating = :new_rating, comments = :new_comments, date = CURRENT_TIMESTAMP
            WHERE entity_id = :review_id
            '''
            print(f"Updating review {review_id} with rating {new_rating} and comments {new_comments}")
            app.db.execute(query, new_rating=new_rating, new_comments=new_comments, review_id=review_id)
        except Exception as e:
            raise ValueError(f"Error updating review: {str(e)}")


    @staticmethod
    def delete_review(review_id):
        try:
            query = 'DELETE FROM Reviews WHERE entity_id = :review_id'
            app.db.execute(query, review_id=review_id)
        except Exception as e:
            raise ValueError(f"Error deleting review: {str(e)}")
        
    @staticmethod
    def get_reviews_by_seller_id(seller_id):
        try:
            query = '''
                SELECT R.entity_id, U.firstname, U.lastname, R.rating, R.comments, R.date, R.uid
                FROM Reviews R
                JOIN Users U ON R.uid = U.id
                WHERE R.seller_id = :seller_id
                ORDER BY R.date DESC
            '''
            rows = app.db.execute(query, seller_id=seller_id)

            reviews = [{
                'id': row[0], 
                'name': f"{row[1]} {row[2]}", 
                'rating': row[3], 
                'comments': row[4], 
                'date': row[5],
                'user_id': row[6]
            } for row in rows]
            return reviews
        except Exception as e:
            raise ValueError(f"Error fetching reviews for seller: {str(e)}")
        
    # Finds the averages and the number of reviews 
    @staticmethod
    def get_product_rating_summary(product_id):
        query = '''
        SELECT AVG(R.rating) AS average_rating, COUNT(R.entity_id) AS number_of_ratings
        FROM Reviews R
        WHERE R.product_id = :product_id
        '''
        result = app.db.execute(query, product_id=product_id)

        if result and result[0] and result[0][0] is not None:
            return {'average_rating': round(result[0][0], 2), 'number_of_ratings': result[0][1]}
        else:
            return {'average_rating': 0, 'number_of_ratings': 0}

    @staticmethod
    def get_seller_rating_summary(seller_id):
        query = '''
            SELECT AVG(R.rating) as average_rating, COUNT(R.rating) as number_of_ratings
            FROM Reviews R
            WHERE R.seller_id = :seller_id
        '''
        result = app.db.execute(query, seller_id=seller_id)
        if result and result[0] and result[0][0] is not None:
            return {'average_rating': round(result[0][0], 2), 'number_of_ratings': result[0][1]}
        else:
            return {'average_rating': 0, 'number_of_ratings': 0}
        

    @staticmethod
    def get_five_star_review_count(seller_id):
        try:
            query = '''
                SELECT COUNT(*)
                FROM Reviews
                WHERE seller_id = :seller_id AND rating = 5
            '''
            result = app.db.execute(query, seller_id=seller_id)
            return result[0] if result else 0
        except Exception as e:
            raise ValueError(f"Error fetching five-star review count: {str(e)}")
        
    @staticmethod
    def get_all_reviews_by_user_id(user_id):
        try:
            query = '''
                SELECT R.entity_id, R.type, COALESCE(P.name, U.firstname || ' ' || U.lastname) AS reviewed_entity,
                       R.rating, R.comments, R.date
                FROM Reviews R
                LEFT JOIN Products P ON R.product_id = P.productid
                LEFT JOIN Users U ON R.seller_id = U.id
                WHERE R.uid = :user_id
                ORDER BY R.date DESC
            '''
            rows = app.db.execute(query, user_id=user_id)

            # Construct a list of review information
            reviews = [{
                'id': row[0],
                'type': row[1],
                'product_or_seller_name': row[2],
                'rating': row[3],
                'comments': row[4],
                'date': row[5]
            } for row in rows]
            return reviews
        except Exception as e:
            raise ValueError(f"Error fetching user reviews: {str(e)}")


    @staticmethod
    def add_vote(review_id, user_id, vote):
        try:
            query = '''
            INSERT INTO ReviewVotes (review_id, user_id, vote)
            VALUES (:review_id, :user_id, :vote)
            ON CONFLICT (review_id, user_id) DO UPDATE
            SET vote = EXCLUDED.vote;
            '''
            app.db.execute(query, review_id=review_id, user_id=user_id, vote=vote)
        except Exception as e:
            raise ValueError(f"Error adding vote: {str(e)}")

    @staticmethod
    def get_votes_by_review_id(review_id):
        try:
            query = '''
            SELECT COUNT(*) FROM ReviewVotes
            WHERE review_id = :review_id AND vote = TRUE;
            '''
            result = app.db.execute(query, review_id=review_id)
            return result[0][0] if result else 0
        except Exception as e:
            raise ValueError(f"Error fetching votes: {str(e)}")
    
    
    @staticmethod
    def check_review_exists(review_type, product_id, seller_id, user_id):
        try:
            if review_type == 'product':
                query = "SELECT COUNT(*) FROM Reviews WHERE product_id = :product_id AND uid = :uid"
                result = app.db.execute(query, product_id=product_id, uid=user_id)
            else:  # 'seller'
                query = "SELECT COUNT(*) FROM Reviews WHERE seller_id = :seller_id AND uid = :uid"
                result = app.db.execute(query, seller_id=seller_id, uid=user_id)

            return result[0][0] > 0
        except Exception as e:
            raise ValueError(f"Error checking existing review: {str(e)}")

