from flask import Flask, request, jsonify, Blueprint, render_template
from flask_login import login_user, logout_user, current_user
import re
# from flask_paginate import Pagination
bp = Blueprint('products', __name__)

from .models.product import Product
from .models.productsforsale import ProductsForSale
from .models.review import Reviews

@bp.route('/', methods=['GET', 'POST'])
def top_products():
    if request.method == 'POST' and request.args.get('action') == 'Get Top Products':
        try:
            k = int(request.form['k'])
            products = Product.get_all(True)
            if k >= 0 and k <= len(products):
                sorted_products = sorted(products, key=lambda x: x.price, reverse=True)[:k]
                return render_template('search.html', top_k_products=sorted_products)
            else:
                return "Invalid input. Please enter a valid number for K."
        except ValueError:
            return "Invalid input. Please enter a valid number for K."
    return render_template('index.html')

@bp.route('/search_product_results', methods=['GET', 'POST'])
def search_keywords():
    try: # an original search
        query = request.form['query']
    except: # for maintaining the search query throughout pagination
        query = request.args.get('query')
    page = int(request.args.get('page', 1))
    per_page = 10
    sort_by = request.args.get('sort_by', default='None')
    rating = request.args.get('rating', default=0)
    rate = int(rating)
    if type(sort_by) is str and sort_by == "priceLow":
        sort_by_column = "price ASC"
    elif type(sort_by) is str and sort_by == "priceHigh":
        sort_by_column = "price DESC"
    else:
        sort_by_column = None
    try:
        products = Product.search_product(sort_by_column, query, page, rate)
        total = Product.search_count(query, rate)
        categories = Product.get_categories()
        clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
        if len(products) == 0:
            return render_template('search_product_results.html')
    except Exception:
        return 'No products found lol'
    return render_template('search_product_results.html', rating=rating, sort_by=sort_by, products=products, page=page, total=total, query=query, per_page=per_page, categories=clean_text)

@bp.route('/search_category_results', methods=['GET', 'POST'])
def search_category():
    category = request.args.get('category')
    page = int(request.args.get('page', 1))
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
    per_page = 10
    rating = request.args.get('rating', default=0)
    rate = int(rating)
    sort_by = request.args.get('sort_by', default='None')
    if type(sort_by) is str and sort_by == "priceLow":
        sort_by_column = "price ASC"
    elif type(sort_by) is str and sort_by == "priceHigh":
        sort_by_column = "price DESC"
    else:
        sort_by_column = None
    try:
        products = Product.search_categories(sort_by_column, category, page, rate)
        total = Product.category_search_count(category, rate)
        if len(products) == 0:
            return render_template('search_category_results.html')
    except Exception:
        return 'No products found AH'
    return render_template('search_category_results.html', rating=rating, sort_by=sort_by, selected_category=category, products=products, page=page, categories=clean_text, total=total, per_page=per_page)

@bp.route('/product/<int:productid>')
def product_detail(productid):
    product = Product.get(productid)
    inventory = ProductsForSale.get_all_sellers_for_product(int(productid))
<<<<<<< HEAD
    reviews = Reviews.get_reviews_by_product_id(productid)
    return render_template('product_detail.html', product=product, inventory=inventory, reviews=reviews)
=======
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
    seller_list = [row["sid"] for row in inventory]
    for seller in seller_list:
        buy_again = Product.get_purchases_by_uid(current_user.id, seller)
        if buy_again == productid:
            #buy_again_status = True
            inventory[7]["buy_status"] = True
        else:
            #buy_again_status = False
            inventory[7]["buy_status"] = True
    #reviews = Review.get_reviews_for_product()
    return render_template('product_detail.html', product=product, inventory=inventory, categories=clean_text)
>>>>>>> origin/ellie-productguru

