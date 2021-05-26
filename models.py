from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()

bcrypt = Bcrypt()

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
    # user_inventory = db.Column(db.Integer, db.ForeignKey('inventory.id'))

    # inv = db.relationship('Inventory', backref='users')

    @property
    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "password": self.password,
            "user_inventory": self.user_inventory,
        }

    def _repr__(self):
        p=self
        return f"<User first_name={p.first_name} last_name={p.last_name} user_inventory={p.user_inventory}> "

    @classmethod
    def signup(cls, first_name, last_name, email, password):
        """Register user w/hashed password & return user."""

        # turn bytestring into normal (unicode utf8) string
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            first_name=first_name, 
            last_name=last_name, 
            email=email,
            password=hashed_pwd
        )

        db.session.add(user)
        
        return user
        # return cls(first_name=first_name, last_name=last_name, email=email, password=hashed_utf8)

    @classmethod
    def authenticate(cls, email, password):
        """Validate that user exists & password is correct. 
        
        Return use if valid; else return false.
        """

        user = cls.query.filter_by(email=email).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False

class Stock(db.Model):
    __tablename__='stock_history'
    # __searchable__ = ['category', 'product_name']  # these fields will be indexed by whoosh

    id = db.Column(db.Integer, primary_key=True, autoincrement= True)
    category = db.Column(db.String(50))
    product_name = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=0)
    receive_quantity = db.Column(db.Integer, default=0)
    receive_by = db.Column(db.String(50))
    issue_quantity = db.Column(db.Integer, default=0)
    issue_by = db.Column(db.String(50))
    issue_to = db.Column(db.String(50))
    phone_number = db.Column(db.String(50))
    create_by = db.Column(db.String(50))
    reorder_levels = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # export_to_csv = db.Column(db.Boolean, default=False)

    def __repr__(self):
        p=self
        return f"<Category={p.category} Product_name={p.product_name} Quantity={p.quantity}>"

# class Category(db.Model):
#     __tablename__='category'

#     id = db.Column(db.Integer, primary_key=True, autoincrement= True)
#     name = db.Column(db.String(50))
#     stock = db.relationship("Stock", cascade="all, delete-orphan", passive_deletes=True)

# class StockHistory(db.Model):
#     __tablename__='stock'
#     # __searchable__ = ['category', 'product_name']  # these fields will be indexed by whoosh

#     id = db.Column(db.Integer, primary_key=True, autoincrement= True)
#     # category = db.Column(db.Integer, db.ForeignKey('category.id',ondelete="cascade"))
#     category = db.Column(db.String(50))
#     product_name = db.Column(db.String(50))
#     quantity = db.Column(db.Integer, default=0)
#     receive_quantity = db.Column(db.Integer, default=0)
#     receive_by = db.Column(db.String(50))
#     issue_quantity = db.Column(db.Integer, default=0)
#     issue_by = db.Column(db.String(50))
#     issue_to = db.Column(db.String(50))
#     phone_number = db.Column(db.String(50))
#     create_by = db.Column(db.String(50))
#     reorder_levels = db.Column(db.Integer, default=0)
#     timestamp = db.Column(db.DateTime, default=datetime.now)
#     last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    # export_to_csv = db.Column(db.Boolean, default=False)



# class Inventory(db.Model):
#     __tablename__='inventory'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
#     amount_in_stock = db.Column(db.Float, nullable=False)
#     vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))

#     # vendor = db.relationship('Vendor', backref='inventory')
#     # product = db.relationship('Product', backref="inventory")

#     def _repr__(self):
#         p=self
#         return f"<Inventory product_id={p.product_id} amount_in_stock={p.amount_in_stock}>"

# class Vendor(db.Model):
#     __tablename__='vendors'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     vendor_name = db.Column(db.String, nullable=False)
#     vendor_description = db.Column(db.String, nullable=False)
#     contact_name = db.Column(db.String, nullable=False)
#     contact_email = db.Column(db.String, unique=True, nullable=False)
#     vendor_website = db.Column(db.String, unique=True, nullable=False)
#     vendor_notes = db.Column(db.String, unique=True, nullable=False)

#     inv = db.relationship('Inventory', backref='vendor')

#     def serialize(self):
#         return {
#             "id": self.id,
#             "vendor_name": self.vendor_name,
#             "vendor_description": self.vendor_description,
#             "contact_name": self.contact_name,
#             "contact_email": self.contact_email,
#             "vendor_website": self.vendor_website,
#             "vendor_notes": self.vendor_notes
#         }
        
# class Product(db.Model):
#     __tablename__='products'

#     id = db.Column(db.Integer, primary_key=True)
#     product_name = db.Column(db.String, nullable=False)
#     product_description = db.Column(db.String, nullable=False)
#     unit_measurement = db.Column(db.String, nullable=False)
#     package_amount = db.Column(db.String, unique=True, nullable=False)
#     price_per_package = db.Column(db.Float, unique=True, nullable=False)
    
#     inv = db.relationship('Inventory', backref='product')

#     def serialize(self):
#         return {
#             "id": self.id,
#             "product_name": self.product_name,
#             "product_description": self.product_description,
#             "unit_measurement": self.unit_measurement,
#             "package_amount": self.package_amount,
#             "price_per_package": self.price_per_package
#         }
