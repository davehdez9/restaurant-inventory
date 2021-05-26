import os
import logging
import requests
import json

from flask import Flask, request, render_template, redirect, flash, session, jsonify, g, url_for
# from secrets import API_KEY
# from flask_whooshalchemy import whoosh_index
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Stock
from forms import SignUpForm, LoginForm, ProductForm, VendorForm, StockForm, StockUpdateForm, IssueForm, ReceiveForm, ReorderLevelForm, ConvertUnitForm

log = logging.getLogger("my-logger")
log.info("Hello, world")

CURR_USER_KEY = "curr_user"
API_BASE_URL = 'https://api.spoonacular.com/recipes/convert?'
API_KEY = '087fcaf2057b4da69bd7067c566617ed'

# APP CONFIGURATIONS -> 
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = (
#     os.environ.get('postgresql:///restaurant_inventory_db'))
app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql:///restaurant_inventory_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
# app.config['WHOOSH_BASE'] = 'whoosh'

debug = DebugToolbarExtension(app)

connect_db(app)
# whoosh_index(app, Stock)

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
        
        return redirect('/home')

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
            return redirect('/home')
        
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
@app.route('/home')
def home_page():
    if g.user:
        return render_template("homePage.html")
    else: 
        redirect('/')

# ----------------------Stock Routes
@app.route('/items', methods=['GET', 'POST'])
def list_items():

    search_category = request.args.get('c')
    search_product = request.args.get('p')
    # all_items = Stock.query.all()
    
    if search_category or search_product:
        search = Stock.query.filter(Stock.category.like(f"%{search_category}%"), Stock.product_name.like(f"%{search_product}%")).all()
    else:
        search = Stock.query.all()

    return render_template('list_items.html', search=search)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    form = StockForm()

    if form.validate_on_submit():
        category = form.category.data
        product_name = form.product_name.data
        quantity = form.quantity.data

        

        new_item = Stock(
            category=category,
            product_name=product_name,
            quantity=quantity,
        )
        db.session.add(new_item)
        flash("Added Successfully", "success")
        db.session.commit()
        return redirect('/items')
    else:
        return render_template('add_items.html', form=form)

@app.route('/update_item/<int:id>/', methods=["GET", "POST"])
def update_item(id):
    query = Stock.query.get_or_404(id)
    form = StockUpdateForm(obj=query)

    if form.validate_on_submit():
        query.category = form.category.data
        query.product_name = form.product_name.data
        query.quantity = form.quantity.data
        flash("Updated Successfully", "success")

        db.session.commit()
        return redirect('/items')
    else:
        return render_template('add_items.html', form=form)

@app.route('/delete_items/<int:id>/', methods=['GET', 'POST'])
def delete_items(id):
    query = Stock.query.get_or_404(id)

    if request.method == 'POST':
        if query:
            db.session.delete(query)
            flash("Deleted Successfully", "success")
            db.session.commit()
            return redirect('/items')
    
    return render_template('delete_items.html')

@app.route('/item_details/<int:id>/')
def item_details(id):
    item = Stock.query.get_or_404(id)
    return render_template('item_detail.html', item=item)

@app.route('/issue_items/<int:id>/', methods=['GET', 'POST'])
def issue_items(id):
    item = Stock.query.get_or_404(id)
    form = IssueForm(obj=item)

    if form.validate_on_submit():
        if item:
            item.issue_quantity = form.issue_quantity.data
            db.session.commit()
         
            item.quantity -= item.issue_quantity
            flash(f"Issued Successfully. {item.quantity} {item.product_name}s now left in Store", 'success')
            db.session.commit()
            return redirect(url_for('item_details', id=id))

    return render_template('add_items.html', item=item, form=form)

@app.route('/receive_items/<int:id>/', methods=['GET', 'POST'])
def receive_items(id):
    item = Stock.query.get_or_404(id)
    form = ReceiveForm(obj=item)

    if form.validate_on_submit():
        if item:
            item.receive_quantity = form.receive_quantity.data
            db.session.commit()

            item.quantity += item.receive_quantity
            flash(f"Received Successfully. {item.quantity} {item.product_name}s now in Store", 'success')
            db.session.commit()
            return redirect(url_for('item_details', id=id))

    return render_template('add_items.html', item=item, form=form)           
        
@app.route('/reorder_level/<int:id>/', methods=['GET', 'POST'])
def reorder_level(id):
    item = Stock.query.get_or_404(id)
    form = ReorderLevelForm(obj=item)

    if form.validate_on_submit():
        if item:
            item.reorder_levels = form.reorder_level.data
            db.session.commit()
            flash(f"Reorder Level for {item.product_name} is update to {item.reorder_levels}")
            return redirect('/items')
    
    return render_template('add_items.html', form=form, item=item)

@app.route('/convert')
def convert():
    return render_template('convert_unit_form.html')

@app.route('/convert_unit')
def convert_unit_form():
    ingredient = request.args.get('ingredient')
    source_amount = request.args.get('sourceAmount')
    source_unit = request.args.get('sourceUnit')
    target_unit = request.args.get('targetUnit')

    response = requests.get(f"{API_BASE_URL}", params={'apiKey':API_KEY, 
                                                        'ingredientName':ingredient, 
                                                        'sourceAmount':source_amount, 
                                                        'sourceUnit':source_unit, 
                                                        'targetUnit':target_unit}
    )

    data = response.json()
    result = data['answer']

    return render_template("convert_unit_form.html", answer=result)








    
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



