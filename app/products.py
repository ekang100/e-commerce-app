from flask import Flask, request, jsonify, Blueprint, render_template
# from flask_paginate import Pagination
bp = Blueprint('products', __name__)

from .models.product import Product

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
    try:
        products = Product.search_product(query)
        if len(products) == 0:
            return render_template('search_product_results.html')
    except Exception:
        return 'No products found'
    return render_template('search_product_results.html', products=products)