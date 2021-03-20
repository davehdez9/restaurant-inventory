"""Seed file to make sample data fro pets db."""

from models import User, Inventory, Vendor, Product, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table is not empty, empty it
Vendor.query.delete()
Product.query.delete()

# Add Users
david = User(first_name="David", last_name="Hernandez", email="david@rosso.com", password="test123", user_inventory=1)
daisy = User(first_name="Daisy", last_name="Mesa", email="daisy@rosso.com", password="test456", user_inventory=2)
luz = User(first_name="Luz", last_name="Lagos", email="Luz@rosso.com", password="test789", user_inventory=2)

# Add Inventory
inv1 = Inventory(product_id=1, amount_in_stock=12, vendor_id=1)
inv2 = Inventory(product_id=2, amount_in_stock=2, vendor_id=2)

# Add Products

bufala = Product(product_name="Mozz Bufala", product_description="Cheese", unit_measurement="gr", package_amount="12/250gr", price_per_package=42)
cheese = Product(product_name="Mozz Cheese", product_description="Cheese", unit_measurement="lb", package_amount="2/5lb", price_per_package=43.93)
salame = Product(product_name="Salame Spicy", product_description="Meet", unit_measurement="lb", package_amount="4/1.323lb", price_per_package=54.95)
basil = Product(product_name="Basil", product_description="Veggie", unit_measurement="lb", package_amount="2/1lb", price_per_package=16.10)
pomodoro = Product(product_name="Pomodoro", product_description="Veggie", unit_measurement="kg", package_amount="1/3kg", price_per_package=20.35)

# Add Vendors

acendico = Vendor(vendor_name="AceEndico", vendor_description="Food Services", contact_name="Alberto", contact_email="Alberto@aceendico.com", vendor_website="www.aceendico.com", vendor_notes="3 Orders a week" )
baldor = Vendor(vendor_name="Baldor", vendor_description="Food Services", contact_name="Amanda", contact_email="Amanda@baldor.com", vendor_website="www.baldor.com", vendor_notes="order every day" )


# Add new objects to session, so theyw will persist
db.session.add(bufala)
db.session.add(cheese)
db.session.add(salame)
db.session.add(basil)
db.session.add(pomodoro)

db.session.add(acendico)
db.session.add(baldor)

db.session.add(david)
db.session.add(daisy)
db.session.add(luz)

db.session.add(inv1)
db.session.add(inv2)

db.session.commit()










db.session.commit()


# Commit -- otherwise, this never gets saved!
