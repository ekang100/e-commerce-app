from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.purchase import Purchase
from .models.review import Reviews

import os
import random

from flask import Blueprint
# Create a Blueprint for the users module. This helps in organizing the app into components.
bp = Blueprint('users', __name__)

# Define a form for user login with email, password, and remember me fields.
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Define a form for new user registration with validation for unique email.
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Register')

# Define a form for updating user information.
class UpdateForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    submit = SubmitField('Update')

    def validate_email(self, email):
    # Define a form for updating user information.
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

    def validate_email(self, email):
    # Custom validator to check if the email already exists.
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

# Define a form for updating the user's password.
class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Update')

# Define a form for updating the user's account balance.
class BalanceForm(FlaskForm):
    balance = StringField('Balance', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_balance(self, balance):
    # Custom validator to ensure the balance added is positive.
        if float(balance.data) <= 0.0:
            raise ValidationError('Must add a positive value!')

# Define a form for updating the user's bio with a character limit.
class BioForm(FlaskForm):
    bio = StringField('500 Character Limit')
    submit = SubmitField('Update')

    def validate_bio(self, bio):
        # Custom validator for bio length.
        if bio.data is None:
            return
        if len(bio.data) > 500:
            raise ValidationError(f'Your bio is too long: {len(bio.data)} characters. It must be 500 characters or less.')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Handles user login, including captcha verification and redirection after successful login.
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    form = LoginForm()

    if 'captchaList' not in session:
        # initialize captcha list if not already in session
        session['captchaList'] = []

    captchaList = session['captchaList']

    if not captchaList:
        # gen captcha information if the list is empty
        static_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/captcha')
        filenames = [filename for filename in os.listdir(static_path) if os.path.isfile(os.path.join(static_path, filename))]
        random_file = random.choice(filenames)
        captchaImg = 'static/captcha/' + random_file
        captchaAnswer = random_file[:5]  # Assuming the answer is the first 5 characters of the filename

        captchaList.append((captchaImg, captchaAnswer))
        session['captchaList'] = captchaList
    else:
        # get captcha information from the list
        captchaImg, captchaAnswer = captchaList[-1]

    captchaCorrect = False

    if request.method == 'POST':
        captchaValue = request.form.get('forCaptcha')
        if captchaValue and captchaValue == captchaAnswer:
            captchaCorrect = True
        else:
            flash('Captcha verification failed. Please try again.', 'error')

        if captchaCorrect and form.validate_on_submit():
            # original login logic
            user = User.get_by_auth(form.email.data, form.password.data)
            if user is None:
                flash('Invalid email or password')
                return redirect(url_for('users.login'))
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index.index')

            # remove the used captcha information from the list
            captchaList.pop()
            session['captchaList'] = captchaList

            return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form, captchaImg=captchaImg)

#Sign up if don't have an account- only need address, email (unique), password, firstname, lastname
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.address.data,
                         form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

#logout of account
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

#reroute to account page
@bp.route('/account')
def account():
    return render_template('account.html')



#Change name or address (don't need to be unique)
@bp.route('/update_name_address', methods=['GET', 'POST'])
def update_name_address():
    form = UpdateForm()
    #checks that name contains only letters upper or lowercase
    if request.method == 'POST':
        if User.update_name_address(current_user.id,
                        form.address.data,
                        form.firstname.data,
                        form.lastname.data):
            return redirect(url_for('users.account'))
    return render_template('update_name_address.html', title='Update Name and Address', form=form)

#Change email (must be unique)
@bp.route('/change_email', methods=['GET', 'POST'])
def change_email():
    form = UpdateForm()
    if request.method == 'POST':
        if User.change_email(current_user.id,
                        form.email.data):
            return redirect(url_for('users.account'))
    return render_template('change_email.html', title='Change Email', form=form)

#Change password
#Will automatically hash and update password
@bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = PasswordForm()
    # if request.method == 'POST':
    if form.validate_on_submit():
        if User.change_password(current_user.id,
                        form.password.data):
            return redirect(url_for('users.account'))
    return render_template('change_password.html', title='Change Password', form=form)

#Add balance to account
@bp.route('/balance', methods=['GET', 'POST'])
def add_balance():
    form = BalanceForm()
    #Checks that balance is a non negative number
    if form.validate_on_submit():
        #Creates new balance by adding added balance to current balance
        new_balance = float(form.balance.data) + float(current_user.balance)
        if User.add_balance(current_user.id,
                        new_balance):
            return redirect(url_for('users.account'))
    return render_template('balance.html', title='Add Balance', form=form)

#Enables user to become a seller
#Changes isSeller boolean to true (default false)
@bp.route('/become_seller', methods=['GET', 'POST'])
def become_seller():
    if request.method == 'POST':
        if User.become_seller(current_user.id):
            return redirect(url_for('users.account'))
    return render_template('account.html')

#Search for any user
@bp.route('/search_user_results', methods=['GET', 'POST'])
def search_user():
    ##add nonetype error handling- reroute to page 'No names found'
    user_to_search = request.form['query']
    try:
        users = User.search_user(user_to_search)
        if len(users) == 0:
            #Display 'no users found' if nothing matches
            return render_template('search_user_results.html')
    except Exception:
        return 'No names found'
    return render_template('search_user_results.html', users=users)

# Route for displaying public profile
@bp.route('/user_profile/<int:account_id>', methods=['GET', 'POST'])
def public_profile(account_id):
    if request.method == 'POST':
        info = User.pubprofile_search(account_id)
        #manually save seller and verified booleans to send to html
        sell_stat = info[0][4]
        ver_stat = info[0][5]
        seller_reviews = Reviews.get_reviews_by_seller_id(account_id) if sell_stat else None
        seller_reviews_summary = Reviews.get_seller_rating_summary(account_id)
        super_seller_status = Reviews.get_five_star_review_count(account_id)
        return render_template('user_profile.html', user=info, sell_stat=sell_stat, ver_stat=ver_stat, seller_reviews=seller_reviews, seller_rating_summary=seller_reviews_summary, super_seller_status=super_seller_status)
    return redirect(url_for('users.account'))

#Added isVerified feature costing $500 and get 10% off 
@bp.route('/account', methods=['GET', 'POST'])
def verify_account():
    if request.method == 'POST':
        #Check balance is greater than 500
        if User.get_balance(current_user.id) > 500:
            #subtract balance by 500
            User.add_balance(current_user.id, float(User.get_balance(current_user.id)) - 500.0)
            if User.verify_account(current_user.id):
                return redirect(url_for('users.account'))
        else:
            #In case balance is too low
            flash('You do not have enough money to become verified: $500 balance needed')
    return render_template('account.html')

#Additional feature to add user bio
@bp.route('/bio', methods=['GET', 'POST'])
def bio():
    form = BioForm()
    #500 character bio form displays on main page
    if form.validate_on_submit():
        if User.bio(current_user.id,
                        form.bio.data):
            return redirect(url_for('users.account'))
    return render_template('bio.html', title='500 Character Limit', form=form)

#Additional feature for avatar
@bp.route('/change_avatar', methods=['GET', 'POST'])
def change_avatar():
    selected_avatar = request.form.get('avatar')
    #drop down menu to select icon with 4 options
    try:
        User.change_avatar(current_user.id, selected_avatar)
        return redirect(url_for('users.account'))
    except:
        raise ValidationError('Could not update avatar')
