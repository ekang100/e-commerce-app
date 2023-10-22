

from flask import request, jsonify, Blueprint, render_template
from .models.review import Reviews 

bp = Blueprint('feedback', __name__)


@bp.route('/feedbacks', methods=['GET', 'POST'])
def get_feedbacks():
    feedbacks = []

    if request.method == 'POST':
        user_id = request.form['user_id']
        
        feedbacks = get_recent_reviews_by_uid(user_id, 5)

    return render_template('feedbacks.html', feedbacks=feedbacks)


def get_recent_reviews_by_uid(uid, limit=5):
    reviews = Reviews.get_most_recent_by_uid(uid, limit)
    reviews_sorted = sorted(reviews, key=lambda x: x.date, reverse=True)
    return reviews_sorted[:limit]
