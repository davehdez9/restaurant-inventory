from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField
from wtforms.validators import InputRequired, Email, Length

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