from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from .models.user import User
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


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

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')


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


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))

@bp.route('/account')
def account():
    return render_template('account.html')

class UpdateForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    submit = SubmitField('Update')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email.')

@bp.route('/update_name_address', methods=['GET', 'POST'])
def update_name_address():
    form = UpdateForm()
    if request.method == 'POST':
        if User.update_name_address(current_user.id,
                        form.address.data,
                        form.firstname.data,
                        form.lastname.data):
            return redirect(url_for('users.account'))
    return render_template('update_name_address.html', title='Update Name and Address', form=form)

@bp.route('/change_email', methods=['GET', 'POST'])
def change_email():
    form = UpdateForm()
    if request.method == 'POST':
        if User.change_email(current_user.id,
                        form.email.data):
            return redirect(url_for('users.account'))
    return render_template('change_email.html', title='Change Email', form=form)

class PasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    submit = SubmitField('Update')
    
@bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    form = PasswordForm()
    # if request.method == 'POST':
    if form.validate_on_submit():
        if User.change_password(current_user.id,
                        form.password.data):
            return redirect(url_for('users.account'))
    return render_template('change_password.html', title='Change Password', form=form)

class BalanceForm(FlaskForm):
    balance = StringField('Balance', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_balance(self, balance):
        if float(balance.data) <= 0.0:
            raise ValidationError('Must add a positive value!')

@bp.route('/balance', methods=['GET', 'POST'])
def add_balance():
    form = BalanceForm()
    # if request.method == 'POST':
    if form.validate_on_submit():
        # form.validate_balance(form.balance.data) #fix this to throw error on html page
        new_balance = float(form.balance.data) + float(current_user.balance)
        if User.add_balance(current_user.id,
                        new_balance):
            return redirect(url_for('users.account'))
    return render_template('balance.html', title='Add Balance', form=form)

@bp.route('/account', methods=['GET', 'POST'])
def become_seller():
    if request.method == 'POST':
        if User.become_seller(current_user.id):
            return redirect(url_for('users.account'))
    return render_template('account.html')

@bp.route('/search_user_results', methods=['GET', 'POST'])
def search_user():
    ##add nonetype error handling
    user_to_search = request.form['query']
    try:
        # users = User.search_user(user_to_search_arr[0], user_to_search_arr[1])
        users = User.search_user(user_to_search)
        if len(users) == 0:
            return render_template('search_user_results.html')
    except Exception:
        return 'No names found'
    return render_template('search_user_results.html', users=users)

# Route for displaying public profile
# FIXXXXX
@bp.route('/user_profile/<int:account_id>', methods=['GET', 'POST'])
def public_profile(account_id):
    if request.method == 'POST':
    # try:
        info = User.pubprofile_search(account_id)
        print(info)
        return render_template('user_profile.html', user=info)
    # except:
    #     print('ERORRRRRR')
    return redirect(url_for('users.account'))
