from flask import request, jsonify, Blueprint, render_template
from .models.product_review import ProductReview
from .models.seller_review import SellerReview

bp = Blueprint('feedback', __name__)


@bp.route('/feedbacks', methods=['GET', 'POST'])
def get_feedbacks():
    feedbacks = []

    if request.method == 'POST':
        user_id = request.form['user_id']
        
        # Fetch most recent feedbacks
        product_reviews = get_recent_reviews_by_uid(user_id, 5)
        # seller_reviews = SellerReview.get_recent_reviews_by_uid(user_id, 5)
        
        # Combining product and seller reviews. 
        # For simplicity, assuming they have the same fields (productid, comments, date, etc.).
        feedbacks = product_reviews
        feedbacks.sort(key=lambda x: x.date, reverse=True)  # Sort by date, most recent first
        feedbacks = feedbacks[:5]  # Limit to 5

    return render_template('feedbacks.html', feedbacks=feedbacks)


def get_recent_reviews_by_uid(uid, limit=5):
    product_reviews = ProductReview.get_most_recent_by_uid(uid, limit)
    # seller_reviews = SellerReview.get_most_recent_by_uid(uid, limit)

    # Combining the two lists
    all_reviews = product_reviews

    # Sorting the combined list by date in descending order
    all_reviews_sorted = sorted(all_reviews, key=lambda x: x.date, reverse=True)

    # Taking only the top 'limit' reviews
    return all_reviews_sorted[:limit]
