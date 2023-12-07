import re
from app.models.product import Product
from .models.seller import Seller
from flask import render_template, redirect, url_for, request, session
from flask import Blueprint
from flask_login import current_user

bp = Blueprint('sellers', __name__)

@bp.route('/sellers_inventory/<int:seller_id>')
def get_seller_inventory(seller_id):
    seller = Seller(seller_id)
    inventory = seller.get_products_for_sale()  # Use the get_products_for_sale method
    categories = Product.get_categories() # get categories to display in dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories
    if inventory:
        # Handle the case when the user has inventory
        return render_template('inventory.html', inventory=inventory, categories=clean_text)
    else:
        return '''
            <script>
                alert("You Don't Have Anything in Your Inventory Yet!");
                window.history.back();  // Redirect back to the previous page or handle as needed
            </script>
        '''

@bp.route('/fulfilled_order_history/<int:seller_id>')
def get_fulfilled_order_history(seller_id):
    seller = Seller(seller_id)
    order_history = seller.get_fulfilledOrder_history()  # Use the get_fulfilledOrder_history method
    if order_history:
        # Handle the case when there's fulfilled order history
        return render_template('fulfilled_order_history.html', order_history=order_history)
    else:
        return '''
            <script>
                alert("No Orders to Fulfill Yet!");
                window.history.back();  // Redirect back to the previous page or handle as needed
            </script>
        '''

    
@bp.route('/unfulfilled_order_history/<int:seller_id>')
def get_unfulfilled_order_history(seller_id):
    seller = Seller(seller_id)
    order_history = seller.get_unfulfilledOrder_history()  # Use the get_fulfilledOrder_history method
    categories = Product.get_categories() # get categories to display in dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories
    if order_history:
        # Handle the case when there's fulfilled order history
        new_sale_flag = session.pop('new_sale_flag', False)  # Pop the flag and default to False if not present
        return render_template('unfulfilled_order_history.html', categories=clean_text, order_history=order_history, new_sale_flag=new_sale_flag)
    else:
        # Use JavaScript alert for the message
        return '''
            <script>
                alert("No Unfulfilled Orders Yet!");
                window.history.back();  // Redirect back to the previous page or handle as needed
            </script>
        '''
    
@bp.route('/make_new_product', methods=['GET', 'POST'])
def make_new_product():
    categories = Product.get_categories() # get categories to display in dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories
    if request.method == 'POST':
        # Get the product details from the form
        name = request.form.get('name')
        price = float(request.form.get('price'))
        description = request.form.get('description')
        category = request.form.get('category')
        image_path = request.form.get('image_path')
        quantity=request.form.get('quantity')
        

        # Assume current_user is provided by Flask-Login
        seller_id = current_user.id

        # Create a Seller object to add the product to the inventory
        seller = Seller(seller_id)

        # Call the add_product method with the form data
        seller.make_new_product(name, price, description, category, quantity, image_path)

        return redirect(url_for('sellers.get_seller_inventory', categories=clean_text, seller_id=seller_id))

    return render_template('make_new_product.html', categories=clean_text)

@bp.route('/add_existing_product', methods=['GET', 'POST'])
def add_existing_product():
    categories = Product.get_categories() # get categories to display in dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories

    seller_id = current_user.id
    # Create a Seller object to get all products
    seller = Seller(seller_id)

    products = seller.get_all_products()

    if request.method == 'POST':

        quantity = request.form.get('quantity')
        productid = request.form.get('product_id')

        seller.add_existing_product(productid, quantity)

        return redirect(url_for('sellers.get_seller_inventory', seller_id=seller_id))

    return render_template('add_existing_product.html', categories=clean_text, products = products)

@bp.route('/modify_product_quantity/<int:product_id>', methods=['GET', 'POST'])
def modify_product_quantity(product_id):
    categories = Product.get_categories() # get categories to display in dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories

    seller_id = current_user.id
    seller = Seller(seller_id)


    # Get the new quantity from the form
    new_quantity = int(request.form.get('new_quantity'))

    # Modify the product quantity
    result = seller.modify_product_quantity(product_id, new_quantity)

    return redirect(url_for('sellers.get_seller_inventory', categories=clean_text, seller_id=seller_id))


@bp.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    categories = Product.get_categories() # get categories to display in dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to remove the product from the inventory
    seller = Seller(seller_id)

    # Remove the product
    result = seller.remove_product(product_id)

    # Redirect back to the inventory page
    return redirect(url_for('sellers.get_seller_inventory', catgegories=clean_text, seller_id=seller_id))


@bp.route('/mark_fulfilled/<int:line_item_id>', methods=['POST'])
def mark_line_item_fulfilled(line_item_id):
    categories = Product.get_categories() # get categories to display in dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Print the line_item_id for debugging purposes
    print("Received line_item_id:", line_item_id)

    # Create a Seller object to mark a line item as fulfilled
    seller = Seller(seller_id)
    result = seller.mark_line_item_fulfilled(line_item_id)

    order_history = seller.get_unfulfilledOrder_history()  # Use the get_fulfilledOrder_history method
    return render_template('unfulfilled_order_history.html', categories=clean_text, order_history=order_history)