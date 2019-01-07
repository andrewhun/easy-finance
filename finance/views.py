import json
from django.urls import reverse
from django.db.models import Sum
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .models import Autovalue, Transaction, Portfolio, Statement, Cash
from .helpers import calculate_sum_of_list, show_error_message, update_stock_prices, lookup, adjust_user_balance

g_invalid_request = "Invalid request method."
g_error_occured = "Something has gone wrong with your request. Please try again."
g_get_method = "GET"

# Create your views here.

def index(request):
	''' This view is responsible for presenting the main page to users.
	In order to do so, it needs to organize data (by using a specific helper routine) into
	two separate tables: the financial summary table and the recurring entries table.
	POST requests sent to this view produce an error.'''

	# if the client sent a GET request
	if request.method == g_get_method:
	
		# if the user is not logged in, redirect them to the login page
		if not request.user.is_authenticated:
			return HttpResponseRedirect(reverse("login"))

		# organize data for the financial summary table
		amount_constant = "amount"

		# get the sum of expenses
		expense_constant = "Expense"

		expense_list = Statement.objects.values_list(amount_constant).filter(user = request.user, 
			statement_type = expense_constant)
		expense_sum = calculate_sum_of_list(expense_list)

		# get the sum of income
		income_constant = "Income"

		income_list = Statement.objects.values_list(amount_constant).filter(user = request.user, 
			statement_type = income_constant)
		income_sum = calculate_sum_of_list(income_list)

		# calculate the cash flow
		cash_flow = income_sum - expense_sum

		# get the user's current balance
		user_cash = Cash.objects.get(user = request.user).cash

		# organize data for the recurring entries table
		# find all of the recurring entries that belong to the current user
		recurring_entries = Autovalue.objects.filter(user = request.user)

		# add the now organized data to a dictionary
		context = {"income_sum": income_sum, "expense_sum": expense_sum, "cash_flow": cash_flow,
		"recurring_entries": recurring_entries, "user_cash": user_cash}
		# present the main page to the user, using the dictionary as the template context
		html = "finance/index.html"

		return render(request, html, context = context)
	# if the client sent a POST request
	else:
		# show an error message to the user
		error_message = "Invalid request method."
		return show_error_message(request, error_message)

def auto_values(request):
	''' This view is responsible for adding recurring entries to
	the current user's account. This includes processing POST requests from
	the client. GET requests sent to this view produce an error. '''

	# if the client sent a GET request
	if request.method == g_get_method: 

		# show an error message to the user
		return show_error_message(request, g_invalid_request)
	
	# if the client sent a POST request
	else:
		
		# input received as expected
		try:
			# place the user's input into variables
			value_type = request.POST["auto_type"]
			title = request.POST["auto_title"]
			amount = request.POST["auto_amount"]
			current_user = request.user
			frequency = request.POST["frequency"]

			# create a new recurring entry based on the user's input
			recurring_entry = Autovalue(value_type = value_type, title = title, amount = amount,
				user = current_user, frequency = frequency)
			recurring_entry.save()
			
			# redirect the user to the main page to showcase changes
			return HttpResponseRedirect(reverse("index"))
		
		# the view has received incomplete input
		except:

			return show_error_message(request, g_error_occured)
		
def manual_values(request):
	''' This view is responsible for adding entries to the financial statement.
	This includes creating entries based on the user's input and the database
	operations that are involved in creating entries. GET requests sent to
	this view result in an error message. '''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valied
		try:

			# place the user's input into variables
			manual_type = request.POST["manual_type"]
			manual_title = request.POST["manual_title"]
			manual_amount = float(request.POST["manual_amount"])

			# create a new entry
			new_entry = Statement(statement_type = manual_type, title = manual_title, 
				amount = manual_amount, user = request.user)

			# add/deduct the value of the entry from the user's balance
			# depending on its type
			adjust_user_balance(request.user, manual_type, manual_amount)

			# save the changes in the database
			new_entry.save()


			# redirect the user to the history page to showcase the changes
			return HttpResponseRedirect(reverse("history"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def edit_auto(request):
	''' This view is responsible for modifying existing recurring entries.
	This includes changing attributes of existing recurring entries according to
	the user's input. GET requests sent to this view result in an error message.'''

	# if the client sent a GET request
	if request.method == g_get_method:

		# show an error message
		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:
		# input received as expected
		try:

			# find the selected entry in the database
			edit_id = request.POST["edit_id"]
			selected_entry = Autovalue.objects.get(user = request.user, id = int(edit_id))
			
			# if the user specified a new value type, replace the old one with it
			edit_type = request.POST["edit_type"]
			if edit_type:

				selected_entry.value_type = edit_type

			# if the user specified a new title, replace the old one with it
			edit_title = request.POST["edit_title"]
			if edit_title:

				selected_entry.title = edit_title

			# if the user specified a new amount, replace the old one with it
			edit_amount = request.POST["edit_amount"]
			if edit_amount:

				selected_entry.amount = edit_amount

			# if the user specified a new frequency, replace the old one with it
			edit_frequency = request.POST["edit_frequency"]
			if edit_frequency:

				selected_entry.frequency = edit_frequency

			# save the changes that were made
			selected_entry.save()
			# redirect the user to the main page to showcase changes
			return HttpResponseRedirect(reverse("index"))
		
		# the view has received incomplete input
		except:
			
			return show_error_message(request, g_error_occured)

def edit_hist(request):
	''' This view is responsible for editing entries in the financial statement table.
	This includes processing the user's request and the database operations involved
	in changing entries. GET requests sent to this view result in an error message. '''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:

			# find the selected entry
			selected_entry = Statement.objects.get(user = request.user, id = request.POST["edit_hist_id"])
			old_type = selected_entry.statement_type
			old_title = selected_entry.title
			old_amount = float(selected_entry.amount)

			# place the user's input into variables if present
			new_type = old_type
			if request.POST["edit_hist_type"]:
				new_type = request.POST["edit_hist_type"]

			new_title = old_title
			if request.POST["edit_hist_title"]:
				new_title = request.POST["edit_hist_title"]

			new_amount = old_amount
			if request.POST["edit_hist_amount"]:
				new_amount = float(request.POST["edit_hist_amount"])

			# change the selected entry 
			selected_entry.statement_type = new_type
			selected_entry.title = new_title
			selected_entry.amount = new_amount

			# adjust the user's balance according to the changes
			user_cash = Cash.objects.get(user = request.user)
			user_balance = float(user_cash.cash)

			from_income_entry = bool(old_type == "Income")
			to_income_entry = bool(new_type == "Income")

			# if the old entry was income deduct its value from the user's cash
			if from_income_entry:

				user_balance -= old_amount

			# if the old entry was expense add its value to the user's cash
			else:

				user_balance += old_amount

			# if the new entry is income add its value to the user's cash
			if to_income_entry:

				user_balance += new_amount

			# if the new entry is expense deduct its value from the user's cash
			else:

				user_balance -= new_amount

			user_cash.cash = user_balance

			# save the changes in the database
			selected_entry.save()
			user_cash.save()

			# redirect user to the history page to showcase the changes
			return HttpResponseRedirect(reverse("history"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def delete_auto(request):
	''' This view is responsible for deleting recurring entries.
	This includes finding the selected entry in the database and removing it.
	GET requests sent to this view result in an error message.'''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:

			# place the user's input into a variable
			delete_id = request.POST["delete_id"]

			# find the selected entry
			selected_entry = Autovalue.objects.get(id = delete_id, user = request.user)

			# delete the selected entry
			selected_entry.delete()

			# redirect the user to the main page to showcase changes
			return HttpResponseRedirect(reverse("index"))

		# if the input is incomplete or some other error occured
		except:

			# show an error message
			return show_error_message(request, g_error_occured)

def delete_all_auto(request):
	''' This view is responsible for removing all recurring entries from the user's account.
	GET requests sent to this view result in an error message'''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:
		
		# if the input is valid
		try:

			# confirm the user's intentions 
			if request.POST["delete_all_check"]:

				# find all recurring entries that belong to the current user
				recurring_entries = Autovalue.objects.filter(user = request.user)

				# delete the entries
				recurring_entries.delete()

			# redirect the user to the main page to showcase changes
			return HttpResponseRedirect(reverse("index"))

		# if the input is incomplete or some other error occured
		except:

			# show an error message
			return show_error_message(request, g_error_occured)

def delete_hist(request):
	''' This view is responsible for deleting entries
	from the financial statement table. This includes
	finding the selected entry and executing the database
	operations involved in deleting entries. GET requests
	sent to this view result in an error message. '''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:

			# find the selected entry
			selected_entry = Statement.objects.get(user = request.user, id = request.POST["delete_hist_id"])

			# add/deduct the entry's value to/from the user's cash
			user_cash = Cash.objects.get(user = request.user)
			balance = float(user_cash.cash)

			is_income_entry = bool(selected_entry.statement_type == "Income")
			if is_income_entry:

				balance -= float(selected_entry.amount)

			else:

				balance += float(selected_entry.amount)

			user_cash.cash = balance
			user_cash.save()

			# delete the selected entry
			selected_entry.delete()

			# redirect the user to the history page to showcase the changes
			return HttpResponseRedirect(reverse("history"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def delete_all_hist(request):
	''' This view is responsible for emptying the financial statement table.
	This includes deleting all statement entries, all transaction entries,
	all portfolio entries and reseting the starting balance of the account to 10,000.00 USD. 
	GET requests sent to the view result in an error message. '''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:

			# place the input into a variable
			user_confirmed_reset = bool(request.POST["delete_all_check2"] == "check")

			if user_confirmed_reset:

				# delete all statement, transaction and portfolio entries
				user_statements = Statement.objects.filter(user = request.user)
				user_portfolio = Portfolio.objects.filter(user = request.user)
				user_transactions = Transaction.objects.filter(user = request.user)

				user_statements.delete()
				user_portfolio.delete()
				user_transactions.delete()

				# reset the user's starting balance to 10000 USD
				user_cash = Cash.objects.get(user = request.user)
				default_balance = 10000.00

				user_cash.cash = default_balance
				user_cash.save()

				# create a statement entry for the starting balance
				starting_balance_statement = Statement(statement_type = "Balance", title = "Starting balance",
					amount = default_balance, user = request.user)
				starting_balance_statement.save()

				# redirect user to the history page to showcase changes
				return HttpResponseRedirect(reverse("history"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def edit_balance(request):
	''' This view is responsible for changing the starting balance
	according to the user's instructions. GET requests sent to this
	view result in an error message. '''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:

			# place the input into a variable
			new_amount = float(request.POST["edit_balance_amount"])

			# update the starting balance entry in the financial statements table
			starting_balance_statement = Statement.objects.get(user = request.user, title = "Starting balance")

			old_amount = float(starting_balance_statement.amount)

			starting_balance_statement.amount = new_amount
			# readjust the user's current balance
			user_cash = Cash.objects.get(user = request.user)

			adjusted_current_balance = float(user_cash.cash) - old_amount + new_amount
			user_cash.cash = adjusted_current_balance
			# save changes
			starting_balance_statement.save()
			user_cash.save()

			# redirect user to the history page to showcase changes
			return HttpResponseRedirect(reverse("history"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def stocks(request):
	''' This view is responsible for presenting the user's portfolio,
	the quote, buy and sell forms to the user. This includes processing 
	data and organizing it into a presentable format.
	POST requests sent to this view result in an error message. '''
	
	# if the client sent a GET request
	if request.method == g_get_method:

		# find the user's portfolio in the database and place it in a variable
		portfolio_set = Portfolio.objects.filter(user = request.user)

		# update the current price and value for each stock using data from the Yahoo Finance API
		updated_portfolio = update_stock_prices(portfolio_set)
		
		# find the user's current balance
		user_cash = Cash.objects.get(user = request.user).cash

		# calculate the grand total

		# set the grand total to equal the user's balance by default
		grand_total = user_cash
		
		# if the user owns stocks add the sum of their value to the grand total
		portfolio_value_sum = updated_portfolio.aggregate(Sum("value"))["value__sum"]
		if portfolio_value_sum != None:
			grand_total +=portfolio_value_sum

		# collect all the data in a dictionary
		context = {"portfolio": updated_portfolio, "user_cash": user_cash, "grand_total": grand_total}
		# present the stocks page to the user
		html = "finance/stocks.html"
		return render(request, html, context = context)

	# if the client sent a POST request show an error
	else:

		return show_error_message(request, g_invalid_request)

def buy(request):
	''' This view is responsible for buying shares of stocks,
	based on the user's instructions. This includes finding the selected stock
	and its current price, deciding whether or not the user can afford the transaction
	and carrying out the database operations necessary to complete the transaction.
	GET requests sent to this view result in an error message'''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:

			# place the user's input into variables
			stock_symbol = request.POST["symbol"]
			stock_shares = int(request.POST["shares"])

			# search for the selected stock's information on Yahoo Finance
			stock_data = lookup(stock_symbol)
			# if the search comes up empty show an error message
			if stock_data == None:

				return HttpResponse(json.dumps({"error": "1"}))
			
			# if the user can't afford the transaction show an error message
			transaction_value = stock_shares * stock_data["price"]
			user_cash = Cash.objects.get(user = request.user)
			if user_cash.cash < transaction_value:

				return HttpResponse(json.dumps({"error": "2"}))

			# if the user can afford the transaction
			else:

				# if the selected stock is in the user's portfolio
				stock_in_portfolio = Portfolio.objects.filter(user = request.user, stock = stock_data["symbol"])
				
				if len(stock_in_portfolio) != 0:
					# update the information regarding the stock with the transaction's data
					stock = Portfolio.objects.get(user = request.user, stock = stock_data["symbol"])

					stock.current_price = float(stock_data["price"])
					new_share_count = int(stock.shares) + stock_shares
					stock.shares = new_share_count
					new_stake_value = float(stock.value) + transaction_value
					stock.value = new_stake_value
				
				# if the stock is not in the user's portfolio yet
				else:
					# add the selected stock to the user's portfolio
					stock = Portfolio(user = request.user, stock = stock_data["symbol"], 
						current_price = stock_data["price"], shares = stock_shares, value = transaction_value)

				# add the transaction to the financial history of the user
				history = Transaction(user = request.user, transaction_type = "Buy", stock = stock_data["symbol"],
					price = stock_data["price"], shares = stock_shares)

				# add the transaction to the financial statement of the user
				statement = Statement(statement_type = "Expense", title = "Buying shares", amount = transaction_value,
					user = request.user)

				# subtract the value of the transaction from the user's balance
				new_balance = float(user_cash.cash) - transaction_value
				user_cash.cash = new_balance

				# save all changes
				stock.save()
				user_cash.save()
				history.save()
				statement.save()

				# redirect the user to the stocks page to showcase the changes
				return HttpResponseRedirect(reverse("stocks"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def login_view(request):
	'''This view is responsible for logging in users.
	This includes presenting the login form to users, responding to invalid input
	and redirecting the user to the main page upon successful login.'''
	
	# if the user is logged in, log them out
	if request.user.is_authenticated:
		logout(request)

	# if the client sent a GET request, present the login form
	if request.method == g_get_method:
		
		html = "finance/login.html"
		return render(request, html)
	
	# if the client sent a POST request
	else:
		
		# if the input is valid
		try:

			# place the user's input into variables
			username = request.POST["username"]
			password = request.POST["password"]

			# authenticate the user
			user = authenticate(request, username=username, password=password)

			# if the user passed in invalid credentials
			if user == None:

				# show an appropriate error message
				error = {"error": "1"}
				return HttpResponse(json.dumps(error))

			# if the user entered correct credentials
			else:

				# log them in and redirect them to the main page
				login(request, user)
				return HttpResponseRedirect(reverse("index"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def logout_view(request):
	'''This view is responsible for logging users out'''
	
	# log out the current user
	logout(request)
	
	# redirect the user to the login page
	return HttpResponseRedirect(reverse("login"))

def quote(request):
	''' This view is responsible for showing the current price of
	the selected stock to the user. This includes finding the selected
	stock and its current price. GET requests sent to this view result in
	an error message. '''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:
		# if the input is valid
		try:

			# place the user's input into a variable
			stock_symbol = request.POST["symbol"]

			# find the selected stock
			stock_data = lookup(stock_symbol)

			# if the selected stock was not found show an error
			if stock_data == None:

				return HttpResponse(json.dumps({"error": "1"}))

			# if the selected stock was found send the data to the client
			else:

				return HttpResponse(json.dumps(stock_data))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def history(request):
	''' This view is responsible for presenting the history page to users.
	This includes presenting the financial statement 
	and transaction history tables, the edit starting balance,
	the add entry and edit entry forms. POST requests sent to this view
	result in an error message. '''

	# if the client sent a GET request
	if request.method == g_get_method:

		# find the user's financial statement and transaction history
		financial_statement = Statement.objects.filter(user = request.user)
		transaction_history = Transaction.objects.filter(user = request.user)

		# place data in a dictionary
		context = {"financial_statement": financial_statement, "transaction_history": transaction_history}

		# render the history page, passing in the user's data as context
		html = "finance/history.html"
		return render(request, html, context = context)

	# if the client sent a POST request show an error message
	else:

		return show_error_message(request, g_invalid_request)

def register(request):
	'''This view is responsible for presenting the register form to users. 
	It registers users who fill out the register form with valid information and submit it. 
	It also sets the starting balance of new users according to their choices.'''
	
	# if the user is logged in, log them out
	if request.user.is_authenticated:
		logout(request)
	
	# if the client sent a GET request, present the register form
	if request.method == g_get_method:

		html = "finance/register.html"

		return render(request, html)
		

	# if the client sent a POST request
	else:	
		
		# if the input is valid
		try:

			# store the user's input in variables
			username = request.POST["username"]
			password = request.POST["password"]
			confirmation = request.POST["confirmation"]
			
			# if the username selected by the user is taken
			if len(User.objects.filter(username = username)) != 0:
				error = {"error": "1"}
				
				# notify the user by showing them an appropriate error message
				return HttpResponse(json.dumps(error))
			
			# if the user's input passed all checks
			else:
				
				# create a new user with the username and password specified by the user
				user = User.objects.create_user(username = username, password = password)
				user.save()
				
				# set the default starting balance to 10000.00 USD
				balance = 10000.00
				
				# if the user has specified a starting balance
				if request.POST["starting_balance"]:
					
					# change the user's starting balance to the specified amount
					balance = round(float(request.POST["starting_balance"]), 2)
						
				# save the starting balance in the database
				cash = Cash(user = user, cash = balance)
				cash.save()

				# add the starting balance to the financial statement
				starting_balance_statement = Statement(statement_type = "Balance", title = "Starting balance",
					amount = balance, user = user)
				starting_balance_statement.save()
				
				# redirect the user to the main page
				login(request, user)
				return HttpResponseRedirect(reverse("index"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def sell(request):
	''' This view is responsible for selling shares of stocks
	according to the user's requests. This includes finding the
	selected stock and its current price, deciding whether or not
	the transaction can be carried out and executing the database
	operations that are necessary. GET requests sent to this view
	result in an error message. '''

	# if the client sent a GET request show an error message
	if request.method == g_get_method:

		return show_error_message(request, g_invalid_request)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:

			# place the user's input into variables
			stock_symbol = request.POST["symbol"]
			stock_shares = int(request.POST["shares"])

			# find the selected stock
			selected_stock = Portfolio.objects.get(user = request.user, stock = stock_symbol)

			# if the user owns no shares of the stock show an error
			if selected_stock.shares == 0:

				return HttpResponse(json.dumps({"error": "1"}))

			# if the user does not own enough shares of the stock show an error
			elif selected_stock.shares < stock_shares:

				return HttpResponse(json.dumps({"error": "2"}))

			# if the transaction can be executed
			else:

				# update the user's portfolio with the transaction's data
				stock_data = lookup(stock_symbol)
				transaction_value = stock_shares * stock_data["price"]

				new_share_count = int(selected_stock.shares) - stock_shares
				selected_stock.shares = new_share_count

				new_stake_value = float(selected_stock.value) - transaction_value
				selected_stock.value = new_stake_value

				selected_stock.current_price = stock_data["price"]

				# add the value of the transaction to the user's balance
				user_cash = Cash.objects.get(user = request.user)
				new_balance = float(user_cash.cash) + transaction_value
				user_cash.cash = new_balance

				# add the transaction to the user's transaction history
				history = Transaction(user = request.user, transaction_type = "Sell", stock = stock_data["symbol"],
					price = stock_data["price"], shares = stock_shares)

				# add the transaction to the user's financial statement
				statement = Statement(statement_type = "Income", title = "Selling shares", amount = transaction_value,
					user = request.user)

				# save all changes
				selected_stock.save()
				user_cash.save()
				history.save()
				statement.save()

				# redirect the user to the stocks page to showcase the changes
				return HttpResponseRedirect(reverse("stocks"))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)

def change_pw(request):
	''' This view is responsible for changing passwords of users.
	This includes processing user requests and making changes
	in the database according to them. '''

	# if the client sent a GET request present the change password form
	if request.method == g_get_method:

		html = "finance/change-pw.html"
		return render(request, html)

	# if the client sent a POST request
	else:

		# if the input is valid
		try:
			# place input into variables
			old_password = request.POST["old_password"]
			new_password = request.POST["new_password"]
			confirmation = request.POST["confirmation"]

			# if the input is correct change the user's password
			authenticated_user = authenticate(request, username = request.user.username, password = old_password)

			if authenticated_user != None:

				request.user.set_password(new_password)
				request.user.save()
				login(request, request.user)

				# redirect the user to the main page
				return HttpResponseRedirect(reverse("index"))

			# if the old password is incorrect show an error
			else:

				error = {"error": "1"}
				return HttpResponse(json.dumps(error))

		# if the input is incomplete or some other error occured show an error message
		except:

			return show_error_message(request, g_error_occured)