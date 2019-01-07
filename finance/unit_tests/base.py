from django.test import TestCase, Client
from django.contrib.auth.models import User
from finance.models import Autovalue, Transaction, Portfolio, Statement, Cash

class BaseUnitTestCase(TestCase):
	''' This class serves as the base of all other classes
	that are used for unit-testing this web application. '''

	# set up the first user the same way registering a new user would, and set up the client
	def setUp(self):

		self.test1 = User.objects.create_user(username = "test1", password = "testpass1")

		Cash.objects.create(user = self.test1, cash = 5000.00)
		Statement.objects.create(statement_type = "Balance", title = "Starting balance", 
			amount = 5000.00, user = self.test1)

		self.client = Client()

	# add a second user
	def add_second_user(self):

		self.test2 = User.objects.create_user(username = "test2", password = "testpass2")
		
		Cash.objects.create(user = self.test2, cash = 10000.00)
		Statement.objects.create(statement_type = "Balance", title = "Starting balance", 
			amount = 10000.00, user = self.test2)

	# add recurring entries to the first user's account
	def add_recurring_entries_for_first_user(self):

		Autovalue.objects.create(value_type = "Income", title = "Work", amount = 50.00, user = self.test1,
		 frequency = "Daily")
		Autovalue.objects.create(value_type = "Expense", title = "Rent", amount = 75.00, user = self.test1,
		 frequency = "Weekly")

	# check the number of recurring entries in the first user's account
	def count_recurring_entries_for_first_user(self):

		return (len(Autovalue.objects.filter(user = self.test1)))

	# add recurring entries to the second user's account
	def add_recurring_entries_for_second_user(self):

		Autovalue.objects.create(value_type = "Income", title = "Work", amount = 1000.00, user = self.test2,
		 frequency = "Monthly")
		Autovalue.objects.create(value_type = "Expense", title = "Groceries", amount = 25.00, user = self.test2,
		 frequency = "Weekly")

	# check the number of recurring entries in the second user's account
	def count_recurring_entries_for_second_user(self):

		return (len(Autovalue.objects.filter(user = self.test2)))

	# add stocks to the first user's portfolio
	def add_stocks_for_first_user(self):

		Portfolio.objects.create(user = self.test1, stock = "NFLX", shares = 5, current_price = 260.00, value = 1300.00)
		Portfolio.objects.create(user = self.test1, stock = "AAPL", shares = 0, current_price = 160.00, value = 0.00)

	# check the number of stocks in the first user's portfolio
	def count_stocks_for_first_user(self):

		return (len(Portfolio.objects.filter(user = self.test1)))

	# add stocks to the second user's portfolio
	def add_stocks_for_second_user(self):

		Portfolio.objects.create(user = self.test2, stock = "GE", shares = 100, current_price = 8, value = 800)
		Portfolio.objects.create(user = self.test2, stock = "AMD", shares = 20, current_price = 15, value = 300)

	# check the number of stocks in the second user's portfolio
	def count_stocks_for_second_user(self):

		return (len(Portfolio.objects.filter(user = self.test2)))

	# add statement entries to the first user's account
	def add_statements_for_first_user(self):

		Statement.objects.create(statement_type = "Income", title = "Work", amount = 50.00, user = self.test1)
		Statement.objects.create(statement_type = "Expense", title = "Groceries", amount = 25.00, user = self.test1)
		Statement.objects.create(statement_type = "Income", title = "Work", amount = 50.00, user = self.test1)

	# check the number of statement entries in the first user's account
	def count_statements_for_first_user(self):

		return (len(Statement.objects.filter(user = self.test1)))

	# add statement entries to the second user's account
	def add_statements_for_second_user(self):

		Statement.objects.create(statement_type = "Income", title = "Work", amount = 1000.00, user = self.test2)
		Statement.objects.create(statement_type = "Expense", title = "Groceries", amount = 25.00, user = self.test2)
		Statement.objects.create(statement_type = "Expense", title = "Rent", amount = 300.00, user = self.test2)

	# check the number of statement entries in the second user's account
	def count_statements_for_second_user(self):

		return (len(Statement.objects.filter(user = self.test2)))

	# add transaction entries to the first user's account
	def add_transactions_for_first_user(self):

		Transaction.objects.create(transaction_type = "Sell", stock = "AAPL", shares = 10, 
			price = 160.00, user = self.test1)

		Transaction.objects.create(transaction_type = "Buy", stock = "NFLX", shares = 5, 
			price = 260.00, user = self.test1)

	# check the number of transaction entries in the first user's account
	def count_transactions_for_first_user(self):

		return (len(Transaction.objects.filter(user = self.test1)))

	# add transaction entries to the second user's account
	def add_transactions_for_second_user(self):

		Transaction.objects.create(transaction_type = "Buy", stock = "GE", shares = 100, 
			price = 8.00, user = self.test2)

		Transaction.objects.create(transaction_type = "Buy", stock = "AMD", shares = 20, 
			price = 15.00, user = self.test2)

	# check the number of transaction entries in the second user's account
	def count_transactions_for_second_user(self):

		return (len(Transaction.objects.filter(user = self.test2)))

	# log in the first user
	def login_as_first_user(self):

		self.client.login(username = "test1", password = "testpass1")

	# log in the second user
	def login_as_second_user(self):

		self.client.login(username = "test2", password = "testpass2")

	# log out the current user
	def log_current_user_out(self):

		self.client.logout()

	# check the first user's current balance
	def get_balance_for_first_user(self):

		return (Cash.objects.get(user = self.test1).cash)

	# check the second user's current balance
	def get_balance_for_second_user(self):

		return (Cash.objects.get(user = self.test2).cash)

	# get the first user's starting balance statement
	def get_starting_balance_statement_for_first_user(self):

		return(Statement.objects.get(user = self.test1, title = "Starting balance"))

	# get the second user's starting balance statement
	def get_starting_balance_statement_for_second_user(self):

		return(Statement.objects.get(user = self.test2, title = "Starting balance"))