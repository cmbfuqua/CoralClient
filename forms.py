from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DecimalField, TextAreaField, DateField, EmailField
from flask_wtf.file import FileField,FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Regexp

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message="Enter a valid 10-digit phone number.")
    ])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class EditUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    dob = DateField('Date of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    phone_number = StringField('Phone Number', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message="Enter a valid 10-digit phone number.")
    ])
    submit = SubmitField('Update')

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ConsignmentForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    item_type = SelectField('Item Type', coerce=int, validators=[DataRequired()])
    item_subtype = SelectField('Item Subtype', coerce=int, validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    description = TextAreaField('Description', validators=[Length(max=200)])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Add Item')
    #featured = BooleanField('Featured (Admin only)')

class UpgradeUserForm(FlaskForm):
    user_email = StringField('User Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('user', 'User'), ('seller', 'Seller')], validators=[DataRequired()])
    submit = SubmitField('Upgrade User')

class CreateOrderForm(FlaskForm):
    buyer_id = SelectField('Selected Buyer', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Order')

class ForgotPasswordForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

class ForgotUsernameForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Username')


class ChangeGeneratedPasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('new_password', message="Passwords must match.")
    ])
    submit = SubmitField('Update Password')






