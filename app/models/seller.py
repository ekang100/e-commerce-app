from flask import current_app as app
from flask import session

from datetime import datetime, timedelta

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

    #gets all products sold by all sellers for sellers to view and add in "Add Existing Products"
    def get_all_products(self):
        rows = app.db.execute('''
                            SELECT *
                            FROM Products
                            WHERE productid NOT IN (
                                SELECT p.productid
                                FROM ProductsForSale pfs
                                JOIN Products p ON pfs.productid = p.productid
                                WHERE pfs.uid = :seller_id);
                              ''', seller_id = self.uid)
        products = [
            {   
                'productid': row[0],
                'name': row[1],
                'price': row[2],
                'description': row[3],
                'category': row[4],
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

        # Check if the sum of quantities is greater than 0 for the given product
        result = app.db.execute('''
            SELECT COALESCE(SUM(quantity), 0)
            FROM ProductsForSale
            WHERE productid = :product_id
        ''', product_id=product_id)

        total_quantity = result[0][0]

        if total_quantity > 0:
            app.db.execute('''
                UPDATE Products
                SET available = TRUE
                WHERE productid = :product_id 
            ''', product_id=product_id)
        else:
            app.db.execute('''
                UPDATE Products
                SET available = FALSE
                WHERE productid = :product_id 
            ''', product_id=product_id)

    def remove_product(self, product_id):
        app.db.execute('''
                    DELETE FROM ProductsForSale
                    WHERE productid = :product_id AND uid= :seller_id
            ''', product_id=product_id, seller_id =self.uid)

        #delete in the cart now 
        app.db.execute('''
                    DELETE FROM LineItem
                    WHERE productid = :product_id AND sellerid = :seller_id AND buyStatus = FALSE
            ''', product_id=product_id, seller_id = self.uid)
        
        #update availability
        # Check if the sum of quantities is greater than 0 for the given product
        result = app.db.execute('''
            SELECT COALESCE(SUM(quantity), 0)
            FROM ProductsForSale
            WHERE productid = :product_id
        ''', product_id=product_id)

        total_quantity = result[0][0]

        if total_quantity > 0:
            app.db.execute('''
                UPDATE Products
                SET available = TRUE
                WHERE productid = :product_id 
            ''', product_id=product_id)
        else:
            app.db.execute('''
                UPDATE Products
                SET available = FALSE
                WHERE productid = :product_id 
            ''', product_id=product_id)


    def make_new_product(self, name, price, description, category, quantity, image_path, avg_rating=0):
        # Determine the availability based on the quantity
        quantity = int(quantity)
        available = quantity > 0

        try: 
            # Insert the new product into the Products table
            app.db.execute('''
                INSERT INTO Products (name, price, description, category, image_path, available, avg_rating)
                VALUES (:name, :price, :description, :category, :image_path, :available, :avg_rating)
            ''', name=name, price=price, description=description, category=category, image_path=image_path, available=available, avg_rating=avg_rating)

            # Execute the SELECT query
            result = app.db.execute('''
                SELECT productid
                FROM Products
                WHERE name = :name
            ''', name=name)
            
            # Fetch the first row from the result
            productid = result[0][0]

            # Insert the product into the ProductsForSale table
            app.db.execute('''
                INSERT INTO ProductsForSale (productid, uid, quantity)
                VALUES (:productid, :seller_id, :quantity)
            ''', productid=productid, seller_id=self.uid, quantity=quantity)

            return True
        except: 
            return False

    def add_existing_product(self, productid, quantity):

        # Insert the new product into the ProductsForSale table
        app.db.execute('''
            INSERT INTO ProductsForSale (productid, uid, quantity)
            VALUES (:productid, :seller_id, :quantity)
        ''', productid=productid, seller_id=self.uid, quantity=quantity)

        if int (quantity) > 0: 
            app.db.execute('''
                UPDATE Products
                SET available = TRUE
                WHERE productid = :product_id 
            ''', product_id=productid)


    def get_fulfilledOrder_history(self):
        # Retrieve the seller's fulfilled order history
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]

        return order_history
    
    def order_fulfilledOrder_history_desc(self):
        # Retrieve the seller's fulfilled order history sorted by descending order chronologically 
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]

        return order_history
    
    def order_fulfilledOrder_history_asc(self):
        # Retrieve the seller's fulfilled order history by ascending order chronologically 
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY li.time_purchased ASC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]

        return order_history

    def order_fulfilledOrder_history_quantitiesHL(self):
        # Retrieve the seller's fulfilled order history ordered by descending quantity
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY li.quantities DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]

        return order_history
    
    def order_fulfilledOrder_history_quantitiesLH(self):
        # Retrieve the seller's fulfilled order history  by ascending quantity
        
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY li.quantities ASC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]

        return order_history

    def order_fulfilledOrder_history_pricesLH(self):
        # Retrieve the seller's fulfilled order history by ascending price
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY p.price ASC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]

        return order_history
    
    def order_fulfilledOrder_history_pricesHL(self):
        # Retrieve the seller's fulfilled order history by descending price
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE
            ORDER BY p.price DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]
        return order_history
    
    def get_fulfilledOrder_history_category(self, category):
        # Retrieve the seller's fulfilled order history by the various categories
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = TRUE AND p.category = :category
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid, category = category)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5]
            }
            for row in rows
        ]

        return order_history

    def get_unfulfilledOrder_history(self):
        # Retrieve the seller's unfulfilled order history
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid)

        current_unfulfilled_count = len(rows)

        # Get the previously stored unfulfilled count
        prev_unfulfilled_count = session.get('prev_unfulfilled_count', 0)

        # Compare the current count with the previous count
        if current_unfulfilled_count > prev_unfulfilled_count:
            # Set a session flag indicating a new sale
            session['new_sale_flag'] = True

        # Store the current unfulfilled count for the next comparison
        session['prev_unfulfilled_count'] = current_unfulfilled_count

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
            }
            for row in rows
        
        ]
        return order_history

    def order_unfulfilledOrder_history_desc(self):
        # Retrieve the seller's unfulfilled order history by chronologically descending order
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
            }
            for row in rows
        ]

        return order_history
    
    def order_unfulfilledOrder_history_asc(self):
        # Retrieve the seller's unfulfilled order history by chronologically ascending order
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY li.time_purchased ASC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
            }
            for row in rows
        ]

        return order_history

    def order_unfulfilledOrder_history_quantitiesHL(self):
        # Retrieve the seller's unfulfilled order history by descending quantities
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY li.quantities DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
            }
            for row in rows
        ]

        return order_history
    
    def order_unfulfilledOrder_history_quantitiesLH(self):
        # Retrieve the seller's unfulfilled order history by ascending quantities
        
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY li.quantities ASC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
            }
            for row in rows
        ]

        return order_history

    def order_unfulfilledOrder_history_pricesLH(self):
        # Retrieve the seller's unfulfilled order history by ascending prices
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY p.price ASC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
            }
            for row in rows
        ]

        return order_history
    
    def order_unfulfilledOrder_history_pricesHL(self):
        # Retrieve the seller's unfulfilled order history by descending prices
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE
            ORDER BY p.price DESC;
        ''', seller_id=self.uid)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
            }
            for row in rows
        ]
        return order_history
    
    def get_unfulfilledOrder_history_category(self, category):
        # Retrieve the seller's unfulfilled order history by categories
        rows = app.db.execute('''
            SELECT li.quantities, li.time_purchased, u.address, li.present, p.price, p.category, li.lineid
            FROM LineItem li
            JOIN OrdersInProgress o ON li.orderid = o.orderid
            JOIN Users u ON o.buyerid = u.id
            JOIN Products p ON li.productid = p.productid
            WHERE li.sellerid = :seller_id AND li.fulfilledStatus = FALSE AND p.category = :category
            ORDER BY li.time_purchased DESC;
        ''', seller_id=self.uid, category = category)

        order_history = [
            {
                'quantities': row[0],
                'time_purchased': row[1],
                'address': row[2],
                'present': row[3],
                'price': row[4],
                'category': row[5],
                'itemid': row[6]
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

    



