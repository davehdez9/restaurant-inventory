from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

# MODELS -> 
class User(db.Model):
    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)
    user_inventory = db.Column(db.Integer, db.ForeignKey('inventory.id'))

    inv = db.relationship('Inventory', backref='users')

    def _repr__(self):
        p=self
        return f"<User first_name={p.first_name} last_name={p.last_name} user_inventory={p.user_inventory}> "

class Inventory(db.Model):
    __tablename__='inventory'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    amount_in_stock = db.Column(db.Float, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

    # vendor = db.relationship('Vendor', backref='inventory')
    # product = db.relationship('Product', backref="inventory")

    def _repr__(self):
        p=self
        return f"<Inventory product_id={p.product_id} amount_in_stock={p.amount_in_stock}>"


class Vendor(db.Model):
    __tablename__='vendors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor_name = db.Column(db.String, nullable=False)
    vendor_description = db.Column(db.String, nullable=False)
    contact_name = db.Column(db.String, nullable=False)
    contact_email = db.Column(db.String, unique=True, nullable=False)
    vendor_website = db.Column(db.String, unique=True, nullable=False)
    vendor_notes = db.Column(db.String, unique=True, nullable=False)

    inv = db.relationship('Inventory', backref='vendor')
    
class Product(db.Model):
    __tablename__='products'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_name = db.Column(db.String, nullable=False)
    product_description = db.Column(db.String, nullable=False)
    unit_measurement = db.Column(db.String, nullable=False)
    package_amount = db.Column(db.String, unique=True, nullable=False)
    price_per_package = db.Column(db.Float, unique=True, nullable=False)
    
    inv = db.relationship('Inventory', backref='product')


# DROP TABLE users
    