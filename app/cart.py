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

    if request.method == 'POST': 
        action_type = request.form.get('action')
        print(action_type) #this is implemented for testing

        if action_type == "update": 
            try:
                newQuantity = request.form.get('newQuantity')
                lineitem_id = request.form.get('lineitem_id')
                LineItem.change_quantity(lineitem_id,newQuantity)
            except ValueError: #might have to modify this
                return "Failed"
        
        elif action_type == "delete": 
            try:
                lineitem_id = request.form.get('lineitem_id')
                LineItem.remove_lineitem(lineitem_id)
            except ValueError: #might have to modify this
                return "Failed"
        
        elif action_type == "order_all":
            #do all checking code here
            # check available balances and inventories
            # update inventories and balances at time of submission
            # The buyer’s balance will be decremented, and the sellers’ balances will be incremented and inventories decremented.
            # cart becomes empty
            print('haha')
            
            
        
    if current_user.is_authenticated:

        allItemsInCart = LineItem.get_all_by_cartid_not_bought(Cart.get_cartID_from_buyerid(current_user.id),False)
        updateCartFirst = Cart.update_total_cart_price(Cart.get_cartID_from_buyerid(current_user.id)) #replace 0's with current_user.id
        updateCartQuantity = Cart.update_number_unique_items(Cart.get_cartID_from_buyerid(current_user.id))
        singleCart = Cart.get_cart_from_buyerid(current_user.id)
        return render_template('cart.html', singleCart = singleCart, ItemsInCart=allItemsInCart)
    else:
         return jsonify({}), 404
    

@bp.route('/buyer-order',methods = ['GET', 'POST'])
def buyerOrder():
    if current_user.is_authenticated:
        allItemsBought = LineItem.get_all_by_cartid_bought(Cart.get_cartID_from_buyerid(current_user.id),True)

        return render_template('buyer-order.html')
    else:
        return jsonify({}), 404

        
    
# @bp.route('/cart/remove/<int:lineid>', methods = ['POST'])
# def cart_remove(lineid):
#     if request.method == 'POST':
#         seller_id = request.form.get('lineitem_id')

#     if current_user.is_authenticated: #also need to check if the item is in the cart
#         LineItem.remove_lineitem(lineid)

#     return render_template('cart.html')
#     #return jsonify([item.__dict__ for item in wishlist])