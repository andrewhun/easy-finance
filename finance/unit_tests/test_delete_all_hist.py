from .base import BaseUnitTestCase
from finance.models import Statement
from django.urls import reverse, resolve
from finance.views import delete_all_hist

class DeleteAllHistCase(BaseUnitTestCase):
	''' This class is responsible for testing the processes of emptying
	the financial statement, transaction history and portfolio tables and
	reseting the starting balance to 10,000.00 USD. This includes testing
	the /delete_all_hist/ url, the delete_all_hist view and the database
	operations involved. '''

	# set up test database
	def setUp(self):

		self.default_balance = 10000.00

		super().setUp()
		super().add_second_user()
		super().add_statements_for_first_user()
		super().add_statements_for_second_user()
		super().add_transactions_for_first_user()
		super().add_transactions_for_second_user()
		super().add_stocks_for_first_user()
		super().add_stocks_for_second_user()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_delete_all_hist_url(self):

		self.assertEqual(resolve(reverse("delete_all_hist")).func, delete_all_hist)

	# test that GET requests sent to the view result in an error message
	def test_delete_all_hist_get(self):

		response = self.client.get(reverse("delete_all_hist"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that invalid input sent to the view results in an error message
	def test_delete_all_hist_invalid_input(self):

		response = self.client.post(reverse("delete_all_hist"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view resets the user's account if it receives valid input
	def test_delete_all_hist_valid_input(self):

		response = self.client.post(reverse("delete_all_hist"), {"delete_all_check2": "check"})

		# test that the user is redirected to the history page
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, "/history/")

		# test that the financial statement table is emptied and a new entry for starting balance is added
		first_user_statements_count = super().count_statements_for_first_user()
		self.assertEqual(first_user_statements_count, 1)

		# test that the transaction history table is emptied
		first_user_transactions_count = super().count_transactions_for_first_user()
		self.assertEqual(first_user_transactions_count, 0)

		# test that the portfolio table is emptied
		first_user_stocks_count = super().count_stocks_for_first_user()
		self.assertEqual(first_user_stocks_count, 0)

		# test that the user's starting balance is reset
		first_user_balance = super().get_balance_for_first_user()
		self.assertEqual(first_user_balance, self.default_balance)

		# test that other users' data is left untouched
		second_user_statements_count = super().count_statements_for_second_user()
		self.assertEqual(second_user_statements_count, 4)

		second_user_transactions_count = super().count_transactions_for_second_user()
		self.assertEqual(second_user_transactions_count, 2)

		second_user_stocks_count = super().count_stocks_for_second_user()
		self.assertEqual(second_user_stocks_count, 2)