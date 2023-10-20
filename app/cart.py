from flask import render_template
from flask_login import current_user
import datetime
from flask import jsonify

from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart
from .models.lineitem import LineItem

from flask import Blueprint, request
bp = Blueprint('cart', __name__)


@bp.route('/cart', methods=['GET', 'POST'])
def cart():
    #currentUID = current_user.id

    if request.method == 'POST': 
        action_type = request.form.get('action')
        print(action_type)
        if action_type == "delete": #this is not working right now for some reason
            try:
                lineitem_id = request.form.get('lineitem_id')
                LineItem.remove_lineitem(lineitem_id)
            except ValueError: #might have to modify this
                return "Failed"
            
        elif action_type == "updateQuantity": 
            try:
                newQuantity = request.form.get('newQuantity')
                lineitem_id = request.form.get('lineitem_id')
                LineItem.change_quantity(lineitem_id,newQuantity)
            except ValueError: #might have to modify this
                return "Failed"

    # if request.method == 'POST' and request.form.get('action') == "delete":
    #     try:
    #         lineitem_id = request.form.get('lineitem_id')
    #         LineItem.remove_lineitem(lineitem_id)

    #     except ValueError: #might have to modify this
    #         return "Failed"

    # elif request.method == 'POST':
    #     try:
    #         newQuantity = request.form.get('newQuantity')
    #         lineitem_id = request.form.get('lineitem_id')
    #         LineItem.change_quantity(lineitem_id,newQuantity)
    #     except ValueError: #might have to modify this
    #         return "Failed"
    
        
    if current_user.is_authenticated:
        #totalItemCount = Cart.get_unique_item_count(current_user.id)  #this will have to use cart and lineitem
        # return render_template('wishlist.html',
        #                        wishlist=wishlist)
        allItemsInCart = LineItem.get_all_by_cartid(Cart.get_cartID_from_buyerid(current_user.id),False)
        # allNamesOfProducts = []
        # for lineitem in LineItem:
        #     allNamesOfProducts.append(LineItem.get_productName(lineitem.productid))
        updateCartFirst = Cart.update_total_cart_price(Cart.get_cartID_from_buyerid(current_user.id)) #replace 0's with current_user.id
        updateCartQuantity = Cart.update_number_unique_items(Cart.get_cartID_from_buyerid(current_user.id))
        singleCart = Cart.get_cart_from_buyerid(current_user.id)
        return render_template('cart.html', singleCart = singleCart, ItemsInCart=allItemsInCart)
        #return redirect(url_for('cart.cart')) 

    else:
         return jsonify({}), 404

# @bp.route('/buyer-order',methods = ['GET', 'POST'])
    
# @bp.route('/cart/remove/<int:lineid>', methods = ['POST'])
# def cart_remove(lineid):
#     if request.method == 'POST':
#         seller_id = request.form.get('lineitem_id')

#     if current_user.is_authenticated: #also need to check if the item is in the cart
#         LineItem.remove_lineitem(lineid)

#     return render_template('cart.html')
#     #return jsonify([item.__dict__ for item in wishlist])

