from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, DateField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

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
    recaptcha = RecaptchaField()
    hidden_trap = StringField('', validators=[Length(max=0)])
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
        EqualTo('new_password', message="Passwords match.")
    ])
    submit = SubmitField('Update Password')
