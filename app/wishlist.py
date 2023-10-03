from flask import render_template
from flask_login import current_user
from flask import jsonify
import datetime

from .models.wishlist import Wishlist
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)
from flask import redirect, url_for


@bp.route('/wishlist')
def index():
    # get all available products for sale:
    # products = Product.get_all(True)
    # find the products current user has in wishlist:
    if current_user.is_authenticated:
        wishes = Wishlist.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        return jsonify({}), 404
    # render the page by adding information to the index.html file
    return jsonify([item.__dict__ for item in wishes])

@bp.route('/wishlist/add/<int:product_id>', methods=['POST'])
def wishlist_add(product_id):
    Wishlist.add(current_user.id, product_id, datetime.datetime(2023, 10, 1, 0, 0, 0))
    return redirect(url_for('wishlist.wishlist'))

