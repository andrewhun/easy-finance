from finance.helpers import wait_for
from .base import BaseFunctionalTestCase
from django.contrib.auth import authenticate

class ChangePwCase(BaseFunctionalTestCase):
	''' This class is responsible for testing the functions of the change password form.
	This includes testing the application's reactions to correct and incorrect input
	being entered through this form. '''

	# set up for the tests
	def setUp(self):

		super().setUp()
		super().log_test_user_in()
		super().navigate_to_change_pw()

		# place all form elements into variables
		self.old_password_input = self.driver.find_element_by_id("old_pw")
		self.new_password_input = self.driver.find_element_by_id("new_pw")
		self.change_confirmation_input = self.driver.find_element_by_id("change_confirmation")
		self.change_pw_form = self.driver.find_element_by_id("change_pw")

	# close the browser after running each test
	def tearDown(self):

		super().tearDown()

	# test that all fields are required in the change password form
	def test_change_pw_fields_are_required(self):

		wait_for(lambda: self.assertTrue(self.old_password_input.get_attribute("required")))

		wait_for(lambda: self.assertTrue(self.new_password_input.get_attribute("required")))

		wait_for(lambda: self.assertTrue(self.change_confirmation_input.get_attribute("required")))

	# test that users are notified if they entered they old password incorrectly
	def test_change_pw_old_pw_incorrect(self):

		self.old_password_input.send_keys("wrong!")

		self.new_password_input.send_keys("asd")

		self.change_confirmation_input.send_keys("asd")

		self.change_pw_form.submit()

		old_pw_error = self.driver.find_element_by_id("oldpw")
		wait_for(lambda: self.assertEqual("Old password does not match records", old_pw_error.text))

	# test that users are notified if their old and new passwords are the same
	def test_change_pw_old_and_new_are_the_same(self):

		self.old_password_input.send_keys("asd")

		self.new_password_input.send_keys("asd")

		self.change_confirmation_input.send_keys("asd")

		self.change_pw_form.submit()

		new_pw_error = self.driver.find_element_by_id("newpw")
		wait_for(lambda: self.assertEqual("Old and new passwords are the same", new_pw_error.text))

	# test that users are notified if they failed to confirm their new password
	def test_change_pw_confirmation_failed(self):

		self.old_password_input.send_keys("testpass1")

		self.new_password_input.send_keys("asd")

		self.change_confirmation_input.send_keys("dsa")

		self.change_pw_form.submit()

		change_confirmation_error = self.driver.find_element_by_id("changeconf")
		wait_for(lambda: self.assertEqual("The new password and its confirmation do not match",
		 change_confirmation_error.text))

	# test that users can change their passwords if they enter correct input
	def test_change_password(self):

		self.old_password_input.send_keys("testpass1")

		self.new_password_input.send_keys("secret")

		self.change_confirmation_input.send_keys("secret")

		self.change_pw_form.submit()

		# wait for the client to be redirected to the main page
		wait_for(lambda: self.assertIn("Main page", self.driver.title))

		reauthenticated_user = authenticate(username = "test1", password = "secret")
		wait_for(lambda: self.assertEqual(self.test1, reauthenticated_user))