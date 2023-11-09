from .models.seller import Seller
from flask import jsonify, request, render_template, redirect, url_for
from flask import Blueprint
from flask_login import current_user

bp = Blueprint('sellers', __name__)

@bp.route('/sellers/', methods=['GET', 'POST'])
def get_seller_inventory():
    if request.method == 'POST':
        seller_id = request.form.get('seller_id')

        if seller_id is not None:
            seller_id = int(seller_id)

            # Create a Seller object to retrieve the user and their inventory
            seller = Seller(seller_id)

            # Use the get_user method to retrieve the user's profile
            user = seller.get_user()

            if user:
                if user["isSeller"]:  # Check if the user is a seller based on the retrieved user profile
                    inventory = seller.get_products()  # Use the get_products method from the Seller model

                    if inventory:
                        # Handle the case when the user is a seller and has inventory
                        return render_template('inventory.html', inventory=inventory, seller=user)
                    else:
                        return jsonify({"message": "Seller's inventory is empty"}), 404
                else:
                    return jsonify({"message": "User is not a valid seller"}), 404
            else:
                return jsonify({"message": "Seller not found"}), 404

    return render_template('your_template.html')  # For handling GET requests, display the form

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

@bp.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to edit the product in the inventory
    seller = Seller(seller_id)

    if request.method == 'POST':
        # Get the updated quantity from the form
        new_quantity = int(request.form.get('new_quantity'))

        # Update the product quantity
        result = seller.update_product_quantity(product_id, new_quantity)

        if result:
            return jsonify({"message": "Product quantity updated"}), 200
        else:
            return jsonify({"message": "Failed to update product quantity"}), 400

    # Fetch the product details for rendering the edit form
    product = seller.get_product(product_id)

    if product:
        return render_template('edit_product.html', product=product)
    else:
        return jsonify({"message": "Product not found"}), 404

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

@bp.route('/order_history', methods=['GET'])
def order_history():
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to retrieve the order history
    seller = Seller(seller_id)
    orders = seller.get_order_history()

    return render_template('order_history.html', orders=orders)

@bp.route('/order_summary/<int:order_id>', methods=['GET'])
def order_summary(order_id):
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to retrieve the order summary
    seller = Seller(seller_id)
    order_summary = seller.get_order_summary(order_id)

    if order_summary:
        return render_template('order_summary.html', order_summary=order_summary)
    else:
        return jsonify({"message": "Order not found"}), 404

@bp.route('/mark_fulfilled/<int:order_id>/<int:line_item_id>', methods=['POST'])
def mark_line_item_fulfilled(order_id, line_item_id):
    # Assume current_user is provided by Flask-Login
    seller_id = current_user.id

    # Create a Seller object to mark a line item as fulfilled
    seller = Seller(seller_id)
    result = seller.mark_line_item_fulfilled(order_id, line_item_id)

    if result:
        return jsonify({"message": "Line item marked as fulfilled"}), 200
    else:
        return jsonify({"message": "Failed to mark line item as fulfilled"}), 400