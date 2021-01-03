from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
    StringField, PasswordField, TextAreaField, DecimalField,RadioField,
    DateField, SelectMultipleField, IntegerField, ValidationError,
    SelectField, widgets
    )
from flask_wtf.file import FileField, FileAllowed, FileRequired#, MultipleFileField
from wtforms.validators import InputRequired, Email, Length, NumberRange
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date, timedelta

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[InputRequired(), Length(min=1, max=99, message="1-49 character range.")])
    price = DecimalField('Retail Price (USD)', validators=[InputRequired()])
    stock = IntegerField('Stock', validators=[InputRequired()])
    description = TextAreaField('Describe', default=' ')
    instructions = TextAreaField('Instructions', default=' ')

    def validate_price(form, field):
        if field.data <= 0:
            raise ValidationError('Please enter a positive value for pricing.')

class LaunchForm(ProductForm):
    choices = []
    ingredients = MultiCheckboxField('Checkfields', choices=choices)

class EditForm(ProductForm):
    pass

def make_checkbox(options):
    choices = []
    i = 0
    for option in options:
        choices.append((i, option))
        i += 1
    return choices
