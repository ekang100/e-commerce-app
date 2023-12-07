from flask import render_template, request, session
from flask_login import current_user
import datetime
import re
import math

from app.models.productsforsale import ProductsForSale

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/', methods=['POST', 'GET'])
def index():

    # get page for pagination
    page = int(request.args.get('page', 1))
    per_page = 10 # can make this adjustable in the future, displays given amount of products on a page

    # get sorting preferences
    sort_by = request.args.get('sort_by', default='None')

    # check sorting preferences to prohibit vulnerability and assign new variable to something more easily passed to a query
    if type(sort_by) is str and sort_by == "priceLow":
        sort_by_column = "price ASC"
    elif type(sort_by) is str and sort_by == "priceHigh":
        sort_by_column = "price DESC"
    elif type(sort_by) is str and sort_by == "popularityLow":
        sort_by_column = "ASC"
    elif type(sort_by) is str and sort_by == "popularityHigh":
        sort_by_column = "DESC"
    else:
        sort_by_column = None
    
    # get ratings preferences
    rating = request.args.get('rating', default=0)
    rate = int(rating)

    # get availability status preferences
    if request.method == 'POST':
        # check if the checkbox was submitted and update in_stock variable
        if 'in_stock' in request.form:
            in_stock = True
        else:
            in_stock = False
    else:
        in_stock = request.args.get('in_stock')

    # if the user only wants to see available products...
    if in_stock:
        available = True
        products = Product.get_paginated_avail(sort_by_column, page, rate, available) # only returns available products
        total = int(Product.get_num_products_avail(rate, available))
    else:
        total = int(Product.get_num_products(rate))
        products = Product.get_paginated(sort_by_column, page, rate) # does not take into account availability status
    
    max_page = int(math.ceil(total / per_page)) # calculate the last page of pagination
    categories = Product.get_categories() # get a list of categories to display in the dropdown
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # remove formatting from category list

    if current_user.is_authenticated:
        buy_again = Product.get_purchases_by_uid(current_user.id)
        product_ids = [product.get("productid") for product in buy_again]
        return render_template('index.html',
                           product_ids=product_ids, rating=rating, avail_products=products, per_page=per_page, page=page, max_page=max_page, categories=clean_text, total=total, sort_by=sort_by, in_stock=in_stock)



    # render the page by adding information to the index.html file
    return render_template('index.html',
                           rating=rating, avail_products=products, per_page=per_page, page=page, max_page=max_page, categories=clean_text, total=total, sort_by=sort_by, in_stock=in_stock)

@bp.route('/account')
def index2():
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
    # find the products current user has bought:
    if current_user.is_authenticated:
        # Get all products depending on how user specifies sorting
        if request.args.get('sort', 'date_desc') is not None:
            sort_order = request.args.get('sort', 'date_desc')
            #sort by descending date
            if sort_order == 'date_desc':
                purchases = Purchase.get_all_by_uid_since(current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0))
            #sort by ascending date
            elif sort_order == 'date_asc':
                purchases = Purchase.get_all_by_uid_since_asc(current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0))
            #sort by quantity
            elif sort_order == 'quantity':
                purchases = Purchase.get_all_by_uid_since_quantities(current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0))
            #sort by price low to high
            elif sort_order == 'priceLow':
                purchases = Purchase.get_all_by_uid_since_price_lh(current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0))
            #sort by price high to low
            elif sort_order == 'priceHigh':
                purchases = Purchase.get_all_by_uid_since_price_hl(current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0))
            #sort by category
            else:
                purchases = Purchase.get_all_by_uid_since_category(current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0), sort_order)
        #default to sort by date descending
        else:
            purchases = Purchase.get_all_by_uid_since(current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0))

        # check if verified and display total saved from verification since verification date
        if current_user.isVerified:
            result = Purchase.get_all_by_uid_price_since(current_user.id, current_user.verifiedDate)
            print(result)
            if len(result) > 0:
                total_saved = sum(item['price'] for item in result)
            else:
                #if nothing bought since verification return 0
                total_saved = 0.00
        else:
            #if not verified return 0
            total_saved = 0.00
    else:
        purchases = None
        total_saved = 0.00
    return render_template('account.html',
                           purchase_history=purchases, total_saved=total_saved, categories=clean_text)