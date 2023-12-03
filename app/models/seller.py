from flask import current_app as app

#reference the user module for the seller (seller a subset of users)
from .user import User

class Seller:

    def __init__(self, uid):
        self.uid = uid

    def get_products_for_sale(self):
        rows = app.db.execute('''
            SELECT s.quantity, p.productid, p.name, p.price, p.description, p.category, p.available, p.avg_rating
            FROM ProductsForSale s
            JOIN Products p ON s.productid = p.productid
            WHERE s.uid = :seller_id
        ''', seller_id=self.uid)

        products = [
            {
                'quantity': row[0],
                'productid': row[1],
                'name': row[2],
                'price': row[3],
                'description': row[4],
                'category': row[5],
                'available': row[6],
                'avg_rating': row[7]
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

    def add_product(self, name, price, description, category, quantity, image_path, avg_rating=0):
        # Determine the availability based on the quantity
        quantity = int(quantity)
        available = quantity > 0

        # Insert the new product into the Products table
        app.db.execute('''
            INSERT INTO Products (name, price, description, category, image_path, available, avg_rating)
            VALUES (:name, :price, :description, :category, :image_path, :available, :avg_rating)
        ''', name=name, price=price, description=description, category=category, image_path=image_path, available=available, avg_rating=avg_rating)

        

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




