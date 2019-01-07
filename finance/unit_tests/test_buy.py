import json
from finance.views import buy
from finance.helpers import lookup
from .base import BaseUnitTestCase
from django.urls import reverse, resolve
from finance.models import Portfolio,Transaction, Statement

class BuyCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of buying shares of stocks.
	This includes testing the /buy/ url, the buy view and the database
	operations involved in buying shares of stocks '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_stocks_for_first_user()
		super().login_as_first_user()

	# test that the url is connected to the view
	def test_buy_url(self):

		self.assertEqual(resolve(reverse("buy")).func, buy)

	# test that GET requests sent to the view result in an error message
	def test_buy_get(self):

		response = self.client.get(reverse("buy"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that entering invalid stock symbols results in an error message
	def test_buy_invalid_stock_symbol(self):

		response = self.client.post(reverse("buy"), {"symbol": "asddfds", "shares": "10"})

		self.assertIn(json.dumps({"error": "1"}), str(response.content))

	# test that the user is notified if they have insufficient funds for the transaction
	def test_buy_insufficient_funds(self):

		response = self.client.post(reverse("buy"), {"symbol": "AAPL", "shares": "10000000"})

		self.assertIn(json.dumps({"error": "2"}), str(response.content))

	# test that incomplete input results in an error message
	def test_buy_incomplete_input(self):

		response = self.client.post(reverse("buy"), {"symbol": "AAPL"})

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that users can buy shares of stock if they enter valid input
	def test_buy_valid_input(self):

		original_balance = super().get_balance_for_first_user()
		new_stock_response = self.client.post(reverse("buy"), {"symbol": "AMD", "shares": "10"})

		# test that a new portfolio entry is created when the user 
		# buys shares of a stock they did not own before
		stocks_count = super().count_stocks_for_first_user()
		self.assertEqual(stocks_count, 3)

		amd_stock = Portfolio.objects.get(user = self.test1, stock = "AMD")
		self.assertEqual(amd_stock.shares, 10)

		# test that the transaction is added to the transaction history
		transactions_count = super().count_transactions_for_first_user()
		self.assertEqual(transactions_count, 1)

		amd_history = Transaction.objects.get(user = self.test1, stock = "AMD")
		self.assertEqual(f"test1: Buy transaction of 10 shares of AMD stock for {amd_stock.current_price} USD each",
			str(amd_history))

		# test that the transaction is added to the financial statement
		statements_count = super().count_statements_for_first_user()
		self.assertEqual(statements_count, 2)

		amd_statement = Statement.objects.get(user = self.test1, statement_type = "Expense")
		self.assertEqual(f"test1: Expense of {amd_stock.value} USD", str(amd_statement))

		# test that the value of the transaction is deducted from the user's balance
		new_balance = super().get_balance_for_first_user()
		deduction_result = original_balance - amd_stock.value
		self.assertEqual(new_balance, deduction_result)

		# test that users are redirected to the stocks page after a successful transaction
		self.assertEqual(new_stock_response.status_code, 302)
		self.assertEqual(new_stock_response.url, "/stocks/")

		# test that an existing portfolio entry is updated when the user
		# buys shares of a stock they already owned
		old_netflix_holding = Portfolio.objects.get(user = self.test1, stock = "NFLX")

		existing_stock_response = self.client.post(reverse("buy"), {"symbol": "NFLX", "shares": "5"})

		new_netflix_holding = Portfolio.objects.get(user = self.test1, stock = "NFLX")
		transaction_value = new_netflix_holding.current_price * 5
		addition_result = old_netflix_holding.value + transaction_value

		self.assertEqual(new_netflix_holding.shares, int(old_netflix_holding.shares) + 5)
		self.assertTrue(self.values_are_relatively_close(new_netflix_holding.value, addition_result))

	def values_are_relatively_close(self, value1, value2):
		''' Decide whether or not the two passed in float values are close to
		each other. '''

		difference = abs(value1 - value2)

		if difference <= 0.1:

			return True

		else:

			return False