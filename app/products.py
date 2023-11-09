from flask import Flask, request, jsonify, Blueprint, render_template
bp = Blueprint('products', __name__)

from .models.product import Product

@bp.route('/', methods=['GET', 'POST'])
def top_products():
    if request.method == 'POST':
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