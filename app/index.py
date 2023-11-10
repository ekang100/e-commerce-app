from flask import render_template, request
from flask_login import current_user
import datetime
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
    products = Product.get_paginated(True, page, per_page)
    max_page = int(math.ceil(len(all_products) / per_page))
    # render the page by adding information to the index.html file
    return render_template('index.html',
                           avail_products=products, page=page, max_page=max_page)



@bp.route('/account')
def index2():
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    return render_template('account.html',
                           purchase_history=purchases)
