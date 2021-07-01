"""Seed file to make sample data fro pets db."""

from models import db
from app import app

#----- create database in terminal
# createdb restaurant_inventory_db      

# Create all tables
db.drop_all()
db.create_all()

db.session.commit()
