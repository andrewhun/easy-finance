from .base import BaseUnitTestCase
from finance.models import Statement
from finance.views import delete_hist
from django.urls import reverse, resolve

class DeleteHistCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of deleting
	entries from the financial statements table. This includes testing
	the /delete_hist/ url, the delete_hist view and the database operations
	involved in deleting entries. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_statements_for_first_user()
		super().login_as_first_user()

	# test that the view and the url are connected
	def test_delete_hist_url(self):

		self.assertEqual(resolve(reverse("delete_hist")).func, delete_hist)

	# test that sending a GET request to the view results in an error message
	def test_delete_hist_get(self):

		response = self.client.get(reverse("delete_hist"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that sending invalid input to the view results in an error message
	def test_delete_hist_invalid_input(self):

		response = self.client.post(reverse("delete_hist"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the selected entry is deleted if the view receives valid input
	def test_delete_hist_valid_input(self):

		old_balance = super().get_balance_for_first_user()
		expense_statement = Statement.objects.get(user = self.test1, statement_type = "Expense")

		expense_response = self.client.post(reverse("delete_hist"), {"delete_hist_id": 3})

		statements_count = super().count_statements_for_first_user()
		self.assertEqual(statements_count, 3)

		number_of_expense_statements = len(Statement.objects.filter(statement_type = "Expense"))
		self.assertEqual(number_of_expense_statements, 0)

		# test that the user is redirected to the history page
		self.assertEqual(expense_response.status_code, 302)
		self.assertEqual(expense_response.url, "/history/")

		# test that the entry's value is added to / deducted from the user's cash
		first_adjustment = old_balance + expense_statement.amount
		new_balance =super().get_balance_for_first_user()
		self.assertEqual(new_balance, first_adjustment)

		income_statement = Statement.objects.get(user = self.test1, id = 4)

		income_response = self.client.post(reverse("delete_hist"), {"delete_hist_id": 4})

		second_adjustment = new_balance - income_statement.amount
		newest_balance = super().get_balance_for_first_user()
		self.assertEqual(newest_balance, second_adjustment)