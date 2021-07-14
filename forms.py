# from secrets import choice
from random import choices
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField
from wtforms.validators import InputRequired, Email, Length, ValidationError, DataRequired
from wtforms.widgets import Input
class SignUpForm(FlaskForm):
    """Form for adding users."""
    username = StringField("Username", validators=[DataRequired(), 
                                                   Length(min=5, max=35, message="Username must be between %(min)d and %(max)dcharacters")], 
                                                   render_kw={"placeholder": "newuser123"})
    email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "newuser123@example.com"})
    password = PasswordField("Password", validators=[Length(min=6)])
    
class LoginForm(FlaskForm):
    username = StringField("username", validators=[DataRequired()], render_kw={"placeholder": "newuser123"})
    password = PasswordField("password", validators=[Length(min=6)])

class UserEditForm(FlaskForm):
    """Form to edit the current user"""

    username = StringField("username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()] )
    password = PasswordField("Password", validators=[Length(min=6)])
class StockForm(FlaskForm):
    """Form to adding a item to the Stock list"""
 
    category = StringField("Category", validators=[InputRequired()])
    product_name = StringField("Product Name", validators=[InputRequired()])
    quantity = FloatField('Quantity', validators=[InputRequired()])
    unit_abbreviation = SelectField("Unit of Measurement", choices=[('Kg', 'Kilograms'), ('lbs', 'Pounds'), ('Gr', 'Grams'), ('Oz', 'Ounces'), ('C', 'Cups'), ('L', 'Liters'), ('Gal', 'Gallons'), ('Qt', 'Quart'), ('Pt', 'Pint'), ('Units', 'Units')],  validators=[InputRequired()])
    # unit_abbreviation = SelectField("Unit Measurement")
    reorder_level = StringField("Minimum required in stock", validators=[InputRequired()])

class StockUpdateForm(FlaskForm):
    """Form to update an item from the db"""
    category = StringField("Category")
    product_name = StringField("Product Name")
    # quantity = FloatField('Quantity')
    unit_abbreviation = SelectField("Unit of Measurement", choices=[('Kg', 'Kilograms'), ('lbs', 'Pounds'), ('Gr', 'Grams'), ('Oz', 'Ounces'), ('C', 'Cups'), ('L', 'Liters'), ('Gal', 'Gallons'), ('Qt', 'Quart'), ('Pt', 'Pint'), ('Units', 'Units')],  validators=[InputRequired()])
    # unit_abbreviation = StringField("Unit Measurement")
    reorder_level = StringField("Reorder Level")

class Search(FlaskForm):
    """Form to search products and categories"""
    category = StringField("Category")
    product_name = StringField("Product Name")
class IssueForm(FlaskForm):
    issue_quantity = FloatField("Issue Quantity")
    # issue_to = StringField("Issue to")
class ReceiveForm(FlaskForm):
    receive_quantity = FloatField("Receive Quantity")
# class ReorderLevelForm(FlaskForm):
#     reorder_level = StringField("Reorder Level")

# class Convertion(FlaskForm):
#     ingredient_name = StringField("Ingredient")
#     source_amount = FloatField("Quantity")
#     source_unit = SelectField("Convert from")
#     target_unit = SelectField("Convert to")
class AddConvertion(FlaskForm):
    unit_name = StringField("Unit Convertion")
    unit_abbreviation = StringField("Abbreviation")

        

