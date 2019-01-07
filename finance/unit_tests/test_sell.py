import json
from finance.views import sell
from finance.helpers import lookup
from .base import BaseUnitTestCase
from django.urls import reverse, resolve
from finance.models import Portfolio,Transaction, Statement

class SellCase(BaseUnitTestCase):
	''' This class is responsible for testing the process of selling shares of stocks.
	This includes testing the /sell/ url, the sell view and the database operations
	involved in selling shares of stocks. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_stocks_for_first_user()

		netflix_price = lookup("NFLX")["price"]
		holding_value = 5 * netflix_price

		netflix_holding = Portfolio.objects.get(stock = "NFLX")
		netflix_holding.current_price = netflix_price
		netflix_holding.value = holding_value
		netflix_holding.save()
		
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_sell_url(self):

		self.assertEqual(resolve(reverse("sell")).func, sell)

	# test that GET requests sent to the view result in an error message
	def test_sell_get(self):

		response = self.client.get(reverse("sell"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that incomplete input leads to an error message
	def test_sell_invalid_input(self):

		response = self.client.post(reverse("sell"), {"symbol": "NFLX"})

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the user is notified if they own no shares of the selected stock
	def test_sell_no_shares_owned(self):

		response = self.client.post(reverse("sell"), {"symbol": "AAPL", "shares": "5"})

		self.assertIn(json.dumps({"error": "1"}), str(response.content))

	# test that the user is notified if they don't own enough shares for the transaction
	def test_sell_not_enough_shares(self):

		response = self.client.post(reverse("sell"), {"symbol": "NFLX", "shares": "10"})

		self.assertIn(json.dumps({"error": "2"}), str(response.content))

	# test that users can sell shares of stock if they enter valid input
	def test_sell_valid_input(self):

		# test that the user's portfolio is updated with the transaction data
		old_netflix_holding = Portfolio.objects.get(user = self.test1, stock = "NFLX")
		old_balance = super().get_balance_for_first_user()

		response = self.client.post(reverse("sell"), {"symbol": "NFLX", "shares": "5"})

		new_netflix_holding = Portfolio.objects.get(user = self.test1, stock = "NFLX")
		self.assertEqual(new_netflix_holding.shares, 0)
		self.assertEqual(float(new_netflix_holding.value), 0.00)

		# test that the transaction's value is added to the user's balance
		new_balance = super().get_balance_for_first_user()
		addition_result = old_balance + old_netflix_holding.value
		self.assertEqual(new_balance, addition_result)

		# test that the transaction is added to the transaction history
		transactions_count = super().count_transactions_for_first_user()
		self.assertEqual(transactions_count, 1)

		netflix_history = Transaction.objects.get(user = self.test1, stock = "NFLX")
		self.assertEqual(f"test1: Sell transaction of 5 shares of NFLX stock for " + 
			f"{new_netflix_holding.current_price} USD each", str(netflix_history))

		# test that the transaction is added to the financial statement
		statements_count = super().count_statements_for_first_user()
		self.assertEqual(statements_count, 2)

		netflix_statement = Statement.objects.get(user = self.test1, statement_type = "Income")
		self.assertEqual(f"test1: Income of {old_netflix_holding.value} USD", str(netflix_statement))

		# test that the user is redirected to the stocks page
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, "/stocks/")
