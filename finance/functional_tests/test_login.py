from finance.helpers import wait_for
from .base import BaseFunctionalTestCase

class LoginCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the login process from the user's
	point of view. This includes testing the application's reactions to both
	valid and invalid inputs. '''

	# set up for the test
	def setUp(self):

		super().setUp()

	# close the browser after each test
	def tearDown(self):

		super().tearDown()

	# test that the username and password fields are required
	def test_login_required_fields(self):

		username_input = self.driver.find_element_by_id("login_user")
		wait_for(lambda: self.assertTrue(username_input.get_attribute("required")))

		password_input = self.driver.find_element_by_id("login_pw")
		wait_for(lambda: self.assertTrue(password_input.get_attribute("required")))

	# test that the user can log in using the form
	def test_login_valid_input(self):

		username_input = self.driver.find_element_by_id("login_user")
		username_input.send_keys("test1")

		password_input = self.driver.find_element_by_id("login_pw")
		password_input.send_keys("testpass1")

		self.driver.find_element_by_id("login").submit()

		wait_for(lambda: self.assertIn("Main page", self.driver.title))

	# test that an error message is shown if the user's input is invalid
	def test_login_invalid_input(self):

		username_input = self.driver.find_element_by_id("login_user")
		username_input.send_keys("test2")

		password_input = self.driver.find_element_by_id("login_pw")
		password_input.send_keys("testpass1")

		self.driver.find_element_by_id("login").submit()

		error_message_div = self.driver.find_element_by_id("loginuser")
		wait_for(lambda: self.assertEqual("Invalid username or password", error_message_div.text))