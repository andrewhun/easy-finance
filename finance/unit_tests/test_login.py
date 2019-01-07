import json
from .base import BaseUnitTestCase
from finance.views import login_view
from django.urls import reverse, resolve

class LoginCase(BaseUnitTestCase):
	''' This class is responsible for testing the login process.
	This includes testing the /login/ url, login.html and login_view.'''

	# set up the test database
	def setUp(self):

		super().setUp()

	# test that the url is connected to login_view
	def test_login_url(self):

		self.assertEqual(resolve(reverse("login")).func, login_view)

	# test that the view presents the login form when it receives a GET request
	def test_login_get(self):

		response = self.client.get(reverse("login"))

		self.assertIn(" <form id = \\\'login\\\' action=\\\'/login/\\\' method=\\\'post\\\'>", str(response.content))
		self.assertIn("</form>", str(response.content))

	# test that logged in users are logged out when they navigate to the url
	def test_login_log_user_out(self):

		# log in the test client
		super().login_as_first_user()

		# navigate to the index page
		response = self.client.get(reverse("index"))

		# the index page is supposed to load for logged in users
		self.assertEqual(response.status_code, 200)
		
		# navigate to the register page
		self.client.get(reverse("login"))
		
		# navigate to the index page again
		response2 = self.client.get(reverse("index"))

		# the index page is supposed to redirect users that are not logged in to the login page
		self.assertEqual(response2.status_code, 302)
		self.assertEqual(response2.url, "/login/")

	
	# test that the view reacts appropriately to incorrect input
	def test_login_incorrect_credentials(self):
		
		# invalid user
		response = self.client.post(reverse("login"), {"username": "test", "password": "secret"})
		error = {"error": "1"}
		self.assertIn(json.dumps(error), str(response.content))
		
		# invalid password
		response2 = self.client.post(reverse("login"), {"username": "test1", "password": "secret"})
		self.assertIn(json.dumps(error), str(response2.content))
	
	# test that the view shows an error message if the input is invalid
	def test_login_invalid_input(self):

		response = self.client.post(reverse("login"), {"username": "test1"})

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view logs users in when they pass in valid crendentials
	def test_login_valid_input(self):

		response = self.client.post(reverse("login"), {"username": "test1", "password": "testpass1"})

		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, "/")