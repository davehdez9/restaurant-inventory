"""Views Tests"""

# run the test like:
#     python -m unittest test_views.py

import os
import requests
from unittest import TestCase

from werkzeug.utils import html, redirect
from app import app, CURR_USER_KEY, API_BASE_URL
from secrets import API_KEY
from models import db, connect_db, User, Stock
from flask import session, g


os.environ['DATABASE_URL'] = 'postgresql:///restaurant_inventory_test'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False
app.config["PRESERVE_CONTEXT_ON_EXCEPTION"] = False

db.drop_all()
db.create_all()

class AppViewTestCase(TestCase):
    
    def setUp(self):
        """Create test client and sample data"""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        self.testuser = User.signup(email="test1@test.com",
                                    username="test1",
                                    password="test123")

        self.testuser_id = 123
        self.testuser.id = self.testuser_id

        self.u2 = User.signup('test2@test.com', 'test2', 'test456')
        self.u2_id = 456
        self.u2.id = self.u2_id

        self.u3 = User.signup('test3@test.com', 'test3', 'test789')
        self.u3_id = 789
        self.u3.id = self.u3_id

        db.session.commit()
    
    def teardown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_landing_page(self):
        with self.client as client:
            # import pdb
            # pdb. set_trace()
            res = client.get("/")

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>Inventory App - Landing Page</h1>", str(res.data))

    def test_signUp_form(self):
        with self.client as client:
            res = client.get('/signUp')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<form method="POST">', html)
    
    def test_signUp_add_user(self):
        with self.client as client:
            u = {"email":"supertest@test.com", "username":"supertest", "password":"supertest"}
            res = client.post("/signUp", data=u, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>Welcome</h1>", html)
            self.assertNotIn('<form method="POST">', html)
        
    def test_login_form(self):
        with self.client as client:
            res = client.get('/login')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1 class="display-1">Login</h1>', html)

    def test_login_redirection(self):
        with self.client as client:
            # u = User.authenticate(self.testuser.username, 'test456')
            u = {"username": self.u2.username, "password":'test456'}
            res = client.post("/login", data=u, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>Welcome</h1>", html)
            
    def test_logout_user(self):
        with self.client as client:
            res = client.get('/logout')

            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/login')

    def test_logout_redirection(self):
        with self.client as client:
            res = client.get('/logout', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1 class="display-1">Login</h1>', html)

    def test_user_profile(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = client.get("/users/profile")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<p>To confirm changes, enter your password:</p>', html)
    
    def test_user_profile_update(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            upd = {"username": "testupdated", "email": "updated@test.com", 'password': 'test123'}
            resp = client.post("/users/profile", data=upd)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 302)
            user = User.query.get(self.testuser_id)
            self.assertEqual(user.username, 'testupdated')
            self.assertEqual(user.email, 'updated@test.com')
        
    # def test_delete_user(self):
 
    def test_home_page(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = client.get("/home")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Welcome</h1>', html)

    #------------------------------- Stock Routes
    def test_list_items(self):
        with self.client as client:
            res = client.get('/items')
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>List of Items</h1>", html)
            
    def test_add_items_form(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            res = client.get('/add_item')
            html = res.get_data(as_text=True)
        
            self.assertEqual(res.status_code, 200)
            self.assertIn('<button class="btn btn-success" type="submit">Add</button>', html)
    
    def test_add_items(self):
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            p = {"category":"Meat", "product_name":"Bacon", "quantity":100, "unit_measurement":"gr"}
            res = client.post("/add_item", data=p, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("Added Successfully", html)
            self.assertNotIn('<button class="btn btn-success" type="submit">Add</button>', html)
    
    def test_update_items_forms(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            p = Stock.query.get(1)
            res = client.get(f"/update_item/{p.id}/")
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button class="btn btn-success" type="submit">Add</button>', html)
    
    def test_update_items(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            p = Stock.query.get(1)
            update = {"category":"Meat", "product_name":"Steak", "quantity":200, "unit_measurement":"kg"}
            res =  client.post(f'/update_item/{p.id}/', data=update, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Meat', html)

            stock = Stock.query.get(1)
            self.assertEqual(stock.product_name, 'Steak')

    def test_delete_items(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            p = Stock.query.get(1)
            res = client.get(f'/delete_items/{p.id}/', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<h1>Are you sure you want to delete?</h1>', html)

    def test_delete_items_post(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            res = client.post(f'/delete_items/1/', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)

            p = Stock.query.get(1)
            self.assertIsNone(p)
            
    def test_item_details(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()

        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            res = client.get(f'/item_details/1/', follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<th>LAST UPDATED</th>', html)

    def test_issue_items_form(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            res = client.get(f'/issue_items/1/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button class="btn btn-success" type="submit">Add</button>', html)

    def test_issue_items(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=200,
            unit_measurement = 'gr',
        )
        db.session.add(p)
        db.session.commit()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            q = {"issue_quantity":100}
            res = client.post(f'/issue_items/1/', data=q, follow_redirects=True)
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<td>100</td>', html)
    
    def test_receive_items_forms(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            res = client.get(f'/receive_items/1/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button class="btn btn-success" type="submit">Add</button>', html)

    def test_receive_items(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            q = {"receive_quantity":100}
            res = client.post(f'/receive_items/1/', data=q, follow_redirects=True)
            html = res.get_data(as_text=True)


            self.assertEqual(res.status_code, 200)
            self.assertIn('<td>200</td>', html)

    def test_reorder_levels_form(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            res = client.get(f'/reorder_level/1/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('<button class="btn btn-success" type="submit">Add</button>', html)

    def test_reorder_levels(self):
        p = Stock(
            id=1,
            category='Meat',
            product_name='Salami',
            quantity=100,
            unit_measurement = 'gr'
        )
        db.session.add(p)
        db.session.commit()
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            q = {"reorder_level":200}
            res = client.post(f'/reorder_level/1/', data=q, follow_redirects=True)
            html = res.get_data(as_text=True)


            self.assertEqual(res.status_code, 200)
            self.assertIn('<td><a href="/reorder_level/1">200</a></td>', html)

    # def test_convert_unit(self):
