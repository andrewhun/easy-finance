import json
from finance.views import register
from .base import BaseUnitTestCase
from django.urls import reverse, resolve
from finance.models import Cash, Statement
from django.contrib.auth.models import User

class RegisterCase(BaseUnitTestCase):
	'''This class is responsible for testing the registration process.
	This includes testing the /register/ url, register.html, the register view and
	the database operations involved in registering new users.'''

	# set up the test database
	def setUp(self):

		super().setUp()
		super().add_second_user()

	# test that the url works and is connected to the view
	def test_register_url(self):

		self.assertEqual(resolve(reverse("register")).func, register)
	
	# test that logged in users are logged out if they navigate to the register page
	def test_register_log_user_out(self):

		# log in the test client
		super().login_as_first_user()

		# navigate to the index page
		response = self.client.get(reverse("index"))

		# the index page is supposed to load for logged in users
		self.assertEqual(response.status_code, 200)
		
		# navigate to the register page
		self.client.get(reverse("register"))
		
		# navigate to the index page again
		response2 = self.client.get(reverse("index"))

		# the index page is supposed to redirect users that are not logged in to the login page
		self.assertEqual(response2.status_code, 302)
		self.assertEqual(response2.url, "/login/")


	# test that the register form loads when a GET request is sent to the url
	def test_register_get(self):

		response = self.client.get(reverse("register"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("<form id = \\\'register\\\' action=\\\'/register/\\\' method=\\\'POST\\\'>", str(response.content))
		self.assertIn("</form>", str(response.content))
		

	# test that the program does not accept invalid input
	def test_register_username_taken(self):


		response = self.client.post(reverse("register"), {"username": "test1", "password": "testpass",
			"confirmation": "testpass"})
		error = {"error": "1"}
		self.assertIn(json.dumps(error), str(response.content))
	
	# test that the view returns shows an error message if the input is invalid
	def test_register_invalid_input(self):

		response = self.client.post(reverse("register"), {"username": "test3", "password": "testpass3",
		"starting_balance": 1000.00})

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test the register view's reaction to valid input
	def test_register_valid_input(self):

		response = self.client.post(reverse("register"), {"username": "test3", "password": "testpass3",
		"confirmation": "testpass3", "starting_balance": 1000.00})

		# test that the user is logged in and redirected to the main page upon successful registration
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, "/")

		# test that a new user is created when the user's input is valid
		number_of_users = len(User.objects.all())
		self.assertEqual(number_of_users, 3)	
	
		# test that the user's starting balance is set according to their input
		third_user = User.objects.get(username = "test3")
		third_balance = Cash.objects.get(user = third_user).cash
		self.assertEqual(third_balance, 1000.00)

		# test that the users starting balance is added to the financial statements table correctly
		number_of_statement_entries = len(Statement.objects.all())
		self.assertEqual(number_of_statement_entries, 3)

		third_starting_statement = Statement.objects.get(user = third_user, title = "Starting balance")
		self.assertEqual(third_starting_statement.amount, 1000.00)

	# test that the application sets the default starting balance for users
	def test_register_default_balance(self):
		
		self.client.post(reverse("register"), {"username": "test4", "password": "testpass4",
		"confirmation": "testpass4", "starting_balance": ""})

		fourth_user = User.objects.get(username = "test4")
		fourth_balance = Cash.objects.get(user = fourth_user).cash
		self.assertEqual(fourth_balance, 10000.00)

		number_of_users = len(User.objects.all())
		self.assertEqual(number_of_users, 3)

		number_of_statement_entries = len(Statement.objects.all())
		self.assertEqual(number_of_statement_entries, 3)

		fourth_starting_statement = Statement.objects.get(user = fourth_user, title = "Starting balance")
		self.assertEqual(fourth_starting_statement.amount, 10000.00)