from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login

from .product import Product

#All user attributes
class User(UserMixin):
    def __init__(self, id, address, email, firstname, lastname, balance, isSeller, isVerified, verifiedDate, bio, avatar):
        self.id = id
        self.address = address
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.isSeller = isSeller
        self.isVerified = isVerified
        self.verifiedDate = verifiedDate
        self.bio = bio
        self.avatar = avatar

#If user authenticated, return all user attributes
    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, address, balance, isSeller, isVerified, verifiedDate, bio, avatar
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

#verify that an account email exists
    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

#Register an account
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

#Update databased for name and address
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

# Update unique email
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

# Rehash and update password
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

# update database to add balance (make sure it is added to current balance in users function)
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
        
    #Used in cart for checkign constraints
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

#Method to become a seller --> changed isSeller to true for a user
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

#Method to become verified --> changed isVerified to true for a user and stores time of verification
# to determine how much money saved since verification
    @staticmethod
    def verify_account(user_id):
        try:
            app.db.execute("""
                UPDATE Users
                SET isVerified = TRUE
                WHERE id = :user_id
            """, user_id=user_id)
            app.db.execute("""
                UPDATE Users
                SET verifiedDate = current_timestamp AT TIME ZONE 'UTC'
                WHERE id = :user_id
            """, user_id=user_id)
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None
        
    # get all products given user id who is a seller
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
        WHERE s.uid = :seller_id
    ''',
        seller_id=self.id)

        
        # Return a list of tuples with the selected values
        products = [
        {
            'quantity': row[0],
            'name': row[2],
            'price': row[3],
            'description': row[4]
        }
        for row in rows
    ]
        return products
        
    #Load all attributes for a user who just logged in    
    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
    SELECT id, address, email, firstname, lastname, balance, isSeller, isVerified, verifiedDate, bio, avatar
    FROM Users
    WHERE id = :id
    """,
                              id=id)
        return User(*(rows[0])) if rows else None

    #Search for any user (combined first and last name together)
    #Can handle any upper or lowercase
    @staticmethod
    def search_user(name):
        try:
            results = app.db.execute("""
                SELECT *
                FROM PubProfile
                WHERE LOWER(name) LIKE LOWER(:name)
            """, name='%' + name + '%')
            return results
        except Exception as e:
            print(str(e))
            return None

    #Load all attributes to display on a users public profile
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

    #Update or change user bio for a given user account
    @staticmethod
    def bio(user_id, bio):
        try:
            app.db.execute("""
                UPDATE Users
                SET bio = :bio
                WHERE id = :user_id
            """, user_id=user_id, bio=bio)
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None
    
    #Update or change user avatar for a given user account
    @staticmethod
    def change_avatar(user_id, avatar):
        try:
            app.db.execute("""
                UPDATE Users
                SET avatar = :avatar
                WHERE id = :user_id
            """, user_id=user_id, avatar=avatar)
            return User.get(user_id)
        except Exception as e:
            print(str(e))
            return None