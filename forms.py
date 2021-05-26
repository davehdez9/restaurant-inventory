from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField
from wtforms.validators import InputRequired, Email, Length, ValidationError
from models import Stock

# categories = ["bread", "cereals", "rice", "pasta", "nodles", "vegetables", "legumes", "fruit", "milk", "cheese", "lean meat", 'fish', "poultry", "eggs", "nuts", "legumes" ]

class SignUpForm(FlaskForm):
    """Form for adding users."""
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[Length(min=6)])

class LoginForm(FlaskForm):
    email = StringField("email", validators=[InputRequired()])
    password = PasswordField("password", validators=[Length(min=6)])

class ProductForm(FlaskForm):

    product_name = StringField("Product Name", validators=[InputRequired()])
    product_description = StringField("description", validators=[InputRequired()])
    unit_measurement = StringField("unit", validators=[InputRequired()])
    package_amount = StringField("package", validators=[InputRequired()])
    price_per_package = FloatField("price", validators=[InputRequired()])

class VendorForm(FlaskForm):
    vendor_name = StringField("Vendor Name", validators=[InputRequired()])
    vendor_description = StringField("Description", validators=[InputRequired()])
    contact_name = StringField("Contact", validators=[InputRequired()])
    contact_email = StringField("Email", validators=[InputRequired(), Email()])
    vendor_website = StringField("Website", validators=[InputRequired()])
    vendor_notes = StringField("Notes", validators=[InputRequired()])

class StockForm(FlaskForm):
    """Form to adding a item to the Stock list"""
    # category = SelectField("Category", validators=[InputRequired()], choices=[(st, st) for st in categories])
    category = StringField("Category", validators=[InputRequired()])
    product_name = StringField("Product Name", validators=[InputRequired()])
    quantity = FloatField('Quantity', validators=[InputRequired()])
class StockSearchForm(FlaskForm):
    """Form to search a item to the Stock list"""
    category = StringField("Category")
    product_name = StringField("Product Name")

class StockUpdateForm(FlaskForm):
    """Form to update an item from the db"""
    category = StringField("Category")
    product_name = StringField("Product Name")
    quantity = FloatField('Quantity')
class IssueForm(FlaskForm):
    issue_quantity = FloatField("Issue Quantity")
    issue_to = StringField("Issue to")
class ReceiveForm(FlaskForm):
    receive_quantity = FloatField("Receive Quantity")
class ReorderLevelForm(FlaskForm):
    reorder_level = StringField("Reorder Level")

class ConvertUnitForm(FlaskForm):
    ingredient_name = StringField("Ingredient")
    source_amount = FloatField("Source Amount")
    source_unit = StringField("Source Unit")
    target_unit = StringField("Target Unit")
    
        

