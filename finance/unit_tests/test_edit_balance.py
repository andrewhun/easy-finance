from .base import BaseUnitTestCase
from finance.models import Statement
from finance.views import edit_balance
from django.urls import reverse, resolve

class EditBalanceCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of changing
	the starting balance of users. This includes testing the /edit_balance/
	url, the edit_balance view and the database operations involved. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_edit_balance_url(self):

		self.assertEqual(resolve(reverse("edit_balance")).func, edit_balance)

	# test that GET requests sent to the view result in an error message
	def test_edit_balance_get(self):

		response = self.client.get(reverse("edit_balance"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that invalid input sent to the view results in an error message
	def test_edit_balance_invalid_input(self):

		response = self.client.post(reverse("edit_balance"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view changes the starting balance if it receives valid input
	def test_edit_balance_valid_input(self):

		old_balance = super().get_balance_for_first_user()
		old_statement = Statement.objects.get(user = self.test1, statement_type = "Balance")

		response = self.client.post(reverse("edit_balance"), {"edit_balance_amount": "2000"})

		# test that the user is redirected to the history page
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, "/history/")

		# test that the starting balance is changed
		new_statement = Statement.objects.get(user = self.test1, statement_type = "Balance")
		self.assertEqual(new_statement.amount, 2000.00)

		# test that the user's balance is adjusted
		adjustment_result = old_balance - old_statement.amount + new_statement.amount
		new_balance = super().get_balance_for_first_user()
		self.assertEqual(adjustment_result, new_balance)