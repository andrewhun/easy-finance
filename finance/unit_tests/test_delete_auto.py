from .base import BaseUnitTestCase
from finance.models import Autovalue
from finance.views import delete_auto
from django.urls import reverse, resolve

class DeleteAutoCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of deleting recurring entries.
	This includes testing the /delete_auto/ url, the delete_auto view and
	the database operations involved in deleting recurring entries. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_recurring_entries_for_first_user()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_delete_auto_url(self):

		self.assertEqual(resolve(reverse("delete_auto")).func, delete_auto)

	# test that sending a GET request to the view results in an error message
	def test_delete_auto_get(self):

		response = self.client.get(reverse("delete_auto"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view handles POST requests
	def test_delete_auto_post(self):

		# test that incomplete input results in an error message
		invalid_response = self.client.post(reverse("delete_auto"))

		self.assertEqual(invalid_response.status_code, 200)
		self.assertIn("error_message", invalid_response.context)

		# test that the view deletes the selected recurring entry if the input is valid
		valid_response = self.client.post(reverse("delete_auto"), {"delete_id": 2})

		number_of_recurring_entries = super().count_recurring_entries_for_first_user()
		self.assertEqual(number_of_recurring_entries, 1)

		recurring_expense_count = len(Autovalue.objects.filter(title = "Expense"))
		self.assertEqual(recurring_expense_count, 0)

		self.assertEqual(valid_response.status_code, 302)
		self.assertEqual(valid_response.url, "/")