from .models.seller import Seller  # Import the Seller model
from flask import jsonify, request, render_template
from flask import Blueprint

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