import os
import requests

from flask import Flask, request, render_template, redirect, flash, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Stock
from forms import SignUpForm, LoginForm, StockForm, StockUpdateForm, IssueForm, ReceiveForm, ReorderLevelForm, UserEditForm
from secrets import API_KEY

CURR_USER_KEY = "curr_user"
API_BASE_URL = 'https://api.spoonacular.com/recipes/convert?'

# APP CONFIGURATIONS -> 
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///restaurant_inventory_db'))
# app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql:///restaurant_inventory_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','my-secret-key')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True

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
        g.user = None

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
                username = form.username.data,
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
    """handle User Login"""
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}", "success")
            return redirect('/home')
        
        flash("invalid credentials", 'danger')
        

    return render_template('login.html', form=form)

# ----- User Logout Route
@app.route("/logout")
def logout_user():
    """Handle logout of users"""
    do_logout()
    flash('Your are now Logout', 'success')
    return redirect('/login')

# User Profile Route 
@app.route('/users/profile', methods=["GET", "POST"]) 
def profile():
    """Update profile for current user"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    user = g.user
    form = UserEditForm(obj=user)

    if form.validate_on_submit():
        if User.authenticate(user.username, form.password.data):
            user.username = form.username.data
            user.email = form.email.data

            db.session.commit()
            return redirect("/items")
        
        flash("Wrong Password, please try again.", 'danger')
    
    return render_template('edit_profile.html', form=form, user_id=user.id)


@app.route('/users/delete', methods=['POST'])
def delete_user():
    """Delete User."""

    if not g.user:
        flash("Access unauthorized.", 'danger')
        return redirect('/')
    
    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect('/signUp')

##################################################################################

# ----- Home page Route
@app.route('/home')
def home_page():
    """Home Page App"""
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
        unit_measurement = form.unit_measurement.data

        

        new_item = Stock(
            category=category,
            product_name=product_name,
            quantity=quantity,
            unit_measurement=unit_measurement
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
        query.unit_measurement = form.unit_measurement.data
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
            flash(f"Reorder Level for {item.product_name} is update to {item.reorder_levels}", "success")
            return redirect('/items')
    
    return render_template('add_items.html', form=form, item=item)

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
    result = data.get('answer')

    return render_template("convert_unit_form.html", result=result)