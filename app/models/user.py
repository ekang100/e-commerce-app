from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login

from .product import Product


class User(UserMixin):
    def __init__(self, id, address, email, firstname, lastname, balance, isSeller):
        self.id = id
        self.address = address
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.isSeller = isSeller

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, address, balance, isSeller
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(address, email, password, firstname, lastname):
        try:
            rows = app.db.execute("""
INSERT INTO Users(address, email, password, firstname, lastname)
VALUES(:address, :email, :password, :firstname, :lastname)
RETURNING id
""",
                                  address=address, email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None
        
    @staticmethod
    def update_name_address(user_id, address, firstname, lastname):
        try:
            app.db.execute("""
                UPDATE Users
                SET address = :address, firstname = :firstname, lastname = :lastname
                WHERE id = :user_id
            """, address=address, firstname=firstname, lastname=lastname, user_id=user_id)
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None
        
    @staticmethod
    def change_email(user_id, email):
        try:
            app.db.execute("""
                UPDATE Users
                SET email = :email
                WHERE id = :user_id
            """, user_id=user_id, email=email)
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None
        
    @staticmethod
    def change_password(user_id, password):
        try:
            app.db.execute("""
                UPDATE Users
                SET password = :password
                WHERE id = :user_id
            """, user_id=user_id, password=generate_password_hash(password))
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None
    
    @staticmethod
    def add_balance(user_id, balance):
        try:
            app.db.execute("""
                UPDATE Users
                SET balance = :balance
                WHERE id = :user_id
            """, user_id=user_id, balance=balance)
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None
        
     #check this with ryan before committing
    #this is used in cart for checkign constraints
    @staticmethod
    def get_balance (id):
        try:
            rows = app.db.execute("""
                SELECT balance
                FROM Users
                WHERE id = :id
            """, id=id)
            return ((rows[0])[0]) if rows else None
        except Exception as e:
            print(str(e))
            return None

    
    @staticmethod
    def become_seller(user_id):
        try:
            app.db.execute("""
                UPDATE Users
                SET isSeller = TRUE
                WHERE id = :user_id
            """, user_id=user_id)
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None
    
    def get_products(self):
        rows = app.db.execute('''
            SELECT p.name, p.description, p.price
            FROM Products p
            WHERE p.seller_id = :seller_id
        ''', seller_id=self.id)

        return [Product(row['name'], row['description'], row['price']) for row in rows]


    #gets the products for sale by the seller of interest (self)
    def get_products_for_sale(self):
        rows = app.db.execute('''
        SELECT s.quantity, p.productid, p.name, p.price, p.description
        FROM ProductsForSale s
        JOIN Products p ON s.productid = p.productid
        WHERE p.seller_id = :seller_id
    ''',
        seller_id=self.id)

        
        products = [Product(*row) for row in rows]
        print(self.id)  # Print the products
        return products
        
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
SELECT id, address, email, firstname, lastname, balance, isSeller
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
    
    # @staticmethod
    # def search_user_firstname(user_to_search):
    #     try:
    #         results = app.db.execute("""
    #             SELECT account_id 
    #             FROM PubProfile
    #             WHERE firstname LIKE :search_query
    #         """, search_query='%' + user_to_search + '%').fetchall()
    #         return results
    #     except Exception as e:
    #         print(str(e))
    #         return None
        
    # @staticmethod
    # def search_user_lastname(user_to_search):
    #     try:
    #         results = app.db.execute("""
    #             SELECT account_id 
    #             FROM PubProfile
    #             WHERE lastname LIKE :search_query
    #         """, search_query='%' + user_to_search + '%').fetchall()
    #         return results
    #     except Exception as e:
    #         print(str(e))
    #         return None
        
    # @staticmethod
    # def search_user(firstname_enter, lastname_enter):
    #     try:
    #         results = app.db.execute("""
    #             SELECT account_id
    #             FROM PubProfile
    #             WHERE firstname LIKE :firstname
    #             AND lastname LIKE :lastname
    #         """, firstname='%' + firstname_enter + '%', lastname='%' + lastname_enter + '%')
    #         return results
    #     except Exception as e:
    #         print(str(e))
    #         return None

    @staticmethod
    def search_user(name):
        try:
            results = app.db.execute("""
                SELECT *
                FROM PubProfile
                WHERE name LIKE :name
            """, name='%' + name + '%')
            return results
        except Exception as e:
            print(str(e))
            return None

    @staticmethod
    def pubprofile_search(account_id):
        try:
            results = app.db.execute("""
                SELECT *
                FROM PubProfile
                WHERE account_id = :account_id
            """, account_id=account_id)
            return results
        except Exception as e:
            print(str(e))
            return None
