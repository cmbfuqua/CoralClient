from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ConsignmentForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    category = SelectField('Category', choices=[('coral', 'Coral'), ('fish', 'Fish')], validators=[DataRequired()])
    sub_category = SelectField('Sub Category', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    description = TextAreaField('Description', validators=[Length(max=200)])
    submit = SubmitField('Submit Item')

class UpgradeUserForm(FlaskForm):
    user_email = StringField('User Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('user', 'User'), ('seller', 'Seller')], validators=[DataRequired()])
    submit = SubmitField('Upgrade User')
