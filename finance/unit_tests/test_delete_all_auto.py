from .base import BaseUnitTestCase
from finance.models import Autovalue
from django.urls import reverse, resolve
from finance.views import delete_all_auto

class DeleteAllAutoCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of removing all
	recurring entries that belong to a user. This includes testing the
	/delete_all_auto/ url, the delete_all_auto view and the database operations
	involved in deleting multiple recurring entries. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_recurring_entries_for_first_user()
		super().add_second_user()
		super().add_recurring_entries_for_second_user()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_delete_all_auto_url(self):

		self.assertEqual(resolve(reverse("delete_all_auto")).func, delete_all_auto)

	# test that a GET request sent to the view results in an error message
	def test_delete_all_auto_get(self):

		response = self.client.get(reverse("delete_all_auto"))

		self.assertIn("error_message", response.context)
		self.assertEqual(response.status_code, 200)

	# test that the view handles POST requests
	def test_delete_all_auto_post(self):

		# test that incomplete input results in an error message
		invalid_response = self.client.post(reverse("delete_all_auto"))

		self.assertIn("error_message", invalid_response.context)
		self.assertEqual(invalid_response.status_code, 200)

		# test that the view removes all recurring entries that belong to the current user if the input is valid
		valid_response = self.client.post(reverse("delete_all_auto"), {"delete_all_check": "check"})

		first_user_recurring_entries_count = super().count_recurring_entries_for_first_user()
		self.assertEqual(first_user_recurring_entries_count, 0)

		self.assertEqual(valid_response.status_code, 302)
		self.assertEqual(valid_response.url, "/")

		# test that other users' recurring entries are unaffected
		second_user_recurring_entries_count = super().count_recurring_entries_for_second_user()
		self.assertEqual(second_user_recurring_entries_count, 2)