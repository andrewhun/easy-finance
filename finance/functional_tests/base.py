import os
from selenium import webdriver
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from selenium.webdriver.support.ui import Select
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from finance.models import Autovalue, Transaction, Portfolio, Statement, Cash
from finance.helpers import wait_for, log_test_user_in, allow_time_to_load


class BaseFunctionalTestCase(StaticLiveServerTestCase):
	''' This class serves as the base of all other classes that are 
	used for testing the functionality of this web application. '''

	# set up a test user the same way registering a new user would, and set up the webdriver
	def setUp(self):

		chrome_options = webdriver.ChromeOptions()
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--headless')
		self.driver = webdriver.Chrome(chrome_options = chrome_options)
		self.driver.implicitly_wait(30)

		self.test1 = User.objects.create_user(username = "test1", password = "testpass1")
		
		Cash.objects.create(user = self.test1, cash = 5000.00)
		Statement.objects.create(statement_type = "Balance", title = "Starting balance", 
			amount = 5000.00, user = self.test1)

		self.driver.get('%s%s' % (self.live_server_url, '/login/'))

	# close the browser after running each test
	def tearDown(self):

		self.driver.close()

	# add recurring entries to the database
	def add_recurring_entries(self):

		Autovalue.objects.create(value_type = "Income", title = "Work", amount = 50.00, 
			user = self.test1, frequency = "Daily")
		Autovalue.objects.create(value_type = "Expense", title = "Groceries", amount = 25.00, 
			user = self.test1, frequency = "Weekly")
		Autovalue.objects.create(value_type = "Expense", title = "Rent", amount = 300.00, 
			user = self.test1, frequency = "Monthly")

	# adds an entry to the financial statement table
	def add_statement_entry(self):

		Statement.objects.create(statement_type = "Income", title = "Work", 
			amount = 1000.00, user = self.test1)

	# add stocks to the user's portfolio
	def add_stocks_to_portfolio(self):

		Portfolio.objects.create(user = self.test1, stock = "AAPL", shares = 10, current_price = 160.00, value = 1600.00)
		Portfolio.objects.create(user = self.test1, stock = "GE", shares = 0, current_price = 10.00, value = 0)

	# add entries to the transaction history table
	def add_transactions_to_history(self):

		Transaction.objects.create(transaction_type = "Buy", stock = "AAPL", shares = 10, 
			price = 160.00, user = self.test1)
		Transaction.objects.create(transaction_type = "Sell", stock = "GE", shares = 5, 
			price = 10.00, user = self.test1)

	# log the user in
	def log_test_user_in(self):

		username_input = self.driver.find_element_by_id("login_user")
		username_input.send_keys("test1")

		password_input = self.driver.find_element_by_id("login_pw")
		password_input.send_keys("testpass1")

		self.driver.find_element_by_id("login").submit()

	# navigate to the stocks page
	def navigate_to_stocks(self):

		stocks_link = self.driver.find_element_by_link_text("Stocks")
		stocks_link.click()

	# navigate to the history page
	def navigate_to_history(self):

		history_link = self.driver.find_element_by_link_text("History")
		history_link.click()

	# navigate to the register page
	def navigate_to_register(self):

		register_link = self.driver.find_element_by_link_text("Register")
		register_link.click()

	# navigate to the login page
	def navigate_to_login(self):

		login_link = self.driver.find_element_by_link_text("Log In")
		login_link.click()

	# click on the website's logo
	def click_on_logo(self):

		logo = self.driver.find_element_by_link_text("Ea$y Finance")
		logo.click()

	# navigate to the change password page
	def navigate_to_change_pw(self):

		change_pw_link = self.driver.find_element_by_link_text("Change Password")
		change_pw_link.click()

	# get the number of recurring entries
	def count_recurring_entries(self):

		return (len(Autovalue.objects.all()))

	# get the number of entries in the financial statement table
	def count_statement_entries(self):

		return (len(Statement.objects.all()))

	# get the number of entries in the transaction history table
	def count_transaction_entries(self):

		return (len(Transaction.objects.all()))

	def count_stocks_in_portfolio(self):

		return (len(Portfolio.objects.all()))

	# get the user's current balance
	def get_current_user_balance(self):

		return (Cash.objects.get(user = self.test1).cash)

	# get the starting balance statement entry
	def get_starting_balance_statement(self):

		return(Statement.objects.get(title = "Starting balance"))
