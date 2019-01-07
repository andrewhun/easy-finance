from finance.models import Cash
from finance.helpers import wait_for
from .base import BaseFunctionalTestCase
from django.contrib.auth.models import User

class RegisterCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the registration process
	from the user's point of view. This includes testing it with valid
	input and testing if the application reacts appropriately to different
	kinds of invalid input. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().navigate_to_register()

	# close the browser after each test
	def tearDown(self):

		super().tearDown()

	# test that the username, password and confirmation fields are required
	def test_register_required_fields(self):

		username_input = self.driver.find_element_by_id("reg_username")
		wait_for(lambda: self.assertTrue(username_input.get_attribute("required")))

		password_input = self.driver.find_element_by_id("reg_pw")
		wait_for(lambda: self.assertTrue(password_input.get_attribute("required")))

		confirmation_input = self.driver.find_element_by_id("reg_confirmation")
		wait_for(lambda: self.assertTrue(confirmation_input.get_attribute("required")))

	# test that the app notifies users about password mismatches
	def test_register_password_mismatch(self):

		username_input = self.driver.find_element_by_id("reg_username")
		username_input.send_keys("test2")

		password_input = self.driver.find_element_by_id("reg_pw")
		password_input.send_keys("asd")

		confirmation_input = self.driver.find_element_by_id("reg_confirmation")
		confirmation_input.send_keys("dsa")

		password_error_div = self.driver.find_element_by_id("regpw")

		register_form = self.driver.find_element_by_id("register")
		register_form.submit()

		wait_for(lambda: self.assertEqual("The password and its confirmation do not match", password_error_div.text))

	# test that the app notifies users about using usernames that are taken
	def test_register_username_taken(self):

		username_input = self.driver.find_element_by_id("reg_username")
		username_input.send_keys("test1")

		password_input = self.driver.find_element_by_id("reg_pw")
		password_input.send_keys("asd")

		confirmation_input = self.driver.find_element_by_id("reg_confirmation")
		confirmation_input.send_keys("asd")

		username_error_div = self.driver.find_element_by_id("regusername")

		register_form = self.driver.find_element_by_id("register")
		register_form.submit()

		wait_for(lambda: self.assertEqual("Username already taken", username_error_div.text))

	# test that users can register if they enter valid credentials
	def test_register_valid_input(self):

		username_input = self.driver.find_element_by_id("reg_username")
		username_input.send_keys("test2")

		password_input = self.driver.find_element_by_id("reg_pw")
		password_input.send_keys("asd")

		confirmation_input = self.driver.find_element_by_id("reg_confirmation")
		confirmation_input.send_keys("asd")

		starting_balance_input = self.driver.find_element_by_id("starting_balance")
		starting_balance_input.send_keys("7500")

		register_form = self.driver.find_element_by_id("register")
		register_form.submit()

		# test that the user is redirected to the main page
		wait_for(lambda: self.assertIn("Main page", self.driver.title))

		# test that the user has the specified starting balance
		test2 = User.objects.get(username = "test2")
		current_user_balance = Cash.objects.get(user = test2).cash
		wait_for(lambda: self.assertEqual(7500, current_user_balance))

	# test that the app assigns the default starting balance to the user's account if they don't specify it
	def test_register_starting_balance(self):
		
		username_input = self.driver.find_element_by_id("reg_username")
		username_input.send_keys("test2")

		password_input = self.driver.find_element_by_id("reg_pw")
		password_input.send_keys("asd")

		confirmation_input = self.driver.find_element_by_id("reg_confirmation")
		confirmation_input.send_keys("asd")

		register_form = self.driver.find_element_by_id("register")
		register_form.submit()

		# test that the user is redirected to the main page
		wait_for(lambda: self.assertIn("Main page", self.driver.title))

		# test that the user has the default starting balance
		test2 = User.objects.get(username = "test2")
		current_user_balance = Cash.objects.get(user = test2).cash
		wait_for(lambda: self.assertEqual(10000.00, current_user_balance))