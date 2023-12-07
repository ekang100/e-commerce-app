from flask import render_template
from flask_login import current_user
import datetime
from flask import jsonify
from decimal import Decimal
import re

from .models.user import User
from .models.product import Product
from .models.purchase import Purchase
from .models.cart import Cart
from .models.lineitem import LineItem
from .models.orders import Orders
from .models.productsforsale import ProductsForSale
from .models.productsforsale import ProductsForSale

from flask import Blueprint, request
bp = Blueprint('cart', __name__)


@bp.route('/cart', methods=['GET', 'POST'])
def cart():
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]

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
        
        elif request.form['action'] == 'add':
            # ADD TO CART!!
            seller_id = request.form['seller_id']
            product_id = request.form['product_id']
            qty = request.form['qty']
            price = request.form['price']
            LineItem.add_to_cart(current_user.id, seller_id, qty, product_id, price, False)

        elif action_type == "gift":
            new_status = True
            if request.form['current_gift_status'] == 'True':
                new_status = False            
            LineItem.update_gift(request.form['lineitem_id'], new_status)

            
            
        
    if current_user.is_authenticated:

        # allItemsInCart = LineItem.get_all_by_cartid_not_bought(Cart.get_cartID_from_buyerid(current_user.id),False)
        allItemsInCart = LineItem.get_all_by_cartid_not_bought(current_user.id)

        updateCartFirst = Cart.update_total_cart_price(Cart.get_cartID_from_buyerid(current_user.id)) #replace 0's with current_user.id
        
        print(allItemsInCart)
                                #verified additional part
        moneySaved = 0.00
        if User.get(current_user.id).isVerified:
            print('this user is verified so they get a discount')
                            #this bottom part needs to change to update it correctly
            moneySaved = round(float(Cart.get_total_cartprice(current_user.id))*0.1,2)
            updateCartFirst = Cart.update_total_cart_price_if_verified(Cart.get_cartID_from_buyerid(current_user.id))
                        
        updateCartQuantity = Cart.update_number_unique_items(Cart.get_cartID_from_buyerid(current_user.id))
        singleCart = Cart.get_cart_from_buyerid(current_user.id)
        return render_template('cart.html', singleCart = singleCart, ItemsInCart=allItemsInCart, ErrorMessageCheck = False, isVerified = User.get(current_user.id).isVerified, moneySaved = moneySaved, categories=clean_text)
    else:
         return jsonify({}), 404
    

@bp.route('/buyer-order',methods = ['GET', 'POST'])
def buyerOrder():
    if current_user.is_authenticated:
        # allOrderIDs = Orders.get_all_orderIDs_by_buyerid(current_user.id)
        # print(allOrderIDs)
        # # this will be correct later

        # lineitems = [] 
        # for order in allOrderIDs:
        #     lineitems.append(LineItem.get_all_lineitems_by_orderid(order))

        categories = Product.get_categories() # get categories to display in dropdown
        clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories

        #post for submitting entire cart
        if request.method == 'POST': 
                action_type = request.form.get('action')
                print(action_type) #this is implemented for testing

                errorMessageString = ''


                if action_type == "order_all":

                    tip = request.form.get('tipPercentage')
                    print ('tip', tip)
                    # tip = round(float(tip),2)

                    #need to error check if they put in a negative without clicking 'add tip'
                    if(float(tip)<0 or float(tip) != round(float(tip),2)):
                        allItemsInCart = LineItem.get_all_by_cartid_not_bought(Cart.get_cartID_from_buyerid(current_user.id),False)
                        updateCartFirst = Cart.update_total_cart_price(Cart.get_cartID_from_buyerid(current_user.id)) #replace 0's with current_user.id
                        
                        #verified additional part
                        moneySaved = 0.00
                        if User.get(current_user.id).isVerified:
                            print('this user is verified so they get a discount')
                            #this bottom part needs to change to update it correctly
                            moneySaved = round(float(Cart.get_total_cartprice(current_user.id))*0.1,2)
                            updateCartFirst = Cart.update_total_cart_price_if_verified(Cart.get_cartID_from_buyerid(current_user.id))
                        
                        updateCartQuantity = Cart.update_number_unique_items(Cart.get_cartID_from_buyerid(current_user.id))
                        singleCart = Cart.get_cart_from_buyerid(current_user.id)
                        print(errorMessageString)
                        can_order = True
                        errorMessageString = 'Please input a valid dollar tip amount.'
                        return render_template('cart.html', categories=clean_text, singleCart = singleCart, ItemsInCart=allItemsInCart, ErrorMessageCheck = True, errorMessageString = errorMessageString, isVerified = User.get(current_user.id).isVerified, moneySaved = moneySaved)
                        

                    can_order = True
            #do all checking code here
            # check available balances and inventories
            # update inventories and balances at time of submission
            # The buyer’s balance will be decremented, and the sellers’ balances will be incremented and inventories decremented.
            # cart becomes empty

                    #1) check available balances
                    if User.get_balance(current_user.id) < Cart.get_total_cartprice(current_user.id) + Decimal(round(float(tip))):
                        can_order = False
                        errorMessageString = 'You do not have enough money!!!! Check your total cart price and tip amount.'
                        # print('User too poor to order')
                        # print('User too poor to order')
                
#            #2) need to check available inventories
                    # allProductIDsinCart = LineItem.get_all_productIDs_by_cartID_not_bought(current_user.id)
                    # for productID in allProductIDsinCart:
                    #     if LineItem.get_sellerid_from_lineid()
                    #!!!!!!!!this here has to be a schema where its like get all productIDs by cartID that are not bought
                    else:
                        lineitemsincart = LineItem.get_all_by_cartid_not_bought(current_user.id)
                        invalidItems = []
                        for lineitem in lineitemsincart:
                            lineitem_pid = lineitem["productid"]
                            lineitem_sellerid= lineitem["sellerid"]
                            lineitem_quantityDemanded = lineitem["quantities"]
                            lineitem_name = lineitem["name"]
                            if ProductsForSale.get_quantity(lineitem_pid, lineitem_sellerid) < lineitem_quantityDemanded:
                                can_order = False
                                invalidItems.append(lineitem_name)
                        if not can_order:
                            errorMessageString = 'Not enough inventory for '
                            i = 1
                            for itemName in invalidItems:
                                if len(invalidItems) ==1:
                                    errorMessageString = errorMessageString + itemName + '.'
                                elif i != len(invalidItems):
                                   errorMessageString = errorMessageString + itemName + ', '
                                elif i == len(invalidItems):
                                    errorMessageString = errorMessageString + 'and ' + itemName + '.'
                                i +=1
                        # print(errorMessageString)

                #if constraints haven't been met
                    if can_order == False:
                        allItemsInCart = LineItem.get_all_by_cartid_not_bought(Cart.get_cartID_from_buyerid(current_user.id),False)
                        updateCartFirst = Cart.update_total_cart_price(Cart.get_cartID_from_buyerid(current_user.id)) #replace 0's with current_user.id
                        
                        #verified additional part
                        moneySaved = 0.00
                        if User.get(current_user.id).isVerified:
                            print('this user is verified so they get a discount')
                            #this bottom part needs to change to update it correctly
                            moneySaved = round(float(Cart.get_total_cartprice(current_user.id))*0.1,2)
                            updateCartFirst = Cart.update_total_cart_price_if_verified(Cart.get_cartID_from_buyerid(current_user.id))
                        
                        updateCartQuantity = Cart.update_number_unique_items(Cart.get_cartID_from_buyerid(current_user.id))
                        singleCart = Cart.get_cart_from_buyerid(current_user.id)
                        print(errorMessageString)
                        can_order = True
                        return render_template('cart.html', categories=clean_text, singleCart = singleCart, ItemsInCart=allItemsInCart, ErrorMessageCheck = True, errorMessageString = errorMessageString, isVerified = User.get(current_user.id).isVerified, moneySaved = moneySaved)
                
                #if constraints have been met
                    else:
                        #decrement balance
                        print ('before', User.get_balance(current_user.id))
                        User.add_balance(current_user.id, (User.get_balance(current_user.id)-Cart.get_total_cartprice(current_user.id) - Decimal(round(float(tip),2)))) #this decrements own balance
                        print ('after', User.get_balance(current_user.id))

                        #generate orderid
                        new_orderid = Orders.add_order_to_orders_table(current_user.id)
                        Orders.update_tipAmount(new_orderid, round(float(tip),2))
                        print(new_orderid)
                        #adds the balance to the seller
                        #need to decrement inventory
                        #change the status of buyStatus
                        
                        allItemsInCart = LineItem.get_all_by_cartid_not_bought(current_user.id)
                        for lineitem in allItemsInCart:
                            lineitem_id = lineitem["lineid"]
                            lineitem_sellerid = lineitem["sellerid"]
                            lineitem_quantityDemanded = lineitem["quantities"]
                            lineitem_unitprice = lineitem["price"]
                            lineitem_pid = lineitem["productid"]
                            #changes status of buyStatus
                            LineItem.change_buystatus(lineitem_id)

                            #adds balance to seller
                            User.add_balance(lineitem_sellerid, (User.get_balance(lineitem_sellerid) + lineitem_unitprice*lineitem_quantityDemanded))
                            
                            #decrements inventory
                            ProductsForSale.update_quantity(lineitem_pid, lineitem_sellerid, ProductsForSale.get_quantity(lineitem_pid, lineitem_sellerid) - lineitem_quantityDemanded)
                            
                            #updates time_purchased
                            LineItem.update_time_purchased_from_lineid(lineitem_id)

                            #assign orderid to the lineitems
                            LineItem.update_lineitem_orderid(lineitem_id, new_orderid)

                        #for order checking:
                        # 1) find an unused order id
                        # 2) assign to all the lineitems here in the cart
                        # 3) insert into orders table the necessary information                            
                            # print(new_orderid)

                        #need to update time of buyStauts
                        #need to assign an ordernumber and add to orders
                        #change the status of fulfillmentStatus?
                        #make sure cart is cleared
                        print('order submitted')


        allItemsBought = LineItem.get_all_by_cartid_bought(Cart.get_cartID_from_buyerid(current_user.id),True)
        
        allOrdersByUser = Orders.get_all_orderIDs_by_buyerid(current_user.id)

        #will update whether an entire order has been fulfilled
        #this hasn't been tested yet
        for order in allOrdersByUser:
            orderID = order["orderid"]
            allFulfilled = True
            lineItemsForEachOrderID = LineItem.get_all_lineitems_by_orderid(orderID)
            for lineitem in lineItemsForEachOrderID:
                if not lineitem["fulfilledStatus"]:
                    allFulfilled = False
            if allFulfilled:
                Orders.update_entireOrderFulfillmentStatus(orderID)
         
         #update availability for ellie's additional feature
        for lineitem in allItemsBought:
            all_sellers_for_product = ProductsForSale.get_all_sellers_for_product(int(lineitem['productid']))
            available = False
            for seller in all_sellers_for_product:
                if(ProductsForSale.get_quantity(int(lineitem['productid']), seller['sid']) != 0):
                    available = True
            
            if(not available):
                Product.update_availability(lineitem['productid'], False)
                print ("availability changed")


        allOrdersByUser = Orders.get_all_orderIDs_by_buyerid(current_user.id)


        return render_template('buyer-order.html', categories=clean_text, allItemsBought = allItemsBought, allOrdersByUser = allOrdersByUser)
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
