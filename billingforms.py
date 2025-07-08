from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, TextAreaField, SubmitField, SelectField,FileField,FloatField
from wtforms.validators import DataRequired, NumberRange, ValidationError

class AddLineItemForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    quantity = IntegerField('Quantity', default=1, validators=[DataRequired(), NumberRange(min=1)])
    unit_price = DecimalField('Unit Price', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Line Item')

class CreateBillForm(FlaskForm):
    notes = TextAreaField('Notes')
    submit = SubmitField('Generate Bill')

class UpdateBillStatusForm(FlaskForm):
    submit = SubmitField('Mark as Paid')

def zero_is_valid(form, field):
    if field.data is None:  # Ensure the field isn't None or empty
        raise ValidationError('This field is required.')
    # If it's 0, it's valid
    if field.data == 0:
        return True

class MaintenanceVisitForm(FlaskForm):
    customer_id = SelectField('Customer', choices=[], coerce=int)
    before_picture = FileField('Before Picture')
    ammonia = FloatField('Ammonia', validators=[zero_is_valid],default=-999)
    nitrite = FloatField('Nitrite', validators=[zero_is_valid],default=-999)
    nitrate = FloatField('Nitrate', validators=[zero_is_valid],default=-999)
    ph = FloatField('pH', validators=[DataRequired()],default=-999)
    phosphates = FloatField('Phosphates', validators=[zero_is_valid],default=-999)
    calcium = FloatField('Calcium', validators=[DataRequired()],default=-999)
    magnesium = FloatField('Magnesium', validators=[DataRequired()],default=-999)
    alkalinity = FloatField('Alkalinity', validators=[DataRequired()],default=-999)
    notes = TextAreaField('Notes')
    recommendations = TextAreaField('Recommendations')
    after_picture = FileField('After Picture')
    submit = SubmitField('Submit')
