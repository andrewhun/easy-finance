from finance.views import history
from .base import BaseUnitTestCase
from django.urls import reverse, resolve
from finance.models import Transaction, Statement

class HistoryCase(BaseUnitTestCase):
	''' This class is responsible for testing the history page.
	This includes testing the /history/ url, the history view,
	history.html and the Statement and Transaction models. '''

	# set up test database
	def setUp(self):

		super().setUp()
		super().add_second_user()
		super().add_statements_for_first_user()
		super().add_statements_for_second_user()
		super().add_transactions_for_first_user()
		super().add_transactions_for_second_user()
		super().login_as_first_user()

	# test that the url and the view are connected
	def test_history_url(self):

		self.assertEqual(resolve(reverse("history")).func, history)

	# test the Statement model
	def test_history_statement_model(self):

		first_user_statements_count = super().count_statements_for_first_user()
		self.assertEqual(4, first_user_statements_count)

		second_user_statements_count = super().count_statements_for_second_user()
		self.assertEqual(4, second_user_statements_count)

		first_user_expense_statement = Statement.objects.get(statement_type = "Expense", user = self.test1)
		self.assertEqual("test1: Expense of 25.00 USD", str(first_user_expense_statement))

		second_user_income_statement = Statement.objects.get(statement_type = "Income", user = self.test2)
		self.assertEqual("test2: Income of 1000.00 USD", str(second_user_income_statement))

	# test the Transaction model
	def test_history_transaction_model(self):

		first_user_transactions_count = super().count_transactions_for_first_user()
		self.assertEqual(2, first_user_transactions_count)

		second_user_transactions_count = super().count_transactions_for_second_user()
		self.assertEqual(2, second_user_transactions_count)

		first_user_sell_transaction = Transaction.objects.get(user = self.test1, stock = "AAPL")
		self.assertEqual("test1: Sell transaction of 10 shares of AAPL stock for 160.00 USD each",
		 str(first_user_sell_transaction))

		second_user_buy_transaction = Transaction.objects.get(user = self.test2, stock = "AMD")		
		self.assertEqual("test2: Buy transaction of 20 shares of AMD stock for 15.00 USD each",
		 str(second_user_buy_transaction))

	# test that POST requests sent to the view result in an error message
	def test_history_post(self):

		response = self.client.post(reverse("history"))

		self.assertEqual(response.status_code, 200)
		self.assertIn("error_message", response.context)

	# test that the view presents the history page if it receives a GET request
	def test_history_get(self):

		response = self.client.get(reverse("history"))

		# test that the edit balance form is present
		self.assertIn("<p> New starting balance", str(response.content))

		# test that the financial statement table is present and has the correct data
		self.assertIn("<td>Income</td>", str(response.content))
		self.assertIn("<td>Work</td>", str(response.content))
		self.assertIn("<td>50.00</td>", str(response.content))

		# test that the add entry form is present
		self.assertIn("Add income/expense entry</h2>", str(response.content))

		# test that the edit entry form is present
		self.assertIn("Edit income/expense entry</h2>", str(response.content))

		# test that the transaction history table is present and has the correct data
		self.assertIn("<td>Sell</td>", str(response.content))
		self.assertIn("<td>AAPL</td>", str(response.content))
		self.assertIn("<td>10</td>", str(response.content))
		self.assertIn("<td>160.00</td>", str(response.content))

	# test that users can only see their own data
	def test_history_separate_data(self):

		super().log_current_user_out()
		super().login_as_second_user()

		response = self.client.get(reverse("history"))

		self.assertNotIn("<td>50.00</td>", str(response.content))

		self.assertIn("<td>Expense</td>", str(response.content))
		self.assertIn("<td>Rent</td>", str(response.content))
		self.assertIn("<td>300.00</td>", str(response.content))

		self.assertNotIn("<td>Sell</td>", str(response.content))
		self.assertNotIn("<td>AAPL</td>", str(response.content))
		self.assertNotIn("<td>10</td>", str(response.content))
		self.assertNotIn("<td>160.00</td>", str(response.content))

		self.assertIn("<td>Buy</td>", str(response.content))
		self.assertIn("<td>AMD</td>", str(response.content))
		self.assertIn("<td>20</td>", str(response.content))
		self.assertIn("<td>15.00</td>", str(response.content))
