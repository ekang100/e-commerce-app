from .models.seller import Seller
from flask import render_template, redirect, url_for, flash, request
from flask import Blueprint
from flask_login import current_user

bp = Blueprint('sellers', __name__)

@bp.route('/sellers_inventory/<int:seller_id>')
def get_seller_inventory(seller_id):
    seller = Seller(seller_id)
    inventory = seller.get_products_for_sale()  # Use the get_products_for_sale method
    if inventory:
        # Handle the case when the user has inventory
        return render_template('inventory.html', inventory=inventory)
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
    if order_history:
        # Handle the case when there's fulfilled order history
        return render_template('unfulfilled_order_history.html', order_history=order_history)
    else:
        # Use JavaScript alert for the message
        return '''
            <script>
                alert("No Unfulfilled Orders Yet!");
                window.history.back();  // Redirect back to the previous page or handle as needed
            </script>
        '''


@bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
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
        result = seller.add_product(name, price, description, category, quantity, image_path)

        return redirect(url_for('sellers.get_seller_inventory', seller_id=seller_id))

    return render_template('add_product.html')

@bp.route('/modify_product_quantity/<int:product_id>', methods=['GET', 'POST'])
def modify_product_quantity(product_id):
    seller_id = current_user.id
    seller = Seller(seller_id)

    if request.method == 'POST':
        # Get the new quantity from the form
        new_quantity = int(request.form.get('new_quantity'))

        # Modify the product quantity
        result = seller.modify_product_quantity(product_id, new_quantity)

        if result:
            flash('Product quantity modified successfully', 'success')
            return redirect(url_for('sellers.get_seller_inventory', seller_id=seller_id))
        else:
            flash('Failed to modify product quantity', 'danger')

    # Redirect back to the inventory page
    return redirect(url_for('sellers.get_seller_inventory', seller_id=seller_id))


@bp.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to remove the product from the inventory
    seller = Seller(seller_id)

    # Remove the product
    result = seller.remove_product(product_id)

    # Redirect back to the inventory page
    return redirect(url_for('sellers.get_seller_inventory', seller_id=seller_id))


@bp.route('/mark_fulfilled/<int:line_item_id>', methods=['POST'])
def mark_line_item_fulfilled(line_item_id):
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Print the line_item_id for debugging purposes
    print("Received line_item_id:", line_item_id)

    # Create a Seller object to mark a line item as fulfilled
    seller = Seller(seller_id)
    result = seller.mark_line_item_fulfilled(line_item_id)

    order_history = seller.get_unfulfilledOrder_history()  # Use the get_fulfilledOrder_history method
    return render_template('unfulfilled_order_history.html', order_history=order_history)