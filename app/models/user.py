from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, uid, address, email, firstname, lastname, balance, isSeller):
        self.uid = uid
        self.address = address
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.isSeller = isSeller

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, uid, email, firstname, lastname, address, balance, isSeller
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
RETURNING uid
""",
                                  address=address, email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname)
            uid = rows[0][0]
            return User.get(uid)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(uid):
        rows = app.db.execute("""
SELECT uid, email, firstname, lastname, address, balance, isSeller 
FROM Users
WHERE uid = :uid
""",
                              uid=uid)
        return User(*(rows[0])) if rows else None
