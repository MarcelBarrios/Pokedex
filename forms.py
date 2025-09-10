from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User  # Assuming models.py is in the same directory or accessible


class SignupForm(FlaskForm):
    """Form for users to create new account."""
    username = StringField(
        'Username',
        validators=[
            DataRequired(message="Username is required."),
            Length(min=3, max=30,
                   message="Username must be between 3 and 30 characters.")
        ]
    )
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required."),
            Email(message="Invalid email address.")
        ]
    )
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message="Password is required."),
            Length(min=6, message="Password must be at least 6 characters long.")
        ]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message="Please confirm your password."),
            EqualTo('password', message="Passwords must match.")
        ]
    )
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email address is already registered. Please use a different one or log in.')


class LoginForm(FlaskForm):
    """Form for users to login."""
    identifier = StringField(  # Can be username or email
        'Username or Email',
        validators=[DataRequired(message="Username or Email is required.")]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(message="Password is required.")]
    )
    submit = SubmitField('Login')


class SearchForm(FlaskForm):
    """Form for searching Pokemon."""
    search_term = StringField(
        'Search Pokemon',
        validators=[DataRequired(message="Enter a Pokemon name or ID.")]
    )
    submit = SubmitField('Search')


