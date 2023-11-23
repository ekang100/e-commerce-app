from .models.seller import Seller
from flask import jsonify, request, render_template, redirect, url_for
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
        return jsonify({"message": "Seller's inventory is empty"}), 404

@bp.route('/fulfilled_order_history/<int:seller_id>')
def get_fulfilled_order_history(seller_id):
    seller = Seller(seller_id)
    order_history = seller.get_fulfilledOrder_history()  # Use the get_fulfilledOrder_history method
    if order_history:
        # Handle the case when there's fulfilled order history
        return render_template('fulfilled_order_history.html', order_history=order_history)
    else:
        return jsonify({"message": "No fulfilled order history for the seller"}), 404
    
@bp.route('/unfulfilled_order_history/<int:seller_id>')
def get_unfulfilled_order_history(seller_id):
    seller = Seller(seller_id)
    order_history = seller.get_unfulfilledOrder_history()  # Use the get_fulfilledOrder_history method
    if order_history:
        # Handle the case when there's fulfilled order history
        return render_template('unfulfilled_order_history.html', order_history=order_history)
    else:
        return jsonify({"message": "No Unfulfillled order history for the seller"}), 404


@bp.route('/add_product', methods=['POST'])
def add_product_to_inventory():
    if request.method == 'POST':
        # Get the product details from the form
        name = request.form.get('name')
        price = float(request.form.get('price'))
        quantity_available = int(request.form.get('quantity_available'))
        description = request.form.get('description')
        category = request.form.get('category')

        # Assume current_user is provided by Flask-Login
        seller_id = current_user.id

        # Create a Seller object to add the product to the inventory
        seller = Seller(seller_id)
        result = seller.add_product(name, price, quantity_available, description, category)

        if result:
            return jsonify({"message": "Product added to inventory"}), 200
        else:
            return jsonify({"message": "Failed to add product"}), 400

@bp.route('/modify_product_quantity/<int:product_id>', methods=['GET', 'POST'])
def modify_product_quantity(product_id):
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to modify the product quantity in the inventory
    seller = Seller(seller_id)

    form = UpdateForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Get the new quantity from the form
        new_quantity = form.new_quantity.data

        # Modify the product quantity
        result = seller.modify_product_quantity(product_id, new_quantity)

        if result:
            flash('Product quantity modified successfully', 'success')
            return redirect(url_for('sellers.get_seller_inventory', seller_id=seller_id))
        else:
            flash('Failed to modify product quantity', 'danger')

    # Render the template for modifying the quantity
    return render_template('modify_quantity.html', title='Modify Quantity', form=form, product_id=product_id)

@bp.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to remove the product from the inventory
    seller = Seller(seller_id)

    # Remove the product
    result = seller.remove_product(product_id)

    if result:
        return jsonify({"message": "Product removed from inventory"}), 200
    else:
        return jsonify({"message": "Failed to remove product"}), 400

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