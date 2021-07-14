from logging import error
import os
import re
from flask.wrappers import Response
import requests

from flask import Flask, request, render_template, redirect, flash, session, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
from models import db, connect_db, User, Stock, UnitConvertion
from forms import SignUpForm, LoginForm, StockForm, StockUpdateForm, IssueForm, ReceiveForm,UserEditForm
from secret import API_KEY

CURR_USER_KEY = "curr_user"
API_BASE_URL = 'https://api.spoonacular.com/recipes/convert?'

# APP CONFIGURATIONS -> 
app = Flask(__name__)

# TO WORK ON DEVELOPMENT -> 
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///restaurant_inventory_db'))

# TO WORK ON PRODUCTION -> 
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace("://", "ql://", 1) or 'sqlite:///restaurant_inventory_db'
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
    flash('You are now logged out', 'success')
    return redirect('/login')

# User Profile Route 
@app.route('/user/profile', methods=["GET", "POST"]) 
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

# User delete Route
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

# Items Route
@app.route('/items', methods=['GET', 'POST'])
def list_items():
    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    # form = Search()
    # if form.validate_on_submit():
    #     category = form.category.data
    #     product_name = form.product_name.data   
    #     user_inventory = Stock.query.filter(Stock.user_id == g.user.id)

    #     if category or product_name:
    #         inventory_display = user_inventory.filter(Stock.category.ilike(f"%{category}%"), Stock.product_name.like(f"%{product_name}%")).all()
    #     else:
    #         inventory_display = user_inventory.all()
    #         # return redirect(url_for('list_items', inventory_display=inventory_display, form=form))
    #         return render_template('list_items.html', inventory_display=inventory_display, form=form)       
            
    # return render_template('list_items.html', form=form)

    search_category = request.args.get('c')
    search_product = request.args.get('p')
    # all_items = Stock.query.all()

    user_inventory = Stock.query.filter(Stock.user_id == g.user.id)
    
    if search_category or search_product:
        inventory_display = user_inventory.filter(Stock.category.ilike(f"%{search_category}%"), Stock.product_name.ilike(f"%{search_product}%")).all()
    else:
        inventory_display = user_inventory.all()

    return render_template('list_items.html', inventory_display=inventory_display)

# Add Items Route
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    form = StockForm()

    # [ x] -> CHECK
    # unit = db.session.query(UnitConvertion.unit_abbreviation, UnitConvertion.unit_name).all()
    # form.unit_abbreviation.choices = unit

    ## Pseudocode for improving searches:
    # # convert all user entires into: "first letter uppercase, all other letters lowercase"

    # first_letter = # find first letter of string
    # rest_of_word = # rest of string
    # updated_word = first_letter.toUpperCase() + rest_of_word.toLowerCase()

    # # search, you need to compare 2 strings, and both strings need to be converted to whatever you have saved in the database
    # # if updated_word in database: return True

    # first_letter = # find first letter of string
    # rest_of_word = # rest of string
    # updated_input = first_letter.toUpperCase() + rest_of_word.toLowerCase()

    # # if updated_input in database return True


    if form.validate_on_submit():
        category = form.category.data
        product_name = form.product_name.data
        quantity = form.quantity.data
        unit_abbreviation = form.unit_abbreviation.data
        reorder_level = form.reorder_level.data

        new_item = Stock(
            category=category,
            product_name=product_name,
            quantity=quantity,
            reorder_levels=reorder_level,
            user_id= g.user.id,
            unit_abbreviation=unit_abbreviation
        )

        db.session.add(new_item)
        
        db.session.commit()
        flash("Added Successfully", "success")
        return redirect('/items')
       
    else:
        return render_template('add_items.html', form=form)

# Update Item Route
@app.route('/update_item/<int:id>/', methods=["GET", "POST"])
def update_item(id):

    if not g.user:
        flash("Access unauthorized", "danger")
        return redirect("/")

    stock = Stock.query.get_or_404(id)
    form = StockUpdateForm(obj=stock)

    # CHECK
    # unit = db.session.query(UnitConvertion.unit_abbreviation, UnitConvertion.unit_name).all()
    # form.unit_abbreviation.choices = unit

    if form.validate_on_submit():
        stock.category = form.category.data
        stock.product_name = form.product_name.data
        stock.quantity = form.quantity.data
        stock.unit_abbreviation = form.unit_abbreviation.data
        stock.reorder_levels = form.reorder_level.data
        flash("Updated Successfully", "success")

        db.session.commit()
        return redirect('/items')
    else:
        return render_template('update_item.html', form=form)

# Delete Item Route
@app.route('/delete_items/<int:id>/', methods=['GET', 'POST'])
def delete_items(id):

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    query = Stock.query.get_or_404(id)

    if request.method == 'POST':
        if query:
            db.session.delete(query)
            flash("Deleted Successfully", "success")
            db.session.commit()
            return redirect('/items')
    
    return render_template('delete_items.html')

# Details of single item Route
@app.route('/item_details/<int:id>/')
def item_details(id):
    if CURR_USER_KEY not in session:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    item = Stock.query.get_or_404(id)
    return render_template('item_detail.html', item=item)

# Issue Item Route
@app.route('/issue_items/<int:id>/', methods=['GET', 'POST'])
def issue_items(id):
    if CURR_USER_KEY not in session:
        flash("Access unauthorized.", "danger")
        return redirect("/")

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

    return render_template('issue_item.html', item=item, form=form)

# Receive Item Route
@app.route('/receive_items/<int:id>/', methods=['GET', 'POST'])
def receive_items(id):
    if CURR_USER_KEY not in session:
        flash("Access unauthorized.", "danger")
        return redirect("/")

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

    return render_template('receive_item.html', item=item, form=form)           

# Convert unit of meaurement Route
@app.route('/convert')
def convert():
    return render_template('convert_unit_form.html')

# Convert unit of meaurement Route
@app.route('/convert_unit', methods=['GET', 'POST'])
def convert_unit_form():
    if CURR_USER_KEY not in session:
        flash("Access unauthorized.", "danger")
        return redirect("/")


    ingredient = request.args.get('product')
    source_amount = request.args.get('quantity')
    source_unit = request.args.get('convertFrom')
    target_unit = request.args.get('convertTo')

    response = requests.get(f"{API_BASE_URL}", params={'apiKey':API_KEY, 
                                                        'ingredientName':ingredient, 
                                                        'sourceAmount':source_amount, 
                                                        'sourceUnit':source_unit, 
                                                        'targetUnit':target_unit}
    )

    data = response.json()
    result = data.get('answer')

    return render_template("convert_unit_form.html", result=result)
    # return redirect(url_for('convert'), result=result)

# @app.route('/add_convertion', methods=['GET', 'POST'])
# def add_convertion():

#     if not g.user:
#         flash("Access unauthorized", "danger")
#         return redirect("/")

#     if request.method == 'POST':
#         unit_name = request.form["name"]
#         unit_abbreviation = request.form["abbreviation"]

#         data = UnitConvertion(unit_abbreviation=unit_abbreviation, unit_name=unit_name )
#         db.session.add(data)
#         db.session.commit()
#         flash("Added Successfully", "success")
#         return redirect(url_for('convert'))

# @app.route('/add_convertion', methods = ['GET', 'POST'])
# def add_convertion():
#     if not g.user:
#         flash("Access unauthorized", "danger")
#         return redirect("/")

#     form = AddConvertion()

#     if form.validate_on_submit():
#         unit_name = form.unit_name.data
#         unit_abbreviation = form.unit_abbreviation.data

#         data = UnitConvertion(unit_name=unit_name, unit_abbreviation=unit_abbreviation)
#         db.session.add(data)
#         flash("Added Successfully", 'success')
#         db.session.commit()
#         return redirect(url_for('convert'))
#     else:
#         return render_template(convert_unit_form, form=form)