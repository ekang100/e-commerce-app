from flask import Flask, request, jsonify, Blueprint, render_template
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
    query = str(request.form['query'])
    page = int(request.args.get('page', 1))
    try:
        products = Product.search_product(query)
        if len(products) == 0:
            return render_template('search_product_results.html')
    except Exception:
        return 'No products found'
    return render_template('search_product_results.html', products=products, page=page)

@bp.route('/product/<int:productid>')
def product_detail(productid):
    product = Product.get(productid)
    inventory = ProductsForSale.get_all_sellers_for_product(int(productid))
    return render_template('product_detail.html', product=product, inventory=inventory)

