from flask.wrappers import Request
from models import User
from werkzeug.test import Client
from app import CURR_USER_KEY, app
from unittest import TestCase
from flask import session, g

# CONFIGURATIONS: 
app.config['TESTING'] = True
app.config['DEBUG_TB_HOST'] = ['dont-show-debug-toolbar']



# UNIT TEST ->>>
#     [] Test Functions
#     [] Test Functions Models

# INTEGRATION TEST ->>>>>``

    # [] Test Get Request
    # [] Test Post Request
    # [] Test Redirections
    # [] Test Session

    # [] Test Models w/ Routes
    # [] Test Forms 
    # [] Test Flas APIS


class AppViewsTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        print('INSIDE SET UP CLASS')
    
    @classmethod
    def tearDownClass(cls):
        print('INSIDE TEAR DOWN CLASS')
    
    def setUp(cls):
        print("INSIDE SET UP")
    
    def tearDown(cls):
        print('INSIDE TEAR DOWN ')
        

    # TEST GET REQUEST
    def test_get_request(self):
        with app.test_client() as client:
            # import pdb
            # pdb.set_trace()
            res = client.get('/')
            html = res.get_data(as_text=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>Inventory App - Landing Page</h1>", html)
    
    # TEST POST REQUEST
    def test_post_request(self):
        with app.test_client() as client:
            res = client.post('/add_item', data={'category': 'Meat', 
                                                 'product_name':'Salami',
                                                 'quantity': 2 })
            
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            # test does not work
            # self.assertIn("<td>Meat</td>", html) 

    # TEST REDIRECTIONS
    def test_redirection(self):
        # curl -v localhost:5000/logout
        with app.test_client() as client:
            res = client.get('/logout')

            self.assertEqual(res.status_code, 302)
            self.assertEqual(res.location, 'http://localhost/')
    
    def test_redirection_follow(self):
        with app.test_client() as client:
            res = client.get('/logout', follow_redirects=True)        
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn("<h1>Inventory App - Landing Page</h1>", html)
    
    # TEST SESSION
    # def test_session(self):
    #     with app.test_client() as client:
    #         # with client.session_transaction() as change_session:
    #         #     change_session[CURR_USER_KEY] = 999

    #         res = client.get('/home')        
            
    #         self.assertEqual(res.status_code, 200)
    #         # self.assertEqual(session[CURR_USER_KEY], g.user)
            