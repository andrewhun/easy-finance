import json
from .base import BaseUnitTestCase
from finance.views import change_pw
from django.urls import reverse, resolve

class ChangePwCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of changing
	passwords. This includes testing the /change_pw/ url, the change_pw
	view, change-pw.html and the database operations involved. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_change_pw_url(self):

		self.assertEqual(resolve(reverse("change_pw")).func, change_pw)

	# test that the view presents the change password form if it receives a GET request
	def test_change_pw_get(self):

		response = self.client.get(reverse("change_pw"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("<h1>Password change</h1>", str(response.content))

	# test that the view shows an error if it receives invalid input
	def test_change_pw_invalid_input(self):

		response = self.client.post(reverse("change_pw"), {"old_password": "testpass1",
			"new_password": "asd"})

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that view handles valid POST requests
	def test_change_pw_post(self):

		# test that the view returns an error if the input is incorrect
		incorrect_response = self.client.post(reverse("change_pw"), {"old_password": "test",
			"new_password": "asd", "confirmation": "asd"})
		self.assertIn(json.dumps({"error": "1"}), str(incorrect_response.content))

		# test that the view changes the user's password if the input is correct
		correct_response = self.client.post(reverse("change_pw"), {"old_password": "testpass1",
			"new_password": "asd", "confirmation": "asd"})

		super().log_current_user_out()
		self.assertTrue(self.client.login(username = "test1", password = "asd"))

		# test that the user is redirected to the main page
		self.assertEqual(correct_response.status_code, 302)
		self.assertEqual(correct_response.url, "/")