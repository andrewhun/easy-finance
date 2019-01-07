import time
import requests
import urllib.parse
from django.shortcuts import render
from background_task import background
from .models import Autovalue, Statement, Cash
from selenium.common.exceptions import WebDriverException

def calculate_sum_of_list(value_list):
	""" Calculate the sum of list elements. """

	# initialize the sum at 0
	value_sum = 0

	# if the list is not empty
	if len(value_list) != 0:

		# iterate through the elements of the list
		for value_tupple in value_list:

			# add each value to the sum
			value_sum += value_tupple[0]

	# return the sum
	return value_sum

def show_error_message(request, error_message):
	''' Show an error message to the user. '''

	# place the message in a dictionary
	context = {"error_message": error_message}

	# place error.html's path into a variable
	html = "finance/error.html"

	# show the message to the user
	return render(request, html, context = context)

def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        response = requests.get("https://api.iextrading.com/1.0/stock/{0}/quote".format(urllib.parse.quote_plus(symbol)))
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def update_stock_prices(portfolio_set):
	''' Update stock prices and value based on data from the Yahoo Finance API. '''

	for portfolio in portfolio_set:

		price_quote = lookup(portfolio.stock)

		portfolio.current_price = round(price_quote["price"], 2)

		# recalculate the value of the user's stake
		portfolio.value = round(portfolio.shares * portfolio.current_price, 2)

		portfolio.save()

	return portfolio_set

def wait_for(assertion_function):
	''' Minimize time spent waiting during functional tests '''

	start_time = time.time()
	MAX_WAIT = 30

	while True:
		try:

			# try to execute the test that is passed in
			return assertion_function()  

		except (AssertionError, WebDriverException) as e:

			# keep trying until the set time limit is reached, then throw an exception
			if time.time() - start_time > MAX_WAIT:
				raise e
			time.sleep(0.5)

def log_test_user_in(driver):
	''' Logs test users in as part of the setup for functional tests that need to access
	login-only pages. '''
	
	username_input = driver.find_element_by_id("login_user")
	username_input.send_keys("test1")

	password_input = driver.find_element_by_id("login_pw")
	password_input.send_keys("testpass1")

	driver.find_element_by_id("login").submit()

def allow_time_to_load():
	''' Wait for a set amount of time to let the webdriver load the page fully '''

	time.sleep(2)

@background
def add_daily_entries_to_statements():
	''' Add daily recurring entries to the financial statements table. '''

	# find all daily recurring entries
	list_of_daily_entries = Autovalue.objects.filter(frequency = "Daily")

	# iterate through the list of entries
	for entry in list_of_daily_entries:

		# add entries to the financial statements table
		Statement.objects.create(statement_type = entry.value_type, title = entry.title,
			amount = entry.amount, user = entry.user)

		# adjust the user's balance with the entry's amount
		adjust_user_balance(entry.user, entry.value_type, float(entry.amount))

@background
def add_weekly_entries_to_statements():
	''' Add weekly recurring entries to the financial statements table. '''

	# find all weekly recurring entries
	list_of_weekly_entries = Autovalue.objects.filter(frequency = "Weekly")

	# iterate though the list of entries
	for entry in list_of_weekly_entries:

		# add entries to the financial statements table
		Statement.objects.create(statement_type = entry.value_type, title = entry.title,
			amount = entry.amount, user = entry.user)

		# adjust the user's balance with the entry's amount
		adjust_user_balance(entry.user, entry.value_type, float(entry.amount))

@background
def add_monthly_entries_to_statements():
	''' Add monthly recurring entries to the financial statements table. '''

	# find all monthly recurring entries
	list_of_monthly_entries = Autovalue.objects.filter(frequency = "Monthly")

	# iterate through the list of entries
	for entry in list_of_monthly_entries:

		# add entries to the financial statements table
		Statement.objects.create(statement_type = entry.value_type, title = entry.title,
			amount = entry.amount, user = entry.user)

		# adjust the user's balance with the entry's amount
		adjust_user_balance(entry.user, entry.value_type, float(entry.amount))

def adjust_user_balance(user, entry_type, entry_amount):
	''' Adds/deducts the specified amount to/from the user's balance, depending on the
	related financial statement entry's type '''

	# get the current user's balance
	user_balance = Cash.objects.get(user = user)
	income_type = "Income"

	# add the amount if the entry is an income
	if entry_type == income_type:

		new_balance = float(user_balance.cash) + entry_amount
	# deduct the amount if the entry is an expense
	else:

		new_balance = float(user_balance.cash) - entry_amount
	# save the change to the database
	user_balance.cash = new_balance
	user_balance.save()