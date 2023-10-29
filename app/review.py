from flask import request, jsonify, Blueprint, render_template, flash
from .models.review import Reviews 

bp = Blueprint('feedback', __name__)

@bp.route('/feedbacks', methods=['GET', 'POST'])
def get_feedbacks():
    feedbacks = []

    if request.method == 'POST':
        user_id = request.form['user_id']

        try:
            feedbacks = get_recent_reviews_by_uid(user_id, 5)
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('feedbacks.html', feedbacks=[])

    return render_template('feedbacks.html', feedbacks=feedbacks)


def get_recent_reviews_by_uid(uid, limit=5):
    try:
        reviews = Reviews.get_most_recent_by_uid(uid, limit)
        reviews_sorted = sorted(reviews, key=lambda x: x.date, reverse=True)
        return reviews_sorted[:limit]
    except Exception as e:
        # Handle database errors
        raise ValueError(f"Error fetching reviews: {str(e)}")
