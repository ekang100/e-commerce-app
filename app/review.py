from flask import redirect, request, jsonify, Blueprint, render_template, flash, url_for, session
from .models.review import Reviews 

bp = Blueprint('feedback', __name__)

@bp.route('/feedbacks', methods=['GET', 'POST'])
def get_feedbacks():
    feedbacks = []

    if request.method == 'POST':
        user_id = request.form['user_id']

        try:
            feedbacks = get_recent_reviews_by_uid(user_id)
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('feedbacks.html', feedbacks=[])

    return render_template('feedbacks.html', feedbacks=feedbacks)


def get_recent_reviews_by_uid(uid):
    try:
        reviews = Reviews.get_most_recent_by_uid(uid)
        reviews_sorted = sorted(reviews, key=lambda x: x.date, reverse=True)
        return reviews_sorted
    except Exception as e:
        # Handle database errors
        raise ValueError(f"Error fetching reviews: {str(e)}")



@bp.route('/post_review', methods=['GET', 'POST'])
def post_review_route():
    user_id = session.get('user_id')  # Assume that the user ID is stored in the session

    if request.method == 'POST':
        type = request.form['type']
        entity_id = request.form['entity_id']
        uid = user_id or request.form['uid']  # Use the user ID from the session if available
        rating = request.form['rating']
        comments = request.form['comments']

        try:
            message = Reviews.post_review(type, entity_id, uid, rating, comments)
            flash(message, 'success')
        except Exception as e:
            flash(f"Error posting review: {str(e)}", 'error')

        return redirect(url_for('feedback.get_feedbacks'))

    # If method is GET, render the review form with the user_id pre-filled if available
    return render_template('post_review.html', user_id=user_id)



