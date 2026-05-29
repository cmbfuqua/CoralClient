from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from wtforms.validators import DataRequired, Length, NumberRange

class ConsignmentForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    item_type = SelectField('Item Type', coerce=int, validators=[DataRequired()])
    item_subtype = SelectField('Item Subtype', coerce=int, validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)], places=2)
    description = TextAreaField('Description', validators=[Length(max=200)])
    image = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Add Item')
