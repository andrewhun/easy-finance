from .base import BaseUnitTestCase
from finance.views import edit_auto
from finance.models import Autovalue
from django.urls import reverse, resolve

class EditAutoCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of editing recurring entries.
	This includes testing the /edit_auto/ url, the edit_auto view
	and the database operations involved in editing recurring entries. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_recurring_entries_for_first_user()
		super().login_as_first_user()

	# test that the url is connected to the view
	def test_edit_auto_url(self):

		self.assertEqual(resolve(reverse("edit_auto")).func, edit_auto)

	# test that the view shows an error message if it receives a GET request
	def test_edit_auto_get(self):

		response = self.client.get(reverse("edit_auto"))
		self.assertIn("error_message", response.context)
		self.assertEqual(response.status_code, 200)

	# test that the view handles POST requests
	def test_edit_auto_post(self):

		# test that the view shows an error message if it receives incomplete input
		invalid_response = self.client.post(reverse("edit_auto"), {"edit_type": "Income",
			"edit_title": "Interest", "edit_amount": 10.00, "edit_frequency": "Monthly"})
		
		self.assertIn("error_message", invalid_response.context)
		self.assertEqual(invalid_response.status_code, 200)

		# test that the view changes the selected recurring entry if it receives valid input
		valid_response = self.client.post(reverse("edit_auto"), {"edit_id": 2, "edit_type": "Income",
			"edit_title": "Interest", "edit_amount": 10.00, "edit_frequency": "Monthly"})
		
		self.assertEqual(valid_response.status_code, 302)
		self.assertEqual(valid_response.url, "/")
		edited_entry = Autovalue.objects.get(title = "Interest")
		self.assertEqual("test1: Income of 10.00 USD recurring at Monthly frequency", str(edited_entry))