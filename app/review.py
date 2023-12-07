from flask import redirect, request, jsonify, Blueprint, render_template, flash, url_for, session
from flask_login import current_user
from .models.review import Reviews
from .models.user import User

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



# @bp.route('/post_review', methods=['POST'])
# def post_review():
#     if request.method == 'POST':
#         product_id = request.form.get('product_id')
#         seller_id = request.form.get('seller_id')
#         user_id = request.form.get('user_id')
#         rating = request.form.get('rating')
#         comments = request.form.get('comments')
#         review_type = 'product' if product_id else 'seller'
#         if not all([user_id, rating, (product_id or seller_id)]):
#             return jsonify({'error': 'Missing data'}), 400
#         try:
#             Reviews.insert_product_review(review_type, product_id, seller_id, user_id, rating, comments)
#             return jsonify({'success': 'Review added successfully'}), 200
#         except Exception as e:
#             return jsonify({'error': str(e)}), 500

#     return jsonify({'error': 'Invalid request method'}), 405

# @bp.route('/post_review', methods=['POST'])
# def post_review():
#     if request.method == 'POST':
#         product_id = request.form.get('product_id')
#         seller_id = request.form.get('seller_id')
#         user_id = request.form.get('user_id')
#         rating = request.form.get('rating')
#         comments = request.form.get('comments')
#         review_type = 'product' if product_id else 'seller'
#         if not all([user_id, rating, (product_id or seller_id)]):
#             flash('Missing data', 'error')
#             return redirect(url_for('product.product_detail', productid=product_id))

#         try:
#             Reviews.insert_product_review(review_type, product_id, seller_id, user_id, rating, comments)
#             flash('Review added successfully', 'success')
#             return redirect(url_for('products.product_detail', productid=product_id))
#         except Exception as e:
#             flash(str(e), 'error')

#     return redirect(url_for('products.product_detail', productid=product_id))
@bp.route('/post_review', methods=['POST'])
def post_review():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        seller_id = request.form.get('seller_id')
        user_id = request.form.get('user_id')
        rating = request.form.get('rating')
        comments = request.form.get('comments')
        review_type = 'seller' if seller_id else 'product'

        if not all([user_id, rating, (product_id or seller_id)]):
            flash('Missing data', 'error')
            redirect_url = url_for('products.product_detail', productid=product_id) if product_id else url_for('users.public_profile', account_id=seller_id)
            return redirect(redirect_url)
        try:
            Reviews.insert_product_review(review_type, product_id, seller_id, user_id, rating, comments)
            flash('Review added successfully', 'success')
            redirect_url = url_for('products.product_detail', productid=product_id) if product_id else url_for('users.public_profile', account_id=seller_id)
            return redirect(redirect_url)
        
        except Exception as e:
            flash(str(e), 'error')

    redirect_url = url_for('products.product_detail', productid=product_id) if product_id else url_for('users.public_profile', account_id=seller_id)
    return redirect(redirect_url)





@bp.route('/update_review/<int:review_id>', methods=['POST'])
def update_review(review_id):
    current_user_id = current_user.id
    new_rating = request.form.get('rating')
    new_comments = request.form.get('comments')

    # Fetch the review and check if the current user is the author
    review = Reviews.get_review_by_id(review_id)

    if review and review['uid'] == current_user_id:
        Reviews.update_review(review_id, new_rating, new_comments)
        flash('Review updated successfully', 'success')

        # Redirect based on review type
        if review['type'] == 'product':
            return redirect(url_for('products.product_detail', productid=review['product_id']))
        else:
            return redirect(url_for('users.public_profile', account_id=review['seller_id']))

    else:
        flash('You do not have permission to update this review', 'error')
    return "Uh oh"


@bp.route('/delete_review/<int:review_id>/', methods=['POST'])
def delete_review(review_id):
    current_user_id = current_user.id
    # Fetch the review and check if the current user is the author
    review = Reviews.get_review_by_id(review_id)
    if review and review['uid'] == current_user_id:
        Reviews.delete_review(review_id)
        flash('Review deleted successfully', 'success')

        # Redirect based on review type
        if review['type'] == 'product':
            return redirect(url_for('products.product_detail', productid=review['product_id']))
        else:  # assuming review_type is 'seller'
            return redirect(url_for('users.public_profile', account_id=review['seller_id']))
    else:
        flash('You do not have permission to delete this review', 'error')
    return "Uh oh"


@bp.route('/vote_review/<int:review_id>/<int:vote>', methods=['POST'])
def vote_review(review_id, vote):
    if not current_user.is_authenticated:
        flash("You need to be logged in to vote.", "error")
        return redirect(url_for('users.login'))

    try:
        Reviews.add_vote(review_id, current_user.id, vote)
        flash("Your vote has been recorded.", "success")
    except ValueError as e:
        flash(str(e), "error")

    # Redirect back to the referring page
    return redirect(request.referrer)




# some html for Super Seller that doesn't work yet, but saving because comments in html don't work
#     <!-- {% if user.five_star_review_count >= 1 %}
#     <div class="super-seller-badge">
#         <h3 style="color: green;">Super Seller!</h3>
#         <img src="app/static/super_seller.png" alt="Super Seller Symbol">
#     </div>
# {% endif %} -->