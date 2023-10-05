from flask import Flask, request, jsonify, Blueprint, render_template
bp = Blueprint('products', __name__)

from .models.product import Product

@bp.route('/', methods=['GET', 'POST'])
def top_products():
    if request.method == 'POST':
        print("postellie")
        try:
            k = int(request.form['k'])
            products = Product.get_all(True)
            sorted_products = sorted(products, key=lambda x: x.price, reverse=True)[:k]
            return render_template('search.html', top_k_products=sorted_products)
        except ValueError:
            return "Invalid input. Please enter a valid number for K."
    return render_template('index.html')