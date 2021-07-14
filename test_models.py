"""Models Tests"""

# run the test like:
#     python -m unittest test_models.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Stock

os.environ['DATABASE_URL'] = 'postgresql:///restaurant_inventory_test'

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    """Test views for User"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("test1@test.com", 'test1', 'test123')
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2@test.com", 'test2', 'test456')
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    # signup test

    def test_valid_signup(self):
        u_test = User.signup("test3@test.com", "test3", "test789")
        uid = 3333
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, 'test3')
        self.assertEqual(u_test.email, 'test3@test.com')
        self.assertNotEqual(u_test.password, 'test789')
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup("test4@test.com", None, 'test987')
        uid = 4444
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup(None, 'test5', 'test654')
        uid = 5555
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup('test6@test.com', 'test6', '')
        with self.assertRaises(ValueError) as context:
            User.signup('test6@test.com', 'test6', None)

    # Authentication Test
    
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, 'test123')
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("notusername", "test123"))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "wrongpass"))