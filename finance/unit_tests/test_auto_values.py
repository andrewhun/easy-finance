from .base import BaseUnitTestCase
from finance.models import Autovalue
from finance.views import auto_values
from django.urls import reverse, resolve

class AutoValueCase(BaseUnitTestCase):
	''' This class is responsible for testing recurring entries.
	This includes testing the /auto_values/ url, the Autovalue model,
	the auto_values view and the database operations involved in
	adding recurring entries to a user's account. '''

	# set up the test database
	def setUp(self):

		super().setUp()
		super().add_recurring_entries_for_first_user()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_auto_values_url(self):

		self.assertEqual(resolve(reverse("auto_values")).func, auto_values)

	# test the Autovalue model
	def test_auto_values_model(self):

		recurring_entry = Autovalue.objects.get(user = self.test1, title = "Work")

		self.assertEqual("test1: Income of 50.00 USD recurring at Daily frequency", str(recurring_entry))

	# test that the view shows an error if it receives a GET request
	def test_auto_values_get(self):

		response = self.client.get(reverse("auto_values"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view handles POST requests
	def test_auto_values_post(self):

		# test that the view will show an error message if it receives incomplete input
		invalid_response = self.client.post(reverse("auto_values"), {"auto_title": "Groceries", 
			"auto_amount": 25.00, "frequency": "Weekly"})

		self.assertEqual(invalid_response.status_code, 200)
		self.assertIn("error_message", invalid_response.context)

		# test that the view creates a new recurring entry if it receives valid input
		valid_response = self.client.post(reverse("auto_values"), {"auto_type": "Expense", 
			"auto_title": "Groceries", "auto_amount": 25.00, "frequency": "Weekly"})

		self.assertEqual(valid_response.status_code, 302)
		self.assertEqual(valid_response.url, "/")

		number_of_recurring_entries = super().count_recurring_entries_for_first_user()
		self.assertEqual(number_of_recurring_entries, 3)

		new_recurring_entry = Autovalue.objects.get(value_type = "Expense", title = "Groceries")

		self.assertEqual("test1: Expense of 25.00 USD recurring at Weekly frequency", str(new_recurring_entry))