from flask import current_app as app
from .product import Product
from .user import User


class Seller:

    def __init__(self, uid):
        self.uid = uid
    
        
    def get_user(self):
        # Implement a SQL query to retrieve the user's profile based on the user's ID
        rows = app.db.execute('''
            SELECT id, address, email, firstname, lastname, balance, isSeller
            FROM Users
            WHERE id = :user_id
        ''',
        user_id=self.uid)

        if rows:
            # Assuming you have a User class or a dictionary to represent a user's profile
            # Here, we're using a dictionary
            user_data = rows[0]  # Access the first (and only) row in the list

            user_profile = {
                "id": user_data[0],
                "address": user_data[1],
                "email": user_data[2],
                "firstname": user_data[3],
                "lastname": user_data[4],
                "balance": user_data[5],
                "isSeller": user_data[6]
            }

            return user_profile
        else:
            return None
        
    # Gets the products by the seller of interest (self) -- beta version
    def get_products(self):
        rows = app.db.execute('''
            SELECT p.name, p.description, p.price
            FROM Products p
            WHERE p.seller_id = :seller_id
        ''', seller_id=self.uid)

        return [Product(*row) for row in rows]


#gets the products for sale by the seller of interest (self)
    # def get_products_for_sale(self):
    #     rows = app.db.execute('''
    #     SELECT s.quantity, p.productid, p.name, p.price, p.description
    #     FROM ProductsForSale s
    #     JOIN Products p ON s.productid = p.productid
    #     WHERE p.seller_id = :seller_id
    # ''',
    #     seller_id=self.uid)

    #     return [Product(*row) for row in rows]


