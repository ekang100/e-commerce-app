from flask import Flask, request, jsonify, Blueprint, render_template
import re
# from flask_paginate import Pagination
bp = Blueprint('products', __name__)

from .models.product import Product
from .models.productsforsale import ProductsForSale

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
    try:
        products = Product.search_product(query, page)
        total = Product.search_count(query)
        categories = Product.get_categories()
        clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
        if len(products) == 0:
            return render_template('search_product_results.html')
    except Exception:
        return 'No products found lol'
    return render_template('search_product_results.html', products=products, page=page, total=total, query=query, per_page=per_page, categories=clean_text)

@bp.route('/search_category_results', methods=['GET', 'POST'])
def search_category():
    category = request.args.get('category')
    page = int(request.args.get('page', 1))
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]
    per_page = 10
    try:
        products = Product.search_categories(category, page)
        total = Product.category_search_count(category)
        if len(products) == 0:
            return render_template('search_category_results.html')
    except Exception:
        return 'No products found AH'
    return render_template('search_category_results.html', selected_category=category, products=products, page=page, categories=clean_text, total=total, per_page=per_page)

@bp.route('/product/<int:productid>')
def product_detail(productid):
    product = Product.get(productid)
    inventory = ProductsForSale.get_all_sellers_for_product(int(productid))
    #reviews = Review.get_reviews_for_product()
    return render_template('product_detail.html', product=product, inventory=inventory)

