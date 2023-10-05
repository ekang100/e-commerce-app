from flask import Blueprint, render_template, request, jsonify
from .models.seller import Seller

bp = Blueprint('sellers', __name__)

@bp.route('/sellers/', methods=['GET', 'POST'])
def get_seller_inventory():
    if request.method == 'POST':
        seller_id = request.form.get('seller_id')

        if seller_id is not None:
            seller_id = int(seller_id)
            seller = Seller(seller_id)

            if seller:  # if seller exists
                # Use the get_products method to retrieve products in the seller's inventory
                inventory = seller.get_products()

                if inventory:
                    return render_template('inventory.html', inventory=inventory, seller=seller)
                else:
                    return jsonify({"message": "Seller's inventory is empty"}), 404
            else:
                return jsonify({"message": "Seller not found"}), 404
        else:
            return jsonify({"message": "Seller ID is missing in the form data"}), 400  # Return a 400 Bad Request response if 'seller_id' is missing

    return render_template('your_template.html')  # For handling GET requests, display the form
