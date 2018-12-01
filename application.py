import os

from cs50 import SQL, eprint
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import time, schedule
# from flask_celery import make_celery
from helpers import apology, login_required, lookup, usd, daily, weekly, monthly
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, DateTime, TIMESTAMP, Sequence, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text, func
import warnings

warnings.simplefilter('ignore')


# Configure application
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

#configure celery for the asynchronous tasks
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0' #http://ide50-andrewhun995.cs50.io:8080/

# celery = make_celery(app)

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
'''
Old version
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")
'''
# set up the database using SQLAlchemy
engine = create_engine(os.getenv("DATABASE_URL"))
conn = engine.connect()

# create  catalog of Tables
metadata = MetaData()

# create the auto_values table
auto_values = Table("auto_values", metadata,
    Column('id', Integer, Sequence('auto_values_id_seq'), primary_key = True),
    Column('type', String),
    Column('title', String),
    Column('amount', Float),
    Column('user_id', Integer),
    Column('time', TIMESTAMP, server_default = func.now()),
    Column('frequency', String))

#create the history table
history = Table('history', metadata,
    Column('id', Integer, Sequence('history_id_seq'), primary_key = True),
    Column('user_id', Integer),
    Column('transaction_type', String),
    Column('stock', String),
    Column('price', Float),
    Column('shares', Integer),
    Column('time', TIMESTAMP, server_default = func.now()))

#create the portfolio table
portfolio = Table('portfolio', metadata,
    Column('id', Integer, Sequence('portfolio_id_seq'), primary_key = True),
    Column('user_id', Integer),
    Column('stock', String),
    Column('current_price', Float),
    Column('shares', Integer))

# create the statement table

statement = Table('statement', metadata,
    Column('id', Integer, Sequence('statement_id_seq'), primary_key = True),
    Column('type', String),
    Column('title', String),
    Column('amount', Float),
    Column('user_id', Integer),
    Column('time', TIMESTAMP, server_default = func.now()))

# create the users table
users = Table('users', metadata,
    Column('id', Integer, Sequence('users_id_seq')),
    Column('username', String, primary_key = True),
    Column('hash', String),
    Column('cash', Float))

# create a session for the database
# this is done in order to separate operations that belong to different users
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods = ["GET", "POST"])
@login_required
def index():
    iden = session["user_id"]
    '''Show summary of finances and settings'''
    # variables for the financial summary table
    expenses = db.execute(text("SELECT SUM(amount) FROM statement WHERE user_id = :iden AND type = 'expense'"), {'iden': iden}).fetchone()
    income = db.execute(text("SELECT SUM(amount) FROM statement WHERE user_id = :iden AND type = 'income'"), {'iden': iden}).fetchone()
    cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': iden}).fetchone()
    # variables for the recurring entries table
    id_ = db.execute(text("SELECT id FROM auto_values WHERE user_id = :iden"), {'iden': iden}).fetchall()
    type_ = db.execute(text("SELECT type FROM auto_values WHERE user_id = :iden"), {'iden': iden}).fetchall()
    title = db.execute(text("SELECT title FROM auto_values WHERE user_id = :iden"), {'iden': iden}).fetchall()
    amount = db.execute(text("SELECT amount FROM auto_values WHERE user_id = :iden"), {'iden': iden}).fetchall()
    time2 = db.execute(text("SELECT time FROM auto_values WHERE user_id = :iden"), {'iden': iden}).fetchall()
    frequency = db.execute(text("SELECT frequency FROM auto_values WHERE user_id = :iden"), {'iden': iden}).fetchall()
    j = len(id_)
    # ensure that grand total does not throw an exception
    if type(income[0]) == type(None) and type(expenses[0]) == type(None):
        grand_total = 0
    elif type(expenses[0]) == type(None):
        grand_total = income[0]
    elif type(income[0]) == type(None):
        grand_total = -1 * (expenses[0])
    else:
        grand_total = income[0] - expenses[0]

    db.commit()
    return render_template("index.html", expenses = expenses, income = income, grand_total = usd(grand_total), usd = usd,
     id_ = id_, type_ = type_, title = title, amount = amount, time = time2, frequency = frequency, j = j, cash = cash[0])

@app.route("/auto_values", methods = ["GET", "POST"])
@login_required
def auto_values():
    '''Add recurring income and expense elements'''
    # get the form input and place it into variables
    frequency = request.form.get("frequency")
    auto_type = request.form.get("auto_type")
    auto_title = str(request.form.get("auto_title"))
    auto_amount = request.form.get("auto_amount")

    # add recurring element to the auto_values table
    db.execute(text("INSERT INTO auto_values(type, title, amount, user_id, frequency) "
    "VALUES(:my_type, :title, :amount, :iden, :frequency)"),
    {'my_type': auto_type, 'title': auto_title, 'amount': float(auto_amount),
        'iden': session["user_id"], 'frequency': frequency})
    db.commit()

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
    '''Add income and expense elements to the financial history table'''
    # get the form input and place it into variables
    manual_type = request.form.get("manual_type")
    manual_title = str(request.form.get("manual_title"))
    manual_amount = request.form.get("manual_amount")

    # grab the user's cash in the users table
    cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': session["user_id"]}).fetchone()
    # add the entry's amount to the cash if its type is income
    if manual_type == "income":
        db.execute(text("UPDATE users SET cash = :cash + :amount WHERE id = :iden"),
        {'amount': float(manual_amount), 'iden': session["user_id"], 'cash': cash[0]})
    # subtract the entry's amount from the cash if its type is expense
    else:
        db.execute(text("UPDATE users SET cash = :cash - :amount WHERE id = :iden"),
        {'amount': float(manual_amount), 'iden': session["user_id"], 'cash': cash[0]})
    # add the element to the statement table
    db.execute(text("INSERT INTO statement(type, title, amount, user_id) "
            "VALUES(:my_type, :title, :amount, :iden)"),
    {'my_type': manual_type, 'title': manual_title, 'amount': float(manual_amount),
        'iden': session["user_id"]})
    db.commit()
    return redirect("/history")

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
    # see if the selected entry is in the database
    result = db.execute(text("SELECT * FROM auto_values WHERE id = :edit_id AND user_id = :iden"), 
        {'edit_id': edit_id, 'iden': iden}).fetchall()
    # invalid entry ID branch
    if len(result) == 0:
        return jsonify({"error":"1"})
    # all other fields are empty branch
    elif not edit_type and not edit_title and not edit_amount and not edit_frequency:
        return redirect("/")
    # "proper" input branch
    else:
        # place either the input from the form or the original values of each relevant column
        # in these variables and use them for updating the database
        my_type = db.execute(text("SELECT CASE WHEN :edit_type = '' THEN type ELSE :edit_type END FROM auto_values WHERE id = :edit_id AND user_id = :iden"),
        {'edit_type': edit_type, 'edit_id': edit_id, 'iden': iden}).fetchone()
        my_title = db.execute(text("SELECT CASE WHEN :edit_title = '' THEN title ELSE :edit_title END FROM auto_values WHERE id = :edit_id AND user_id = :iden"),
        {'edit_title': edit_title, 'edit_id': edit_id, 'iden': iden}).fetchone()
        '''
        Old-version: overly complicated SQL query
        For some reason I thought that I would need to write a branch for each possible
        combination of type, title, amount and frequency values if I did the
        checking with Python if-else statements, but that is not the case
        I got a tunnel-vision on solving this purely through SQL for some reason
        my_amount = engine.execute(text("SELECT CASE WHEN :edit_amount = '' THEN amount ELSE :edit_amount END FROM auto_values WHERE id = :edit_id AND user_id = :iden"),
        edit_amount = edit_amount, edit_id = edit_id, iden = iden).fetchone()
        '''
        if not edit_amount:
            my_amount = db.execute(text("SELECT amount FROM auto_values WHERE id = :edit_id AND user_id = :iden"),
                {'edit_id': edit_id, 'iden': iden}).fetchone()
        else:
            # styling the variable as a tuple to fit the UPDATE statement properly
            my_amount = (edit_amount,)
        my_frequency = db.execute(text("SELECT CASE WHEN :edit_frequency = '' THEN frequency ELSE :edit_frequency END FROM auto_values WHERE id = :edit_id AND user_id = :iden"),
        {'edit_frequency': edit_frequency, 'edit_id': edit_id, 'iden': iden}).fetchone()
        # either update auto_values with the new values or keep the old ones if there are no new values
        db.execute(text("UPDATE auto_values SET type = :my_type, title = :my_title, amount = :my_amount, frequency = :my_frequency "
                "WHERE id = :edit_id AND user_id = :iden"), {'edit_id': edit_id, 'my_type': my_type[0], 'my_title': my_title[0], 
                        'my_amount': float(my_amount[0]), 'my_frequency': my_frequency[0], 'iden': iden})
        db.commit()
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
    print(edit_hist_id)

    # invalid entry ID branch
    if len(db.execute(text("SELECT * FROM statement WHERE id = :edit_hist_id AND user_id = :iden"),
     {'edit_hist_id': edit_hist_id, 'iden': iden}).fetchall()) == 0:
        return jsonify({"error":"1"})
    # all other fields are empty branch
    elif not edit_hist_type and not edit_hist_title and not edit_hist_amount:
        return redirect("/history")
    # "proper" input branch
    else:
        # grab the old type of the selected entry and the user's cash from the users table
        old_type = db.execute(text("SELECT type FROM statement WHERE user_id = :iden AND id = :edit_hist_id")
        , {'iden': iden, 'edit_hist_id': edit_hist_id}).fetchone()[0]
        cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': session["user_id"]}).fetchone()
        # prepare variables for updating the statement table
        my_type = db.execute(text("SELECT CASE WHEN :edit_hist_type = '' THEN type ELSE :edit_hist_type END FROM statement WHERE id = :edit_hist_id AND user_id = :iden"),
        {'edit_hist_type': edit_hist_type, 'edit_hist_id': edit_hist_id, 'iden': iden}).fetchone()
        my_title = db.execute(text("SELECT CASE WHEN :edit_hist_title = '' THEN title ELSE :edit_hist_title END FROM statement WHERE id = :edit_hist_id AND user_id = :iden"),
        {'edit_hist_title': edit_hist_title, 'edit_hist_id': edit_hist_id, 'iden': iden}).fetchone()
        '''
        Old version
        my_amount = engine.execute(text("SELECT CASE WHEN :edit_hist_amount = '' THEN amount ELSE :edit_hist_amount END FROM statement WHERE id = :edit_hist_id AND user_id = :iden"),
        edit_hist_amount = edit_hist_amount, edit_hist_id = edit_hist_id, iden = iden).fetchone()
        '''
        if not edit_hist_amount:
            my_amount = db.execute(text("SELECT amount FROM statement WHERE id = :edit_hist_id AND user_id = :iden"),
             {'edit_hist_id': edit_hist_id, 'iden': iden}).fetchone()
        else:
            my_amount = (edit_hist_amount,)
        # grab the old amount of the selected entry
        amount = db.execute(text("SELECT amount FROM statement WHERE id = :edit_hist_id AND user_id = :iden"),
        {'edit_hist_id': edit_hist_id, 'iden': iden}).fetchone()
        #update the users cash according to the input
        # if the old and new types are both "income", subtract the old amount from the user's cash
        # and add the new amount to it
        if my_type[0] == "income" and old_type == "income":
            db.execute(text("UPDATE users SET cash = :cash - :amount + :my_amount WHERE id = :iden"),
            {'amount': amount[0], 'my_amount': float(my_amount[0]),
                        'iden': iden, 'cash': cash[0]})
        # if the old type is "expense" while the new one is "income" add both the old and
        # the new amount to the cash
        elif my_type[0] == "income" and old_type == "expense":
            db.execute(text("UPDATE users SET cash = :cash + :amount + :my_amount WHERE id = :iden"),
            {'amount': amount[0], 'my_amount': float(my_amount[0]),
                        'iden': iden, 'cash': cash[0]})
        # if both the old type and the new one are "income" add the old amount to the user's cash
        # and subtract the new one from it
        elif my_type[0] == "expense" and old_type == "expense":
            db.execute(text("UPDATE users SET cash = :cash + :amount - :my_amount WHERE id = :iden"),
            {'amount': amount[0], 'my_amount': float(my_amount[0]),
                        'iden': iden, 'cash': cash[0]})
        # if the old type is "income" and the new type is "expense" subtract both the old and
        # the new amounts from the user's cash
        else:
            db.execute(text("UPDATE users SET cash = :cash - :amount - :my_amount WHERE id = :iden"),
            {'amount': amount[0], 'my_amount': float(my_amount[0]),
                        'iden': iden, 'cash': cash[0]})

        db.execute(text("UPDATE statement SET type = :my_type, title = :my_title, amount = :my_amount "
                "WHERE id = :edit_hist_id AND user_id = :iden"), {'edit_hist_id': edit_hist_id,
                        'my_type': my_type[0], 'my_title': my_title[0], 'my_amount': float(my_amount[0]) , 'iden': iden})
        db.commit()
    return redirect("/history")

@app.route("/delete_auto", methods = ["POST"])
@login_required
def delete_auto():
    '''Delete recurring income and expense elements'''
    # get the entry ID and the user ID
    delete_id = request.form.get("delete_id")
    iden = session["user_id"]
    print(delete_id)

    check = request.form.get("check")

    # check if the selected entry is in the database
    result = db.execute(text("SELECT * FROM auto_values WHERE id = :delete_id AND user_id = :iden"),
     {'delete_id': delete_id, 'iden': iden}).fetchall()
    print(result)
    # invalid entry ID branch
    if len(result) == 0:
        return jsonify({"error": "1"})
    # valid input branch
    else:
        # delete appropriate row from the auto_values table
        db.execute(text("DELETE FROM auto_values WHERE id = :delete_id AND user_id = :iden"),
        {'delete_id': delete_id, 'iden': iden})
    db.commit()
    return redirect("/")

@app.route("/delete_all_auto", methods = ["POST"])
@login_required
def delete_all_auto():
    '''Delete all recurring entries'''
    check = request.form.get("delete_all_check")

    # if the "delete all recurring entries" checkbox is checked,
    # delete all recurring entries
    if check == "check":
        db.execute(text("DELETE FROM auto_values WHERE user_id = :iden"), {'iden': session["user_id"]})
        db.commit()
        return redirect("/")
    else:
        return redirect("/")


@app.route("/delete_hist", methods = ["GET", "POST"])
@login_required
def delete_hist():
    '''Delete income and expense elements from the financial history table'''
    # get the entry ID and the user ID
    delete_hist_id = request.form.get("delete_hist_id")
    iden = session["user_id"]
    

    # invalid entry ID branch
    if len(db.execute(text("SELECT * FROM statement WHERE id = :delete_hist_id AND user_id = :iden"),
    {'delete_hist_id': delete_hist_id, 'iden': iden}).fetchall()) == 0:
        return jsonify({"error": "1"})
    # valid input branch
    else:
        # grab the type and amount of the selected entry and the user's cash
        amount = db.execute(text("SELECT amount FROM statement WHERE id = :delete_hist_id AND user_id = :iden"),
        {'delete_hist_id': delete_hist_id, 'iden': iden}).fetchone()
        my_type = db.execute(text("SELECT type FROM statement WHERE id = :delete_hist_id AND user_id = :iden"),
        {'delete_hist_id': delete_hist_id, 'iden': iden}).fetchone()
        cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': iden}).fetchone()[0]
        # if entry's type is income subtract its amount from the user's cash
        if my_type[0] == "income":
            db.execute(text("UPDATE users SET cash = :cash - :amount WHERE id = :iden"),
            {'amount': amount[0], 'iden': iden, 'cash': cash})
        # if the entry's type is expense add its value to the user's cash
        else:
            db.execute(text("UPDATE users SET cash = :cash + :amount WHERE id = :iden"),
            {'amount': amount[0], 'iden': iden, 'cash': cash})
        db.execute(text("DELETE FROM statement WHERE id = :delete_hist_id AND user_id = :iden"),
        {'delete_hist_id': delete_hist_id, 'iden': iden})
        db.commit()
    return redirect("/history")

@app.route("/delete_all_hist", methods = ["POST"])
@login_required
def delete_all_hist():
    '''Delete all income and expense entries, reset starting balance to 10K USD,
        empty portfolio and transaction history tables'''
    iden = session["user_id"]
    check = request.form.get("delete_all_check2")
    # if the "delete all entries" checkbox is checked, delete all
    # entries from the statement, history and portfolio tables and reset
    # the starting balance of the account to 10000 USD
    if check == "check":
        db.execute(text("DELETE FROM statement WHERE user_id = :iden"), {'iden': iden})
        db.execute(text("DELETE FROM history WHERE user_id = :iden"), {'iden': iden})
        db.execute(text("DELETE FROM portfolio WHERE user_id = :iden"), {'iden': iden})
        db.execute(text("UPDATE users SET cash = 10000.00 WHERE id = :iden"), {'iden': iden})
        cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': iden}).fetchone()[0]
        db.execute(text("INSERT INTO statement (type, title, amount, user_id) "
                "VALUES ('balance', 'starting balance', :cash, :iden)"), {'cash': cash, 'iden': iden})
        db.commit()
        return redirect("/history")
    else:
        return redirect("/history")

@app.route("/edit_balance", methods = ["GET", "POST"])
@login_required
def edit_balance():
    '''Change the starting balance in the financial history table'''
    # get the new balance from the form
    edit_balance_amount = request.form.get("edit_balance_amount")

    # grab the user's cash an the old starting balance
    cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': session["user_id"]}).fetchone()
    old_balance = db.execute(text("SELECT amount FROM statement WHERE user_id = :iden AND title = 'starting balance'"),
    {'iden': session["user_id"]}).fetchone()
    # update the starting balance in the statement table
    db.execute(text("UPDATE statement SET amount = :amount WHERE user_id = :iden AND title = 'starting balance'"),
    {'amount': float(edit_balance_amount), 'iden': session["user_id"]})
    # subtract the old balance from the user's cash and add the new one to it
    db.execute(text("UPDATE users SET cash = :cash - :old_balance + :amount WHERE id = :iden"),
    {'amount': float(edit_balance_amount), 'old_balance': float(old_balance[0]),
        'iden': session["user_id"], 'cash': cash[0]})
    db.commit()
    # refresh page to showcase changes
    return redirect("/history")

@app.route("/stocks", methods = ["GET", "POST"])
@login_required
def stocks():
    """Show portfolio of stocks"""
    # prepare necessary variables
    stocks = db.execute(text("SELECT stock FROM portfolio WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': session["user_id"]}).fetchone()
    # set up and style shares, current price value and grand total
    shares = db.execute(text("SELECT shares FROM portfolio WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    i = len(stocks)
    current_price = []
    for j in range(i) :
        current_price.append(lookup(stocks[j]["stock"])["price"])
    value = []
    for k in range(i):
        value.append(shares[k]['shares'] * current_price[k])
    grand_total = cash[0]
    for m in range(i):
        grand_total += value[m]
    grand_total = usd(grand_total)
    for n in range(i):
        current_price[n] = usd(current_price[n])
        value[n] = usd(value[n])
    db.commit()
    # show the HTML table with these values to the user
    return render_template("stocks.html", i = i, stocks = stocks, current_price = current_price,
    value = value, cash = usd(cash[0]), grand_total = grand_total, shares = shares)



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
        cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': session["user_id"]}).fetchone()
        # check for valid input
        # return error codes as JSON objects so that JavaScript
        # can show appropriate messages to the user
        # invalid stock symbol (no stock found)
        if not stock:
            return jsonify({"error": "1"})
        # insufficient funds
        elif (int(shares) * stock["price"]) > cash[0]:
            return jsonify({"error": "2"})
        # valid input and sufficient funds
        else:
            owned_stocks = db.execute(text("SELECT stock FROM portfolio WHERE user_id = :iden AND stock = :stock")
            , {'iden': session["user_id"], 'stock': str(stock["symbol"])}).fetchall()
            # either create a new entry in the portfolio or update an existing one depending on
            # whether or not the user has shares in the stock chosen to be purchased
            if len(owned_stocks) == 0:
                db.execute(text("INSERT INTO portfolio(user_id, stock, current_price, shares) "
                                "VALUES(:user_id, :stock, :price, :shares)"),
                {'user_id': session["user_id"], 'stock': str(stock["symbol"]), 'price': stock["price"],
                                'shares': int(shares)})
            else:
                db.execute(text("UPDATE portfolio SET current_price = :price, shares = shares + :my_shares"
                                " WHERE user_id = :iden AND stock = :stock"), {'price': stock["price"], 'my_shares': int(shares),
                                                'iden': session["user_id"], 'stock': stock["symbol"]})
            # add the transaction to the statement table as an expense
            db.execute(text("INSERT INTO statement(type, title, amount, user_id) "
                        "VALUES ('expense', 'buying shares', :amount, :iden)"), {'iden': session["user_id"],
                                    'amount': (int(shares) * stock["price"])})

            # enter the transaction in history
            db.execute(text("INSERT INTO history(user_id, transaction_type, stock, price, shares)"
                        " VALUES(:user_id, 'buy', :stock, :price, :shares)"), {'user_id': session["user_id"], 'stock': str(stock["symbol"]),
                                     'price': stock["price"], 'shares': int(shares)})
            # decrease the user's cash with the transactions's worth in the database
            db.execute(text("UPDATE users SET cash = cash - :total WHERE id = :iden"), {'total': (int(shares) * stock["price"]),
                        'iden': session["user_id"]})
            # redirect user to the main page (redundant)
            db.commit()
            return redirect("/")


@app.route("/buy2", methods = ["GET", "POST"])
@login_required
def buy2():

    print(request.form.get("shares"), request.form.get("symbol"))
    return jsonify({"this_is": "a_json"})

@app.route("/history")
@login_required
def history():
    """Show history of transactions and finances"""
    # transactions
    transaction_type = db.execute(text("SELECT transaction_type FROM history WHERE user_id = :iden"),
    {'iden': session["user_id"]}).fetchall()
    stock = db.execute(text("SELECT stock FROM history WHERE user_id = :iden"),
    {'iden': session["user_id"]}).fetchall()
    price = db.execute(text("SELECT price FROM history WHERE user_id = :iden"),
    {'iden': session["user_id"]}).fetchall()
    shares = db.execute(text("SELECT shares FROM history WHERE user_id = :iden"),
    {'iden': session["user_id"]}).fetchall()
    time = db.execute(text("SELECT time FROM history WHERE user_id = :iden"),
    {'iden': session["user_id"]}).fetchall()
    i = len(time)
    # finances
    id_ = db.execute(text("SELECT id FROM statement WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    time2 = db.execute(text("SELECT time FROM statement WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    amount = db.execute(text("SELECT amount FROM statement WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    title = db.execute(text("SELECT title FROM statement WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    type_ = db.execute(text("SELECT type FROM statement WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    db.commit()
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

        # Query database for username
        rows = db.execute(text("SELECT * FROM users WHERE username = :username"),
                          {'username': request.form.get("username")}).fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return jsonify({"error": "1"})
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
        # prepare the variables to be used
        starting_balance = request.form.get("starting_balance")
        hashed = generate_password_hash(request.form.get("password"))
        username = request.form.get("username")
        # if the username is taken notify the user
        result = db.execute(text("SELECT * FROM users WHERE username = :username"),{'username': username}).fetchall()
        if len(result) != 0:
            return jsonify({"error": "1"})
        else:
            # add the user to the database
            db.execute(text("INSERT INTO users(username, hash) VALUES(:username, :hashed)"),
        {'username':  username, 'hashed': hashed})
            # once the registration process is complete, log the user in
            rows = db.execute(text("SELECT * FROM users WHERE username = :username"), {'username': username}).fetchall()
            session["user_id"] = rows[0]["id"]
            # if the user has entered a starting balance update their cash with the value
            if starting_balance:
                db.execute(text("UPDATE users SET cash = :starting_balance WHERE id = :iden"),
                {'starting_balance': float(starting_balance), 'iden': session["user_id"]})
            # grab the user's cash and present it as the starting balance in the statement table
            cash = db.execute(text("SELECT cash FROM users WHERE id = :iden"), {'iden': session["user_id"]}).fetchone()
            db.execute(text("INSERT INTO statement(type, title, amount, user_id) "
            "VALUES('balance', 'starting balance', :amount, :iden)"), {'amount': cash[0],
            'iden': session["user_id"]})
            db.commit()
        return redirect("/")

    # user reached the route via GET (through a redirect or a link)
    else:
        return render_template("register.html", usd = usd)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # prepary the variables used in sell.html
    stocks = db.execute(text("SELECT stock FROM portfolio WHERE user_id = :iden"), {'iden': session["user_id"]}).fetchall()
    i = len(stocks)
    # user reaches the route via the POST method (by filling out the HTML form)
    if request.method == "POST":
        # prepare the variables for the database operations
        my_symbol = str(request.form.get("symbol"))
        my_stock = db.execute(text("SELECT stock FROM portfolio WHERE user_id = :iden AND stock = :stock"),
        {'iden': session["user_id"], 'stock': my_symbol}).fetchone()
        my_shares = db.execute(text("SELECT shares FROM portfolio WHERE user_id = :iden AND stock = :stock"),
        {'iden': session["user_id"], 'stock': my_symbol}).fetchone()
        selling_shares = request.form.get("shares")
        # catch any errors in the input and return the appropriate error code
        # stock not in portfolio branch
        if not my_stock[0]:
            return jsonify({"error": "1"})
        # no shares owned branch
        elif my_shares[0] == 0:
            return jsonify({"error": "2"})
        # not enough shares owned branch
        elif my_shares[0] < int(selling_shares):
            return jsonify({"error": "3"})
        # the user's input is valid
        else:
            # enter the transaction into the statement table as an income entry
            my_price = lookup(my_symbol)["price"]
            db.execute(text("INSERT INTO statement(type, title, amount, user_id) "
                        "VALUES ('income', 'selling shares', :amount, :iden)"),
            {'amount': (my_price * int(selling_shares)), 'iden': session["user_id"]})
            # add the transaction to the history table, update the user's cash and portfolio
            db.execute(text("INSERT INTO history(user_id, transaction_type, stock, price, shares)"
                        " VALUES (:iden, 'sell', :stock, :price, :shares)"), {'iden': session["user_id"],
                                    'stock': my_symbol, 'price': my_price, 'shares': int(selling_shares)})
            db.execute(text("UPDATE portfolio SET shares = shares - :selling_shares "
                        "WHERE user_id = :iden AND stock = :stock"), 
            {'selling_shares': int(selling_shares), 'iden': session["user_id"], 'stock': my_symbol})
            db.execute(text("UPDATE users SET cash = cash + :total WHERE id = :iden")
            , {'total': (my_price * int(selling_shares)), 'iden': session["user_id"]})
        db.commit()
        # redirect the user to index.html
        return redirect("/")
    # user reached the route via the GET method
    else:
        # present the HTML form which sell.html contains to the user
        return render_template("sell.html", stocks = stocks, i = i)

@app.route("/change-pw", methods=["GET", "POST"])
@login_required
def change_pw():
    '''Change passwords '''
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
        # get the hashes for checking the password
        old_hash = generate_password_hash(old_password)
        real_old_hash = db.execute(text("SELECT hash FROM users WHERE id = :iden"), {'iden': session["user_id"]}).fetchone()


        # old pw wrong branch
        if not (check_password_hash(real_old_hash[0], old_password)):
            return jsonify({"error": "1"})
        # valid user input
        else:
            # update the users table in the database by placing the new_password's hash
            # into the hash column (for the user who's currently logged in)
            new_hash = generate_password_hash(new_password)
            db.execute(text("UPDATE users SET hash = :new_hash WHERE id = :iden"), {'new_hash': new_hash,
                        'iden': session["user_id"]})
        db.commit()
        # redirect the user to the main page
        return redirect("/")

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
