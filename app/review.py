from flask import request, jsonify, Blueprint, render_template
from .models.review import Reviews  # Assuming the unified table is named 'Review'

bp = Blueprint('feedback', __name__)


@bp.route('/feedbacks', methods=['GET', 'POST'])
def get_feedbacks():
    feedbacks = []

    if request.method == 'POST':
        user_id = request.form['user_id']
        
        # Fetch most recent feedbacks
        feedbacks = get_recent_reviews_by_uid(user_id, 5)

    return render_template('feedbacks.html', feedbacks=feedbacks)


def get_recent_reviews_by_uid(uid, limit=5):
    # Fetch most recent reviews directly from the unified Review model
    reviews = Reviews.get_most_recent_by_uid(uid, limit)

    # Sorting the reviews by date in descending order (just to ensure order, 
    # but ideally this should already be handled by the database query)
    reviews_sorted = sorted(reviews, key=lambda x: x.date, reverse=True)

    # Taking only the top 'limit' reviews
    return reviews_sorted[:limit]
