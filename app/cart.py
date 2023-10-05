from flask import render_template
from flask_login import current_user
import datetime
from flask import jsonify

from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart
from .models.lineitem import LineItem

from flask import Blueprint
bp = Blueprint('cart', __name__)


@bp.route('/cart')
def cart():
    #currentUID = current_user.id
    if current_user.is_authenticated:
        #totalItemCount = Cart.get_unique_item_count(current_user.id)  #this will have to use cart and lineitem
        # return render_template('wishlist.html',
        #                        wishlist=wishlist)
        allItemsInCart = LineItem.get_all_by_cartid_not_fulfilled(Cart.get_cartID_from_buyerid(current_user.id),False)
        updateCartFirst = Cart.update_total_cart_price(Cart.get_cartID_from_buyerid(current_user.id)) #replace 0's with current_user.id
        singleCart = Cart.get_cartID_from_buyerid(current_user.id)
        return render_template('cart.html', singleCart = singleCart, ItemsInCart=allItemsInCart)
        #return redirect(url_for('cart.cart')) 

    else:
         return jsonify({}), 404

    #return jsonify([item.__dict__ for item in wishlist])

