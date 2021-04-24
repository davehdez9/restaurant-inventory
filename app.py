import os

from flask import Flask, request, render_template, redirect, flash, session, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, Vendor, Product, User, Inventory
from forms import SignUpForm, LoginForm, ProductForm, VendorForm

CURR_USER_KEY = "curr_user"

# APP CONFIGURATIONS -> 
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     os.environ.get('postgresql:///restaurant_inventory_db'))
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql:///restaurant_inventory_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

######################################################################
# User signup/login/logout

@app.before_request
def add_user_to_g():
    """If we are logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user: None

def do_login(user):
    """Log in User"""
    session[CURR_USER_KEY] = user.id

def do_logout():
    """Log Out User"""
    if CURR_USER_KEY in session: 
        del session[CURR_USER_KEY]

# ----- Landing Page Route
@app.route("/")
def landing_page():
    """Shoes Landing Page"""
    return render_template("landing_page.html")

# ----- User signUp Route
@app.route("/signUp", methods=['GET', 'POST'])
def sign_up():
    """Handle user signup.

    Create a new user and add to DB. Redirect to home page.

    If Form not valid, present form.

    If there already is a user with that name: flash message and re-represent form.
    
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                email = form.email.data,
                password = form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template('signUp.html', form=form)

        do_login(user)
        
        return redirect('/homePage')

    else:
        return render_template('signUp.html', form=form)

# ----- User Login Route  
@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """handle User Loging"""
    
    form = LoginForm()

    if form.validate_on_submit():

        user = User.authenticate(form.email.data, form.password.data)

        if user:
            do_login(user)
            flash("Welcome Back!", "success")
            return redirect('/homePage')
        
        flash("invalid credentials", 'danger')
        

    return render_template('login.html', form=form)

# ----- User Logout Route
@app.route("/logout")
def logout_user():
    """Handle logout of users"""
    # session.pop('user_id')
    # flash("GoodBye!")
    do_logout()
    flash('Your are now Logout', 'success')
    return redirect('/')

# ----- Home page Route
@app.route('/homePage')
def home_page():
    if g.user:
        return render_template("homePage.html")
    else: 
        redirect('/')

# ---------- Inventory Routes
# GET /Inventory - Get all Inventories
# GET /Inventory/[id] - Get inventory
# POST /Inventory -  Create inventory
# PUT/PATCH /Inventory/[id] - Update inventory
# DELETE /Inventory/[id] - Delete Inventory 

# ---------- Products Routes
# GET /products - Get all products
@app.route('/products')
def list_products():
    if not g.user:
        flash("Please Login First")
        return redirect('/')
    all_products = Product.query.all()
    return render_template('products/products.html', products=all_products)

# GET /products/[id] - Get product
@app.route('/products/<int:id>')
def find_product(id):
    product = Product.query.get_or_404(id)
    return jsonify(product=product.serialize())

# POST /products -  Create product
@app.route('/products/new', methods=['GET', 'POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        product_name = form.product_name.data
        product_description = form.product_description.data
        unit_measurement = form.unit_measurement.data
        package_amount = form.package_amount.data
        price_per_package= form.price_per_package.data

        new_product = Product(
            product_name=product_name,
            product_description=product_description,
            unit_measurement=unit_measurement,
            package_amount=package_amount,
            price_per_package=price_per_package
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect("/products")
    else:
        return render_template('products/add_new_product_form.html', form=form)
    
# PUT/PATCH /products/[id] - Update product
@app.route('/products/<int:id>/edit', methods=["GET", "POST"])
def update_product(id):

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')

    product = Product.query.get_or_404(id)
    # product = Product.query.get(id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        product.product_name = form.product_name.data
        product.product_description = form.product_description.data
        product.unit_measurement = form.unit_measurement.data
        product.package_amount = form.package_amount.data
        product.price_per_package = form.price_per_package.data

        db.session.commit()
        return redirect("/products")
    else:
        return render_template('products/edit_product_form.html', form=form, product=product)

# DELETE /products/[id] - Delete Products 
@app.route('/products/<int:id>/delete', methods=["POST"])
def delete_product(id):
    """delete product """

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')
    
    product = Product.query.get_or_404(id)
    
    db.session.delete(product)
    db.session.commit()
    return redirect('/products')

# ---------- Vendor Routes
# GET /Vendors - Get all Vendors
@app.route('/vendors')
def list_vendors():
    """Get all Vendors"""
    if not g.user:
        flash("Please Login First")
        return redirect('/')
    
    # all_vendors = [vendor.serialize() for vendor in Vendor.query.all()]
    all_vendors = Vendor.query.all()
    return render_template('vendors/vendors.html', vendors=all_vendors)
# GET /vendors/[id] - Get vendors
@app.route('/vendors/<int:id>')
def find_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    return jsonify(vendor=vendor.serialize())

# POST /vendors -  Create product
@app.route('/vendors/new', methods=["GET", "POST"])
def add_vendor():
    """Add a New Vendor"""

    form = VendorForm()
    if form.validate_on_submit():
        vendor_name=form.vendor_name.data,
        vendor_description=form.vendor_description.data
        contact_name=form.contact_name.data
        contact_email=form.contact_email.data
        vendor_website=form.vendor_website.data
        vendor_notes=form.vendor_notes.data

        new_vendor = Vendor(
            vendor_name=vendor_name,
            vendor_description=vendor_description,
            contact_name=contact_name,
            contact_email=contact_email,
            vendor_website=vendor_website,
            vendor_notes=vendor_notes
        )
        db.session.add(new_vendor)
        db.session.commit()
        return redirect("/vendors")
    else:
        return render_template('vendors/add_new_vendor_form.html',form=form)
    
# PUT/PATCH /vendors/[id] - Update product
@app.route('/vendors/<int:id>/edit', methods=["GET", "POST"])
def update_vendor(id):
    """Update Product"""
    if not g.user:
        flash("Access Unauthorized", "danger")
        return redirect('/')

    vendor = Vendor.query.get_or_404(id)

    form = VendorForm(obj=vendor)

    if form.validate_on_submit():
        vendor.vendor_name=form.vendor_name.data,
        vendor.vendor_description=form.vendor_description.data
        vendor.contact_name=form.contact_name.data
        vendor.contact_email=form.contact_email.data
        vendor.vendor_website=form.vendor_website.data
        vendor.vendor_notes=form.vendor_notes.data

        db.session.commit()
        return redirect("/vendors")
    else:
        return render_template('vendors/edit_vendor_form.html', form=form, vendor=vendor)


# DELETE /vendor/[id] - Delete vendor 
@app.route('/vendors/<int:id>/delete', methods=["POST"])
def delete_vendor(id):
    """Delete Vendor"""
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect('/')
    
    vendor = Vendor.query.get_or_404(id)
    db.session.delete(vendor)
    db.session.commit()
    return redirect('/vendors')



