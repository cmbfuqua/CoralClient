from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

class UpgradeUserForm(FlaskForm):
    user_email = StringField('User Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('user', 'User'), ('seller', 'Seller')], validators=[DataRequired()])
    submit = SubmitField('Upgrade User')

class CreateOrderForm(FlaskForm):
    buyer_id = SelectField('Selected Buyer', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Order')
