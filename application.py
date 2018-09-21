import os

from cs50 import SQL, eprint
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import time, schedule
from flask_celery import make_celery
from helpers import apology, login_required, lookup, usd, daily, weekly, monthly

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#configure celery for the asynchronous tasks
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0' #http://ide50-andrewhun995.cs50.io:8080/

celery = make_celery(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")

@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    '''Show summary of finances and settings'''
    # variables for the financial summary table
    expenses = db.execute("SELECT SUM(amount) FROM statement WHERE user_id = :iden AND type = 'expense'", iden = session["user_id"])
    income = db.execute("SELECT SUM(amount) FROM statement WHERE user_id = :iden AND type = 'income'", iden = session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])
    # variables for the recurring entries table
    id_ = db.execute("SELECT id FROM auto_values WHERE user_id = :iden", iden = session["user_id"])
    type_ = db.execute("SELECT type FROM auto_values WHERE user_id = :iden", iden = session["user_id"])
    title = db.execute("SELECT title FROM auto_values WHERE user_id = :iden", iden = session["user_id"])
    amount = db.execute("SELECT amount FROM auto_values WHERE user_id = :iden", iden = session["user_id"])
    time2 = db.execute("SELECT time FROM auto_values WHERE user_id = :iden", iden = session["user_id"])
    frequency = db.execute("SELECT frequency FROM auto_values WHERE user_id = :iden", iden = session["user_id"])
    j = len(id_)
    # ensure that grand total does not throw an exception
    if type(income[0]["SUM(amount)"]) == type(None) and type(expenses[0]["SUM(amount)"]) == type(None):
        grand_total = 0
    elif type(expenses[0]["SUM(amount)"]) == type(None):
        grand_total = income[0]["SUM(amount)"]
    elif type(income[0]["SUM(amount)"]) == type(None):
        grand_total = -1 * (expenses[0]["SUM(amount)"])
    else:
        grand_total = income[0]["SUM(amount)"] - expenses[0]["SUM(amount)"]

    return render_template("index.html", expenses = expenses, income = income, grand_total = usd(grand_total), usd = usd,
     id_ = id_, type_ = type_, title = title, amount = amount, time = time2, frequency = frequency, j = j, cash = cash[0]['cash'])

@app.route("/auto_values", methods = ["GET", "POST"])
@login_required
def auto_values():
    '''Adds recurring income and expense elements'''
    # get the form input and place it into variables
    frequency = request.form.get("frequency")
    auto_type = request.form.get("auto_type")
    auto_title = str(request.form.get("auto_title"))
    auto_amount = request.form.get("auto_amount")
    # check for missing or invalid input
    if not frequency:
        return jsonify({"error": "1"})
    elif not auto_type:
        return jsonify({"error": "2"})
    elif not auto_title:
        return jsonify({"error": "3"})
    elif not auto_amount:
        return jsonify({"error": "4"})
    # valid input
    else:
        # add recurring element to the auto_values table
        db.execute("INSERT INTO auto_values(type, title, amount, user_id, frequency) "
        "VALUES(:my_type, :title, :amount, :iden, :frequency)",
        my_type = auto_type, title = auto_title, amount = float(auto_amount),
        iden = session["user_id"], frequency = frequency)

    return redirect("/")
'''
DOES NOT WORK
@celery.task(name = "application.daily_celery")
def daily_celery():
    daily().delay()

@celery.task(name = "application.weekly_celery")
def weekly_celery():
    weekly().delay()

@celery.task(name = "application.monthly_celery")
def monthly_celery():
    monthly().delay()

celery.conf.beat_schedule = {
    'add-every-minute': {
        'task': 'application.daily_celery',
        'schedule': 60.0
    },
}
celery.conf.beat_schedule = {
    'add-every-5-minutes': {
        'task': 'application.weekly_celery',
        'schedule': 300.0
    },
}
celery.conf.beat_schedule = {
    'add-every-10-minutes': {
        'task': 'application.monthly_celery',
        'schedule': 600.0
    },
}
celery.conf.timezone = 'UTC'

'''
@app.route("/manual_values", methods = ["GET", "POST"])
@login_required
def manual_values():
    '''Adds income and expense elements to the financial history table'''
    # get the form input and place it into variables
    manual_type = request.form.get("manual_type")
    manual_title = str(request.form.get("manual_title"))
    manual_amount = request.form.get("manual_amount")
    # check for missing or invalid input
    if not manual_type:
        return jsonify({"error": "1"})
    elif not manual_title:
        return jsonify({"error": "2"})
    elif not manual_amount:
        return jsonify({"error": "3"})
    # valid input
    else:
        # grab the user's cash in the users table
        cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])
        # add the entry's amount to the cash if its type is income
        if manual_type == "income":
            db.execute("UPDATE users SET cash = :cash + :amount WHERE id = :iden",
            amount = float(manual_amount), iden = session["user_id"], cash = cash[0]["cash"])
        # subtract the entry's amount from the cash if its type is expense
        else:
            db.execute("UPDATE users SET cash = :cash - :amount WHERE id = :iden",
            amount = float(manual_amount), iden = session["user_id"], cash = cash[0]["cash"])
        # add the element to the statement table
        db.execute("INSERT INTO statement(type, title, amount, user_id) "
        "VALUES(:my_type, :title, :amount, :iden)",
        my_type = manual_type, title = manual_title, amount = float(manual_amount),
        iden = session["user_id"])
    return redirect("/")

@app.route("/edit_auto", methods = ["GET", "POST"])
@login_required
def edit_auto():
    """Edit recurring income and expense elements"""
    # place form input into variables
    edit_id = request.form.get("edit_id")
    edit_type = request.form.get("edit_type")
    edit_title = request.form.get("edit_title")
    edit_amount = request.form.get("edit_amount")
    edit_frequency = request.form.get("edit_frequency")
    iden = session["user_id"]
    # missing entry ID branch
    if not edit_id:
        return jsonify({"error": "1"})
    # invalid entry ID branch
    elif not db.execute("SELECT * FROM auto_values WHERE id = :edit_id AND user_id = :iden", edit_id = edit_id,
    iden = iden):
        return jsonify({"error":"2"})
    # all other fields are empty branch
    elif not edit_type and not edit_title and not edit_amount and not edit_frequency:
        return redirect("/")
    # "proper" input branch
    else:
        # place either the input from the form or the original values of each relevant column
        # in these variables and use them for updating the database
        my_type = db.execute("SELECT CASE WHEN :edit_type = '' THEN type ELSE :edit_type END FROM auto_values WHERE id = :edit_id AND user_id = :iden",
        edit_type = edit_type, edit_id = edit_id, iden = iden)
        my_title = db.execute("SELECT CASE WHEN :edit_title = '' THEN title ELSE :edit_title END FROM auto_values WHERE id = :edit_id AND user_id = :iden",
        edit_title = edit_title, edit_id = edit_id, iden = iden)
        my_amount = db.execute("SELECT CASE WHEN :edit_amount = '' THEN amount ELSE :edit_amount END FROM auto_values WHERE id = :edit_id AND user_id = :iden",
        edit_amount = edit_amount, edit_id = edit_id, iden = iden)
        my_frequency = db.execute("SELECT CASE WHEN :edit_frequency = '' THEN frequency ELSE :edit_frequency END FROM auto_values WHERE id = :edit_id AND user_id = :iden",
        edit_frequency = edit_frequency, edit_id = edit_id, iden = iden)
        # either update auto_values with the new values or keep the old ones if there are no new values
        db.execute("UPDATE auto_values SET type = :my_type, title = :my_title, amount = :my_amount, frequency = :my_frequency "
        "WHERE id = :edit_id AND user_id = :iden", edit_id = edit_id, my_type = my_type[0][list(my_type[0].keys())[0]],
        my_title = my_title[0][list(my_title[0].keys())[0]], my_amount = float(my_amount[0][list(my_amount[0].keys())[0]]) ,
        my_frequency = my_frequency[0][list(my_frequency[0].keys())[0]], iden = iden)
    return redirect("/")

@app.route("/edit_hist", methods = ["GET", "POST"])
@login_required
def edit_hist():
    """Edit income and expense elements in the financial history table"""
    # place form input into variables
    edit_hist_id = request.form.get("edit_hist_id")
    edit_hist_type = request.form.get("edit_hist_type")
    edit_hist_title = request.form.get("edit_hist_title")
    edit_hist_amount = request.form.get("edit_hist_amount")
    iden = session["user_id"]
    # missing entry ID branch
    if not edit_hist_id:
        return jsonify({"error": "1"})
    # invalid entry ID branch
    elif not db.execute("SELECT * FROM statement WHERE id = :edit_hist_id AND user_id = :iden", edit_hist_id = edit_hist_id,
    iden = iden):
        return jsonify({"error":"2"})
    # all other fields are empty branch
    elif not edit_hist_type and not edit_hist_title and not edit_hist_amount:
        return redirect("/history")
    # "proper" input branch
    else:
        # grab the old type of the selected entry and the user's cash from the users table
        old_type = db.execute("SELECT type FROM statement WHERE user_id = :iden AND id = :edit_hist_id"
        , iden = iden, edit_hist_id = edit_hist_id)[0]["type"]
        cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])
        # prepare variables for updating the statement table
        my_type = db.execute("SELECT CASE WHEN :edit_hist_type = '' THEN type ELSE :edit_hist_type END FROM statement WHERE id = :edit_hist_id AND user_id = :iden",
        edit_hist_type = edit_hist_type, edit_hist_id = edit_hist_id, iden = iden)
        my_title = db.execute("SELECT CASE WHEN :edit_hist_title = '' THEN title ELSE :edit_hist_title END FROM statement WHERE id = :edit_hist_id AND user_id = :iden",
        edit_hist_title = edit_hist_title, edit_hist_id = edit_hist_id, iden = iden)
        my_amount = db.execute("SELECT CASE WHEN :edit_hist_amount = '' THEN amount ELSE :edit_hist_amount END FROM statement WHERE id = :edit_hist_id AND user_id = :iden",
        edit_hist_amount = edit_hist_amount, edit_hist_id = edit_hist_id, iden = iden)
        # grab the old amount of the selected entry
        amount = db.execute("SELECT amount FROM statement WHERE id = :edit_hist_id AND user_id = :iden",
        edit_hist_id = edit_hist_id, iden = iden)
        #update the users cash according to the input
        # if the old and new types are both "income", subtract the old amount from the user's cash
        # and add the new amount to it
        if my_type[0][list(my_type[0].keys())[0]] == "income" and old_type == "income":
            db.execute("UPDATE users SET cash = :cash - :amount + :my_amount WHERE id = :iden",
            amount = amount[0]["amount"], my_amount = float(my_amount[0][list(my_amount[0].keys())[0]]),
            iden = iden, cash = cash[0]["cash"])
        # if the old type is "expense" while the new one is "income" add both the old and
        # the new amount to the cash
        elif my_type[0][list(my_type[0].keys())[0]] == "income" and old_type == "expense":
            db.execute("UPDATE users SET cash = :cash + :amount + :my_amount WHERE id = :iden",
            amount = amount[0]["amount"], my_amount = float(my_amount[0][list(my_amount[0].keys())[0]]),
            iden = iden, cash = cash[0]["cash"])
        # if both the old type and the new one are "income" add the old amount to the user's cash
        # and subtract the new one from it
        elif my_type[0][list(my_type[0].keys())[0]] == "expense" and old_type == "expense":
            db.execute("UPDATE users SET cash = :cash + :amount - :my_amount WHERE id = :iden",
            amount = amount[0]["amount"], my_amount = float(my_amount[0][list(my_amount[0].keys())[0]]),
            iden = iden, cash = cash[0]["cash"])
        # if the old type is "income" and the new type is "expense" subtract both the old and
        # the new amounts from the user's cash
        else:
            db.execute("UPDATE users SET cash = :cash - :amount - :my_amount WHERE id = :iden",
            amount = amount[0]["amount"], my_amount = float(my_amount[0][list(my_amount[0].keys())[0]]),
            iden = iden, cash = cash[0]["cash"])

        db.execute("UPDATE statement SET type = :my_type, title = :my_title, amount = :my_amount "
        "WHERE id = :edit_hist_id AND user_id = :iden", edit_hist_id = edit_hist_id,
        my_type = my_type[0][list(my_type[0].keys())[0]],
        my_title = my_title[0][list(my_title[0].keys())[0]],
        my_amount = float(my_amount[0][list(my_amount[0].keys())[0]]) , iden = iden)
    return redirect("/history")

@app.route("/delete_auto", methods = ["GET", "POST"])
@login_required
def delete_auto():
    '''Delete recurring income and expense elements'''
    # get the entry ID and the user ID
    delete_id = request.form.get("delete_id")
    iden = session["user_id"]

    check = request.form.get("check")
    # if the "delete all recurring entries" checkbox is checked,
    # delete all recurring entries
    if check == "check":
        db.execute("DELETE FROM auto_values WHERE user_id = :iden", iden = iden)
        return redirect("/")
    # missing entry ID branch
    elif not delete_id:
        return jsonify({"error": "1"})
    # invalid entry ID branch
    elif not db.execute("SELECT * FROM auto_values WHERE id = :delete_id AND user_id = :iden",
    delete_id = delete_id, iden = iden):
        return jsonify({"error": "2"})
    # valid input branch
    else:
        # delete appropriate row from the auto_values table
        db.execute("DELETE FROM auto_values WHERE id = :delete_id AND user_id = :iden",
        delete_id = delete_id, iden = iden)
    return redirect("/")

@app.route("/delete_hist", methods = ["GET", "POST"])
@login_required
def delete_hist():
    '''Delete income and expense elements from the financial history table'''
    # get the entry ID and the user ID
    delete_hist_id = request.form.get("delete_hist_id")
    iden = session["user_id"]
    check = request.form.get("check")
    # if the "delete all entries" checkbox is checked, delete all
    # entries from the statement, history and portfolio tables and reset
    # the starting balance of the account to 10000 USD
    if check == "check":
        db.execute("DELETE FROM statement WHERE user_id = :iden", iden = iden)
        db.execute("DELETE FROM history WHERE user_id = :iden", iden = iden)
        db.execute("DELETE FROM portfolio WHERE user_id = :iden", iden = iden)
        db.execute("UPDATE users SET cash = 10000.00 WHERE id = :iden", iden = iden)
        cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = iden)[0]["cash"]
        db.execute("INSERT INTO statement (type, title, amount, user_id) "
        "VALUES ('balance', 'starting balance', :cash, :iden)", cash = cash, iden = iden)
    # missing entry ID branch
    elif not delete_hist_id:
        return jsonify({"error": "1"})
    # invalid entry ID branch
    elif not db.execute("SELECT * FROM statement WHERE id = :delete_hist_id AND user_id = :iden",
    delete_hist_id = delete_hist_id, iden = iden):
        return jsonify({"error": "2"})
    # valid input branch
    else:
        # grab the type and amount of the selected entry and the user's cash
        amount = db.execute("SELECT amount FROM statement WHERE id = :delete_hist_id AND user_id = :iden",
        delete_hist_id = delete_hist_id, iden = iden)
        my_type = db.execute("SELECT type FROM statement WHERE id = :delete_hist_id AND user_id = :iden",
        delete_hist_id = delete_hist_id, iden = iden)
        cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = iden)[0]["cash"]
        # if entry's type is income subtract its amount from the user's cash
        if my_type[0]["type"] == "income":
            db.execute("UPDATE users SET cash = :cash - :amount WHERE id = :iden",
            amount = amount[0]["amount"], iden = iden, cash = cash)
        # if the entry's type is expense add its value to the user's cash
        else:
            db.execute("UPDATE users SET cash = :cash + :amount WHERE id = :iden",
            amount = amount[0]["amount"], iden = iden, cash = cash)
        db.execute("DELETE FROM statement WHERE id = :delete_hist_id AND user_id = :iden",
        delete_hist_id = delete_hist_id, iden = iden)
    return redirect("/history")

@app.route("/edit_balance", methods = ["GET", "POST"])
@login_required
def edit_balance():
    '''Changes the starting balance in the financial history table'''
    # get the new balance from the form
    edit_balance_amount = request.form.get("edit_balance_amount")
    # missing amount branch
    if not edit_balance_amount:
        return jsonify({"error" : "1"})
    # success
    else:
        # grab the user's cash an the old starting balance
        cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])
        old_balance = db.execute("SELECT amount FROM statement WHERE user_id = :iden AND title = 'starting balance'",
        iden = session["user_id"])
        # update the starting balance in the statement table
        db.execute("UPDATE statement SET amount = :amount WHERE user_id = :iden AND title = 'starting balance'",
        amount = float(edit_balance_amount), iden = session["user_id"])
        # subtract the old balance from the user's cash and add the new one to it
        db.execute("UPDATE users SET cash = :cash - :old_balance + :amount WHERE id = :iden",
        amount = float(edit_balance_amount), old_balance = float(old_balance[0]["amount"]),
        iden = session["user_id"], cash = cash[0]["cash"])
    # refresh page to showcase changes
    return redirect("/history")

@app.route("/stocks", methods = ["GET", "POST"])
@login_required
def stocks():
    """Show portfolio of stocks"""
    # prepare necessary variables
    stocks = db.execute("SELECT stock FROM portfolio WHERE user_id = :iden", iden = session["user_id"])
    cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])
    # set up and style shares, current price value and grand total
    shares = db.execute("SELECT shares FROM portfolio WHERE user_id = :iden", iden = session["user_id"])
    i = len(stocks)
    current_price = []
    for j in range(i) :
        current_price.append(lookup(stocks[j]["stock"])["price"])
    value = []
    for k in range(i):
        value.append(shares[k]['shares'] * current_price[k])
    grand_total = cash[0]['cash']
    for m in range(i):
        grand_total += value[m]
    grand_total = usd(grand_total)
    for n in range(i):
        current_price[n] = usd(current_price[n])
        value[n] = usd(value[n])
    # show the HTML table with these values to the user
    return render_template("stocks.html", i = i, stocks = stocks, current_price = current_price,
    value = value, cash = usd(cash[0]["cash"]), grand_total = grand_total, shares = shares)



@app.route("/buy", methods = ["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # user reaches the route via GET method
    if request.method == "GET":
        return render_template("buy.html")
    # user reaches the route via POST method
    else:
        # set up variables to be used
        shares = request.form.get("shares")
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])
        # check for valid input
        # return error codes as JSON objects so that JavaScript
        # can show appropriate messages to the user
        # missing stock symbol
        if not symbol:
            return jsonify({"error": "1"})
        # missing number of shares
        elif not shares:
            return jsonify({"error": "2"})
        # invalid number of shares
        elif int(shares) < 1:
            return jsonify({"error": "3"})
        # invalid stock symbol (no stock found)
        elif not stock:
            return jsonify({"error": "4"})
        # insufficient funds
        elif (int(shares) * stock["price"]) > cash[0]['cash']:
            return jsonify({"error": "5"})
        # valid input and sufficient funds
        else:
            owned_stocks = db.execute("SELECT stock FROM portfolio WHERE user_id = :iden AND stock = :stock"
            , iden = session["user_id"], stock = str(stock["symbol"]))
            # either create a new entry in the portfolio or update an existing one depending on
            # whether or not the user has shares in the stock chosen to be purchased
            if not owned_stocks:
                db.execute("INSERT INTO portfolio(user_id, stock, current_price, shares) "
                "VALUES(:user_id, :stock, :price, :shares)",
                user_id = session["user_id"], stock = str(stock["symbol"]), price = stock["price"],
                shares = int(shares))
            else:
                db.execute("UPDATE portfolio SET current_price = {0}, shares = shares + {1}"
                " WHERE user_id = :iden AND stock = :stock".format(stock["price"], int(shares)),
                iden = session["user_id"], stock = stock["symbol"])
            # add the transaction to the statement table as an expense
            db.execute("INSERT INTO statement(type, title, amount, user_id) "
            "VALUES ('expense', 'buying shares', :amount, :iden)", iden = session["user_id"],
            amount = int(shares) * stock["price"])

            # enter the transaction in history
            db.execute("INSERT INTO history(user_id, transaction_type, stock, price, shares)"
            " VALUES(:user_id, 'buy', :stock, :price, :shares)", user_id = session["user_id"], stock = str(stock["symbol"]),
             price = stock["price"], shares = int(shares))
            # decrease the user's cash with the transactions's worth in the database
            db.execute("UPDATE users SET cash = cash - {0} WHERE id = :iden".format(int(shares) * stock["price"]),
            iden = session["user_id"])
            # redirect user to the main page (redundant)
            return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions and finances"""
    # transactions
    transaction_type = db.execute("SELECT transaction_type FROM history WHERE user_id = :iden",
    iden = session["user_id"])
    stock = db.execute("SELECT stock FROM history WHERE user_id = :iden",
    iden = session["user_id"])
    price = db.execute("SELECT price FROM history WHERE user_id = :iden",
    iden = session["user_id"])
    shares = db.execute("SELECT shares FROM history WHERE user_id = :iden",
    iden = session["user_id"])
    time = db.execute("SELECT time FROM history WHERE user_id = :iden",
    iden = session["user_id"])
    i = len(time)
    # finances
    id_ = db.execute("SELECT id FROM statement WHERE user_id = :iden", iden = session["user_id"])
    time2 = db.execute("SELECT time FROM statement WHERE user_id = :iden", iden = session["user_id"])
    amount = db.execute("SELECT amount FROM statement WHERE user_id = :iden", iden = session["user_id"])
    title = db.execute("SELECT title FROM statement WHERE user_id = :iden", iden = session["user_id"])
    type_ = db.execute("SELECT type FROM statement WHERE user_id = :iden", iden = session["user_id"])
    k = len(time2)
    return render_template("history.html", stock = stock, i = i, price = price,
    transaction_type = transaction_type, shares = shares, time = time, time2 = time2,
     type_ = type_, amount = amount, title = title, k = k, usd = usd, id_ = id_)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return jsonify({"error": "1"})

        # Ensure password was submitted
        elif not request.form.get("password"):
            return jsonify({"error": "2"})

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return jsonify({"error": "3"})
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # get the information from the quote form
    symbol = request.form.get("symbol")
    if not symbol:
        return jsonify({"error": "1"})
    price = lookup(symbol)
    # if the user reached the route via POST and their submission was valid, return the
    # result of lookup for them
    if request.method == "POST":
        if not price:
            return jsonify({"error": "1"})
        else:
            return jsonify(price)


@app.route("/register", methods=["GET", "POST"])
def register():

    """Register user"""
    # user reached the route via POST
    if request.method == "POST":
        starting_balance = request.form.get("starting_balance")
        # check the username to see if it is missing
        if not request.form.get("username"):
            return jsonify({"error": "1"})
        # check the password and its confirmation to see if either of them are missing
        # or if they do not match
        elif not request.form.get("password"):
            return jsonify({"error": "2"})
        elif not request.form.get("confirmation"):
            return jsonify({"error": "3"})
        elif request.form.get("password") != request.form.get("confirmation"):
            return jsonify({"error": "4"})
        # add the user to the database
        hashed = generate_password_hash(request.form.get("password"))
        username = request.form.get("username")
        # if the username is taken notify the user
        if not (db.execute("INSERT INTO users(username, hash) VALUES(:username, :hashed)",
        username = username, hashed = hashed)):
            return jsonify({"error": "5"})
        else:
            # once the registration process is complete, log the user in
            rows = db.execute("SELECT * FROM users WHERE username = :username", username = username)
            session["user_id"] = rows[0]["id"]
            # if the user has entered a starting balance update their cash with the value
            if starting_balance:
                db.execute("UPDATE users SET cash = :starting_balance WHERE id = :iden",
                starting_balance = float(starting_balance), iden = session["user_id"])
            # grab the user's cash and present it as the starting balance in the statement table
            cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])
            db.execute("INSERT INTO statement(type, title, amount, user_id) "
            "VALUES('balance', 'starting balance', :amount, :iden)", amount = cash[0]['cash'],
            iden = session["user_id"])
        return redirect("/")

    # user reached the route via GET (through a redirect or a link)
    else:
        return render_template("register.html", usd = usd)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # prepary the variables used in sell.html
    stocks = db.execute("SELECT stock FROM portfolio WHERE user_id = :iden", iden = session["user_id"])
    i = len(stocks)
    eprint(i)
    # user reaches the route via the POST method (by filling out the HTML form)
    if request.method == "POST":
        # prepare the variables for the database operations
        my_symbol = str(request.form.get("symbol"))
        my_stock = db.execute("SELECT stock FROM portfolio WHERE user_id = :iden AND stock = :stock",
        iden = session["user_id"], stock = my_symbol)
        my_shares = db.execute("SELECT shares FROM portfolio WHERE user_id = :iden AND stock = :stock",
        iden = session["user_id"], stock = my_symbol)
        selling_shares = request.form.get("shares")
        eprint(my_symbol)
        eprint(selling_shares)
        # catch any errors in the input and return the appropriate error code
         # missing stock symbol branch
        if not my_symbol:
            return jsonify({"error": "1"})
        # missing number of shares branch
        elif not selling_shares:
            return jsonify({"error": "2"})
        # invalid number of shares branch
        elif int(selling_shares) < 1:
            return jsonify({"error": "3"})
        # stock not in portfolio branch
        elif not my_stock:
            return jsonify({"error": "4"})
        # no shares owned branch
        elif my_shares[0]["shares"] == 0:
            return jsonify({"error": "5"})
        # not enough shares owned branch
        elif my_shares[0]["shares"] < int(selling_shares):
            return jsonify({"error": "6"})
        # the user's input is valid
        else:
            # enter the transaction into the statement table as an income entry
            my_price = lookup(my_symbol)["price"]
            db.execute("INSERT INTO statement(type, title, amount, user_id) "
            "VALUES ('income', 'selling shares', :amount, :iden)",
            amount = my_price * int(selling_shares), iden = session["user_id"])
            # add the transaction to the history table, update the user's cash and portfolio
            db.execute("INSERT INTO history(user_id, transaction_type, stock, price, shares)"
            " VALUES (:iden, 'sell', :stock, :price, :shares)", iden = session["user_id"],
            stock = my_symbol, price = my_price, shares = int(selling_shares))
            db.execute("UPDATE portfolio SET shares = shares - {0} "
            "WHERE user_id = :iden AND stock = :stock".format(int(selling_shares)), iden = session["user_id"], stock = my_symbol)
            db.execute("UPDATE users SET cash = cash + {0} WHERE id = :iden"
            .format(my_price * int(selling_shares)), iden = session["user_id"])
        # redirect the user to index.html
        return redirect("/")
    # user reached the route via the GET method
    else:
        # present the HTML form which sell.html contains to the user
        return render_template("sell.html", stocks = stocks, i = i)

@app.route("/change-pw", methods=["GET", "POST"])
@login_required
def change_pw():
    '''Changes passwords '''
    # user reaches the route via the GET method
    if request.method == "GET":
        # present the user with the HTML form
        return render_template("change-pw.html")
    # user reaches the route via the POST method
    else:
        # place user input into variables, cast as strings
        old_password = str(request.form.get("old_password"))
        new_password = str(request.form.get("new_password"))
        confirmation = str(request.form.get("confirmation"))
        old_hash = generate_password_hash(old_password)
        real_old_hash = db.execute("SELECT hash FROM users WHERE id = :iden", iden = session["user_id"])

        eprint(old_password)
        eprint(real_old_hash[0]["hash"])
        eprint(check_password_hash(real_old_hash[0]["hash"], old_password))
        # check the user's input for any errors: empty fields, old pw same as new and
        # confirmation not matching the pw, return appropriate error code in JSON
        # missing old password branch
        if not old_password:
            return jsonify({"error": "1"})
        # missing new password branch
        elif not new_password:
            return jsonify({"error": "2"})
        # missing confirmation branch
        elif not confirmation:
            return jsonify({"error": "3"})
        # old pw same as new branch
        elif old_password == new_password:
            return jsonify({"error": "4"})
        # password mismatch branch
        elif new_password != confirmation:
            return jsonify({"error": "5"})
        # old pw wrong branch
        elif not (check_password_hash(real_old_hash[0]["hash"], old_password)):
            return jsonify({"error": "6"})
        # valid user input
        else:
            # update the users table in the database by placing the new_password's hash
            # into the hash column (for the user who's currently logged in)
            new_hash = generate_password_hash(new_password)
            db.execute("UPDATE users SET hash = :new_hash WHERE id = :iden", new_hash = new_hash,
            iden = session["user_id"])
            # redirect the user to the main page
            return redirect("/")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
