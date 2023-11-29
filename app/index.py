from flask import render_template, request
from flask_login import current_user
import datetime
import re
import math

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)

@bp.route('/')
def index():

    # get all available products for sale:
    page = int(request.args.get('page', 1))
    per_page = 10 # can make this adjustable in the future
    all_products = Product.get_all()

    sort_by = request.args.get('sort_by', default='None')

    products = Product.get_paginated(True, page, per_page, sort_by)
    max_page = int(math.ceil(len(all_products) / per_page))
    categories = Product.get_categories()
    clean_text = [re.sub(r"\('([^']+)',\)", r"\1", text) for text in categories]


    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products, page=page, max_page=max_page, categories=clean_text)



@bp.route('/account')
def index2():
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1950, 9, 14, 0, 0, 0))
        if current_user.isVerified:
            result = Purchase.get_all_by_uid_price_since(current_user.id, current_user.verifiedDate)
            print(result)
            if len(result) > 0:
                total_saved = sum(item['price'] for item in result)
            else:
                total_saved = 0.00
        else:
            total_saved = 0.00
    else:
        purchases = None
        total_saved = 0.00
    return render_template('account.html',
                           purchase_history=purchases, total_saved=total_saved)
