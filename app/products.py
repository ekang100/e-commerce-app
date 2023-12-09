from flask import Flask, request, jsonify, Blueprint, render_template
from flask_login import login_user, logout_user, current_user
import re
# from flask_paginate import Pagination
bp = Blueprint('products', __name__)

from .models.product import Product
from .models.productsforsale import ProductsForSale
from .models.review import Reviews

# for the repeated process of checking and reassigning sorting preferences before passing to query. preventing injection attacks
def sort_assignment(sort_by):
    allowed_sort_columns = {
        "priceLow": "price ASC",
        "priceHigh": "price DESC",
        "popularityLow": "ASC",
        "popularityHigh": "DESC"
    }
    
    return allowed_sort_columns.get(sort_by, None)

# search product based on matches in name or description
@bp.route('/search_product_results', methods=['GET', 'POST'])
def search_keywords():
    try: # an original search
        query = request.form['query']
    except: # for maintaining the search query throughout pagination
        query = request.args.get('query')
    page = int(request.args.get('page', 1))
    per_page = 10
    # get sorting preferences
    sort_by = request.args.get('sort_by', default='None')

    # get ratings preferences
    rating = request.args.get('rating', default=0)

    rate = int(rating)

    # check sorting preferences to prohibit vulnerability and assign new variable to something more easily passed to a query
    sort_by_column = sort_assignment(sort_by)
  
    # an old method that I wanted to keep in here just in case...
    #if request.method == 'POST':
        # Check if the checkbox was submitted and update the in_stock variable accordingly
    #    if 'in_stock' in request.form:
    #        in_stock = True
    #    else:
    #        in_stock = False
    #else:

    # get availability status preferencses
    in_stock = request.args.get('in_stock')
    
    try:
        if in_stock:
            available = True
            products = Product.search_product_avail(sort_by_column, query, page, rate, available) # get prodcuts that are available based on search query, filtering/sorting
            total = int(Product.search_count_avail(query, rate, available))
        else:
            total = int(Product.search_count(query, rate))
            products = Product.search_product(sort_by_column, query, page, rate) # does not take into account availability
        categories = Product.get_categories() # get categories to display in dropdown
        clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories] # reformat categories
        if current_user.is_authenticated:
            buy_again = Product.get_purchases_by_uid(current_user.id) # get all of current user's purchases
            product_ids = [product.get("productid") for product in buy_again] # reformat to a list of productids to check for buy again
            return render_template('search_product_results.html', product_ids=product_ids, in_stock=in_stock, rating=rating, sort_by=sort_by, products=products, page=page, total=total, query=query, per_page=per_page, categories=clean_text)
        if len(products) == 0:
            return render_template('search_product_results.html')
    except Exception:
        return 'No products found lol'
    return render_template('search_product_results.html', in_stock=in_stock, rating=rating, sort_by=sort_by, products=products, page=page, total=total, query=query, per_page=per_page, categories=clean_text)

# searching for products based on category using a dropdown and a preset list of categories
@bp.route('/search_category_results', methods=['GET', 'POST'])
def search_category():
    try: # an original search
        category = request.form['category']
    except: # for maintaining the search query throughout pagination
        category = request.args.get('category')
    page = int(request.args.get('page', 1))
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
    per_page = 10
    rating = request.args.get('rating', default=0)
    rate = int(rating)
    sort_by = request.args.get('sort_by', default='None')
    sort_by_column = sort_assignment(sort_by)
    in_stock = request.args.get('in_stock')
    try:
    
        if in_stock:
            available = True
            products = Product.search_categories_avail(sort_by_column, category, page, rate, available)
            total = int(Product.category_search_count_avail(category, rate, available))
        else:
            total = int(Product.category_search_count(category, rate))
            products = Product.search_categories(sort_by_column, category, page, rate) # does not take into account availability
        #productid = products[0].get('productid')
        if current_user.is_authenticated:
            buy_again = Product.get_purchases_by_uid(current_user.id)
            product_ids = [product.get("productid") for product in buy_again]
            return render_template('search_category_results.html', in_stock=in_stock, product_ids=product_ids, rating=rating, sort_by=sort_by, selected_category=category, products=products, page=page, categories=clean_text, total=total, per_page=per_page)
        if len(products) == 0:
            return render_template('search_category_results.html')
    except Exception:
        return 'No products found AH'
    return render_template('search_category_results.html', in_stock=in_stock, rating=rating, sort_by=sort_by, selected_category=category, products=products, page=page, categories=clean_text, total=total, per_page=per_page)

# show detailed information for a given product
@bp.route('/product/<int:productid>')
def product_detail(productid):
    product = Product.get(productid) # get product info
    inventory = ProductsForSale.get_all_sellers_for_product(int(productid)) # get a list of sellers for the product
    reviews = Reviews.get_reviews_by_product_id(productid)
    product_rating_summary = Reviews.get_product_rating_summary(productid)  
    if product_rating_summary is None:
        product_rating_summary = {
        'average_rating': 0,
        'number_of_ratings': 0
    }
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
    return render_template('product_detail.html', product=product, inventory=inventory, reviews=reviews, product_rating_summary=product_rating_summary, categories=clean_text)

    return render_template('product_detail.html', product=product, inventory=inventory, categories=clean_text, reviews=reviews)
