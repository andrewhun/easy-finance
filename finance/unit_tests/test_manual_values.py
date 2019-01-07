from .base import BaseUnitTestCase
from finance.views import manual_values
from django.urls import reverse, resolve
from finance.models import Transaction, Statement

class ManualValuesCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of adding entries
	to the financial statement table. This includes testing the /manual_values/
	url, the manual_values view and the database operations involved in adding
	entries. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_manual_values_url(self):

		self.assertEqual(resolve(reverse("manual_values")).func, manual_values)

	# test that GET requests sent to the view result in an error message
	def test_manual_values_get(self):

		response = self.client.get(reverse("manual_values"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that incomplete input sent to the view results in an error message
	def test_manual_values_invalid_input(self):

		response = self.client.post(reverse("manual_values"), {"manual_type": "Expense",
			"manual_title": "Rent"})

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view adds a new entry to the statements table if the input is valid
	def test_manual_values_valid_input(self):

		original_balance = super().get_balance_for_first_user()

		income_response = self.client.post(reverse("manual_values"), {"manual_type": "Income",
			"manual_title": "Work", "manual_amount": "300"})

		work_statement = Statement.objects.get(user = self.test1, statement_type = "Income")
		self.assertEqual(len(Statement.objects.all()), 2)
		self.assertEqual("test1: Income of 300.00 USD", str(work_statement))

		# test that the user is redirected to the history page
		self.assertEqual(income_response.status_code, 302)
		self.assertEqual(income_response.url, "/history/")

		# test that the entry's value is added to / deducted from the user's balance
		addition_result = original_balance + work_statement.amount
		new_balance = super().get_balance_for_first_user()
		self.assertEqual(addition_result, new_balance)

		expense_response = self.client.post(reverse("manual_values"), {"manual_type": "Expense",
			"manual_title": "Rent", "manual_amount": "325"})

		rent_statement = Statement.objects.get(user = self.test1, statement_type = "Expense")

		deduction_result = new_balance - rent_statement.amount
		newest_balance = super().get_balance_for_first_user()
		self.assertEqual(deduction_result, newest_balance)