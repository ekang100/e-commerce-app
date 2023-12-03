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

    #gets the products for sale by the seller of interest (self)
    def get_products_for_sale(self):
        rows = app.db.execute('''
        SELECT s.quantity, p.productid, p.name, p.price, p.description
        FROM ProductsForSale s
        JOIN Products p ON s.productid = p.productid
        WHERE s.uid = :seller_id
    ''',
        seller_id=self.uid)

        products = [
        {
            'quantity': row[0],
            'productid': row[1],
            'name': row[2],
            'price': row[3],
            'description': row[4]
        }
        for row in rows
    ]
        return products
    
    def modify_product_quantity(self, product_id, new_quantity):
    # Modify the product quantity in the inventory
        app.db.execute('''
            UPDATE ProductsForSale
            SET quantity = :new_quantity
            WHERE productid = :product_id AND uid = :seller_id
        ''', new_quantity=new_quantity, product_id=product_id, seller_id=self.uid)

    def remove_product(self, product_id):
        app.db.execute('''
                    DELETE FROM ProductsForSale
                    WHERE productid = :product_id
            ''', product_id=product_id)
        

        # Now delete the product from Products table
        app.db.execute('''
            DELETE FROM Products
            WHERE productid = :product_id
        ''', product_id=product_id)

    def add_product(self, name, price, description, category, quantity, image_path=None, available=False, avg_rating=0):
        # Insert the new product into the Products table
        app.db.execute('''
            INSERT INTO Products (name, price, description, category, image_path, available, avg_rating)
            VALUES (:name, :price, :description, :category, :image_path, :available, :avg_rating)
        ''', name=name, price=price, description=description, category=category, image_path=image_path, available=available, avg_rating=avg_rating)


    def add_to_products_for_sale(self, name, quantity):
        # Get the product_id of the newly inserted product
        result = app.db.execute('''
            SELECT productid
            FROM Products
            WHERE name = :name
        ''', name=name).fetchone()

        print(result)

        product_id = result['productid']
        # Ensure the uid is the id of the current user (seller)
        uid = self.id

        # Insert into ProductsForSale
        app.db.execute('''
            INSERT INTO ProductsForSale (productid, uid, quantity)
            VALUES (:product_id, :uid, :quantity)
        ''', product_id=product_id, uid=uid, quantity=quantity)

        
    def get_fulfilledOrder_history(self):
        # Retrieve the seller's fulfilled order history
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2]
            }
            for row in rows
        ]
        return order_history
    
    def get_unfulfilledOrder_history(self):
        # Retrieve the seller's fulfilled order history
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'itemid': row[3]
            }
            for row in rows
        ]
        return order_history
    
    def mark_line_item_fulfilled(self, line_id):
        # Mark a specific LineItem as fulfilled
        app.db.execute('''
            UPDATE LineItem
            SET fulfilledStatus = TRUE
            WHERE lineid = :line_id 
        ''', line_id=line_id)




