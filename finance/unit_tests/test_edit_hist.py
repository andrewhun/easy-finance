from .base import BaseUnitTestCase
from finance.views import edit_hist
from finance.models import Statement
from django.urls import reverse, resolve

class EditHistCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of editing
	entries in the financial statement table. This includes testing
	the /edit_hist/ url, the edit_hist view and the database operations
	involved in editing entries. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_statements_for_first_user()
		super().login_as_first_user()

	# test that the url and the views are connected
	def test_edit_hist_url(self):

		self.assertEqual(resolve(reverse("edit_hist")).func, edit_hist)

	# test that a GET request sent to the view results in an error message
	def test_edit_hist_get(self):

		response = self.client.get(reverse("edit_hist"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that invalid input sent to the view results in an error message
	def test_edit_hist_invalid_input(self):

		response = self.client.post(reverse("edit_hist"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view edits the selected entries if the input is valid
	def test_edit_hist_valid_input(self):

		original_balance = super().get_balance_for_first_user()
		original_statement = Statement.objects.get(user = self.test1, statement_type = "Expense")

		expense_to_expense_response = self.client.post(reverse("edit_hist"),
			{"edit_hist_id": 3, "edit_hist_type": "", "edit_hist_title": "", "edit_hist_amount": "30"})

		# test that the user is redirected to the history page
		self.assertEqual(expense_to_expense_response.status_code, 302)
		self.assertEqual(expense_to_expense_response.url, "/history/")

		statements_count = super().count_statements_for_first_user()
		self.assertEqual(statements_count, 4)

		grocery_statement = Statement.objects.get(user = self.test1, statement_type = "Expense")
		self.assertEqual("test1: Expense of 30.00 USD", str(grocery_statement))

		# test that the user's balance is adjusted according to the change
		first_adjustment = original_balance + original_statement.amount - grocery_statement.amount
		expense_to_expense_balance = super().get_balance_for_first_user()
		self.assertEqual(first_adjustment, expense_to_expense_balance)

		expense_to_income_response = self.client.post(reverse("edit_hist"),
			{"edit_hist_id": 3, "edit_hist_type": "Income", "edit_hist_title": "Lottery", "edit_hist_amount": "1000"})

		lottery_statement = Statement.objects.get(user = self.test1, title = "Lottery")
		self.assertEqual("test1: Income of 1000.00 USD", str(lottery_statement))

		second_adjustment = expense_to_expense_balance + grocery_statement.amount + lottery_statement.amount
		expense_to_income_balance = super().get_balance_for_first_user()
		self.assertEqual(expense_to_income_balance, second_adjustment)

		income_to_income_response = self.client.post(reverse("edit_hist"),
			{"edit_hist_id": 3, "edit_hist_type": "", "edit_hist_title": "Presents", "edit_hist_amount": "25"})

		present_statement = Statement.objects.get(user = self.test1, title = "Presents")
		self.assertEqual("test1: Income of 25.00 USD", str(present_statement))

		third_adjustment = expense_to_income_balance - lottery_statement.amount + present_statement.amount
		income_to_income_balance = super().get_balance_for_first_user()
		self.assertEqual(income_to_income_balance, third_adjustment)

		income_to_expense_response = self.client.post(reverse("edit_hist"),
			{"edit_hist_id": 3, "edit_hist_type": "Expense", "edit_hist_title": "Loan", "edit_hist_amount": "45"})

		loan_statement = Statement.objects.get(user = self.test1, title = "Loan")
		self.assertEqual("test1: Expense of 45.00 USD", str(loan_statement))

		fourth_adjustment = income_to_income_balance - present_statement.amount - loan_statement.amount
		income_to_expense_balance = super().get_balance_for_first_user()
		self.assertEqual(income_to_expense_balance, fourth_adjustment)