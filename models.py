"""SQLAlchemy models for the Inventory App."""
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect this database to provide flask app.

    Call this the Flask App
    
    """
    db.app = app
    db.init_app(app)

# MODELS -> 
class User(db.Model):
    """User in the system"""

    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    Stock  = db.relationship('Stock', backref='user', cascade='all, delete')

    def _repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, email, username, password):
        """Register user w/hashed password & return user."""

        # turn bytestring into normal (unicode utf8) string
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            email=email,
            username=username,
            password=hashed_pwd
        )

        db.session.add(user)
        return user
        # return cls(first_name=first_name, last_name=last_name, email=email, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct. 
        
        Return use if valid; else return false.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        
        return False

class Stock(db.Model):
    __tablename__='stock_history'

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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    unit_abbreviation = db.Column(db.String(50))

    # unit_abbreviation = db.Column(db.Text, db.ForeignKey('unit_convertion.unit_abbreviation'))

    # abv = db.relationship('UnitConvertion', back_populates="stock")
    # abv = db.relationship('UnitConvertion', backref="stock_histories")

    def __repr__(self):
        p=self
        return f"<Category={p.category} Product_name={p.product_name} Quantity={p.quantity}>"

class UnitConvertion(db.Model):
    __tablename__='unit_convertion'
    
    unit_abbreviation = db.Column(db.Text, primary_key=True, nullable=False, unique=True)
    unit_name = db.Column(db.Text, nullable=False, unique=True)

    # stock = db.relationship('Stock', back_populates="abv")
    # stock = db.relationship('Stock', backref='unit_convertions')
    
    

    def _repr_(self):
        p=self
        return f"<Unit_Abbreviation={p.unit_abbreviation} Unit_Name={p.unit_name} stock={p.stock} >"
    

    
    
