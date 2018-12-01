import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final_project.db")

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


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


def usd(value):
    """Format value as USD."""
    return "${0:.2f}".format(value)

def daily():
    '''Add entries to the statement table every day'''
    # grab all daily recurring values
    daily_rows = db.execute("SELECT * FROM auto_values "
    "WHERE user_id = :iden AND frequency = 'daily'", iden = session["user_id]"])
    j = len(daily_rows)
    # grab the user's cash
    cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])[0]["cash"]
    # iterate through each entry
    for i in range(j):
        # if the entry's type is income add its amount to the user's cash
        if daily_rows[i]["type"] == "income":
            db.execute("UPDATE users SET cash = :cash + :amount WHERE id = :iden", cash = cash,
             iden = session["user_id"], amount = daily_rows[i]["amount"])
        # if the entry's type is expense subtract its amount from the user's cash
        else:
            db.execute("UPDATE users SET cash = :cash - :amount WHERE id = :iden", cash = cash,
             iden = session["user_id"], amount = daily_rows[i]["amount"])
        # add the entry to the statement table
        db.execute("INSERT INTO statement(type, title, amount, user_id) "
        "VALUES(:my_type, :title, :amount, :user_id", my_type = daily_rows[i]["type"],
        title = daily_rows[i]["title"], amount = daily_rows[i]["amount"],
        user_id = daily_rows[i]["user_id"])

def weekly():
    '''Add entries to the statement table every week'''
    # grab all weekly recurring entries from the auto_values table
    weekly_rows = db.execute("SELECT * FROM auto_values "
    "WHERE user_id = :iden AND frequency = 'weekly'", iden = session["user_id]"])
    j = len(weekly_rows)
    # grab the user's cash
    cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])[0]["cash"]
    # iterate through each entry
    for i in range(j):

        # if the entry's type is income add its amount to the user's cash
        if weekly_rows[i]["type"] == "income":
            db.execute("UPDATE users SET cash = :cash + :amount WHERE id = :iden", cash = cash,
             iden = session["user_id"], amount = weekly_rows[i]["amount"])
        # if the entry's type is expense subtract its amount from the user's cash
        else:
            db.execute("UPDATE users SET cash = :cash - :amount WHERE id = :iden", cash = cash,
             iden = session["user_id"], amount = weekly_rows[i]["amount"])
        # add the entry to the statement table
        db.execute("INSERT INTO statement(type, title, amount, user_id) "
        "VALUES(:my_type, :title, :amount, :user_id", my_type = weekly_rows[i]["type"],
        title = weekly_rows[i]["title"], amount = weekly_rows[i]["amount"],
        user_id = weekly_rows[i]["user_id"])

def monthly():
    '''Add entries to the statement table every month'''
    # grab all monthly recurring entries from the auto_values table
    monthly_rows = db.execute("SELECT * FROM auto_values "
    "WHERE user_id = :iden AND frequency = 'monthly'", iden = session["user_id]"])
    j = len(monthly_rows)
    # grab the user's cash
    cash = db.execute("SELECT cash FROM users WHERE id = :iden", iden = session["user_id"])[0]["cash"]
    # iterate through each entry
    for i in range(j):
        # if the entry's type is income add its amount to the user's cash
        if monthly_rows[i]["type"] == "income":
            db.execute("UPDATE users SET cash = :cash + :amount WHERE id = :iden", cash = cash,
             iden = session["user_id"], amount = monthly_rows[i]["amount"])
        # if the entry's type is expense subtract its amount from the user's cash
        else:
            db.execute("UPDATE users SET cash = :cash - :amount WHERE id = :iden", cash = cash,
             iden = session["user_id"], amount = monthly_rows[i]["amount"])
        # add the entry to the statement table
        db.execute("INSERT INTO statement(type, title, amount, user_id) "
        "VALUES(:my_type, :title, :amount, :user_id", my_type = monthly_rows[i]["type"],
        title = monthly_rows[i]["title"], amount = monthly_rows[i]["amount"],
        user_id = monthly_rows[i]["user_id"])