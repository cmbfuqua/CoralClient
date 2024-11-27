from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, TextAreaField, SubmitField, SelectField,FileField,FloatField
from wtforms.validators import DataRequired, NumberRange

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



class MaintenanceVisitForm(FlaskForm):
    customer_id = SelectField('Customer', choices=[], coerce=int)
    before_picture = FileField('Before Picture')
    ammonia = FloatField('Ammonia', validators=[DataRequired()])
    nitrite = FloatField('Nitrite', validators=[DataRequired()])
    nitrate = FloatField('Nitrate', validators=[DataRequired()])
    ph = FloatField('pH', validators=[DataRequired()])
    phosphates = FloatField('Phosphates', validators=[DataRequired()])
    calcium = FloatField('Calcium', validators=[DataRequired()])
    magnesium = FloatField('Magnesium', validators=[DataRequired()])
    alkalinity = FloatField('Alkalinity', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    recommendations = TextAreaField('Recommendations')
    after_picture = FileField('After Picture')
    submit = SubmitField('Submit')
