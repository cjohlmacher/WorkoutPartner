from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class CreateUserForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8)])

class AuthenticateForm(FlaskForm):
    """Form for authenticating user"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password')
    
