from flask import Blueprint, render_template, redirect, url_for, flash, request
from urllib.parse import urlparse
from models import db, User
from forms import LoginForm, SignupForm  # Ensure SignupForm is imported
from flask_login import login_user, current_user, login_required, logout_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SignupForm()
    if form.validate_on_submit():
        existing_user_email = User.query.filter_by(
            email=form.email.data).first()
        if existing_user_email:
            flash(
                'That email address is already registered. Please log in or use a different email.', 'warning')
            # Or render_template with form
            return redirect(url_for('auth.signup'))

        existing_user_username = User.query.filter_by(
            username=form.username.data).first()
        if existing_user_username:
            flash(
                'That username is already taken. Please choose a different one.', 'warning')
            # Or render_template with form
            return redirect(url_for('auth.signup'))

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', title='Sign Up', form=form)


# pokedex_project/routes/auth.py
# ... other imports ...


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(email=form.identifier.data).first()
        if not user:
            user = User.query.filter_by(username=form.identifier.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username/email or password.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=True)
        flash(f'Welcome back, {user.username}!', 'success')

        next_page_arg = request.args.get('next')
        if not next_page_arg or urlparse(next_page_arg).netloc != '':
            next_page_redirect = url_for('main.index')
        else:
            next_page_redirect = next_page_arg
        return redirect(next_page_redirect)

    # Debugging for GET requests or failed POST validation
    print(
        f"--- Attempting to render login.html for method: {request.method} ---")
    try:
        # Ensure all variables needed by login.html and base.html are available.
        # 'form' is passed. 'current_year' and 'search_form' come from context_processor.
        html_output = render_template('login.html', title='Login', form=form)
        print(
            f"--- Rendered login.html. Content length: {len(html_output)} ---")
        if not html_output.strip() and request.method == 'GET':  # Check if it's genuinely empty
            print(
                "--- WARNING: login.html rendered as empty or whitespace only on GET! ---")
            # You could even try rendering a minimal string to see if render_template itself is broken
            # return "Minimal render test"
        return html_output
    except Exception as e:
        print(f"--- ERROR rendering login.html: {e} ---")
        # It's important to see this error in the test output if it happens
        import traceback
        traceback.print_exc()
        raise  # Re-raise to make the test fail clearly if a Jinja error occurs here


@auth_bp.route('/logout')
@login_required  # Ensures only logged-in users can logout
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
