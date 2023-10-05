from flask import Blueprint, jsonify, request
from .models.seller import Seller

bp = Blueprint('seller', __name__)

@bp.route('/', methods=['GET', 'POST'])
def getSellerInventory():
    if request.method == 'POST':
        seller_id = int(request.form['id'])

        seller = Seller(seller_id)

        if seller:  # if seller exists
            # Use the get_products method to retrieve products in the seller's inventory
            inventory = seller.get_products()

            if inventory:
                # Convert inventory data to a list of dictionaries
                inventory_data = [{"name": item.name, "price": item.price, "category": item.category, "availability": item.available, "rating": item.avg_rating} for item in inventory]
                return render_template('sellerProducts.html', inventory=inventory, seller=seller)
            else:
                return jsonify({"message": "Seller's inventory is empty"}), 404
        else:
            return jsonify({"message": "Seller not found"}), 404
    else:
        return jsonify({"message": "Seller ID is missing in the form data"}), 400  # Return a 400 Bad Request response if 'id' is missing
