import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


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
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    stocks = db.execute("SELECT symbol, shares FROM purchases WHERE person_id = ?", session["user_id"])
    total_sum = []
    for stock in stocks:
        symbol = str(stock["symbol"])
        shares = int(stock["shares"])
        name = lookup(symbol)["name"]
        price = lookup(symbol)["price"]
        total = shares * price
        stock["name"] = name
        stock["price"] = usd(price)
        stock["total"] = usd(total)
        total_sum.append(float(total))

    user_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    cash_total = sum(total_sum) + user_balance
    return render_template("index.html", stocks=stocks, user_balance=usd(user_balance), cash_total=usd(cash_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    symbol = request.form.get("symbol")
    shares = request.form.get("shares")
    stock = lookup(symbol)

    if not request.form.get("symbol"):
        return apology("must provide a symbol", 400)
    if not request.form.get("shares"):
        return apology("must provide an amount", 400)
    elif not request.form.get("shares").isdigit() or int(request.form.get("shares")) < 1:
        return apology("invalid amount of shares", 400)
    if not stock:
        return apology("invalid stock symbol", 400)

    user_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    total = stock["price"] * float(shares)
    if float(user_balance[0]["cash"]) < total:
        return apology("not enough balance to purchase", 400)
    db.execute("INSERT INTO purchases (person_id, symbol, price, shares, time) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
    session["user_id"], symbol, stock["price"], shares)
    db.execute("INSERT INTO history (person_id, operation, symbol, shares, price, time) VALUES (?, 'BUY', ?, ?, ?, CURRENT_TIMESTAMP)",
    session["user_id"], symbol, shares, stock["price"])

    x = user_balance[0]["cash"] - total
    db.execute("UPDATE users SET cash = ? WHERE id = ?", float(x) ,session["user_id"])
    return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    stocks = db.execute("SELECT * FROM history WHERE person_id = ?", session["user_id"])

    for stock in stocks:
        symbol = str(stock["symbol"])
        shares = int(stock["shares"])
        operation = str(stock["operation"])
        price = float(stock["price"])
        time = stock["time"]

    return render_template("history.html", stocks=stocks, price=usd(price))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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
    if request.method == "GET":
        return render_template("quote.html")
    else:
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        stock = lookup(request.form.get("symbol"))

        if not stock:
            return apology("invalid stock symbol", 400)
        return render_template("quote.html", quoted=True, stock=stock, name=stock["name"], symbol=stock["symbol"], price=usd(stock["price"]))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must be the same", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", request.form.get("username"), generate_password_hash(request.form.get("password")))
            return redirect("/")
        return apology("username not available", 400)

    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        look = lookup(request.form.get("symbol"))
        shares = request.form.get("shares")
        symbol = request.form.get("symbol")
        user_shares = db.execute("SELECT shares FROM purchases WHERE person_id = ? AND symbol = ?", session["user_id"], request.form.get("symbol"))[0]["shares"]
        value = look["price"] * int(shares)
        user_balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        if not request.form.get("symbol") or not look:
            return apology("you must provide a stock", 400)
        elif not shares or int(user_shares) < int(shares):
            return apology("invalid share number", 400)
        else:
            db.execute("UPDATE users SET cash = ? WHERE id = ?", user_balance + value, session["user_id"])
            db.execute("INSERT INTO history (person_id, operation, symbol, shares, price, time) VALUES (?, 'SELL', ?, ?, ?, CURRENT_TIMESTAMP)",
            session["user_id"], symbol, shares, value)

            if int(user_shares) == int(shares):
                db.execute("DELETE FROM purchases WHERE person_id = ? AND symbol = ?", session["user_id"], symbol)
            if int(user_shares) > int(shares):
                db.execute("UPDATE purchases SET shares = ? WHERE person_id = ? AND symbol = ?", shares, session["user_id"], symbol)

        return redirect("/")
    else:
        symbols = db.execute("SELECT symbol FROM purchases WHERE person_id = ?", session["user_id"])
        return render_template("sell.html", symbols=symbols)

#Personal touch
#Allow users to change passwords
@app.route("/password", methods=["GET", "POST"])
@login_required
def change_pw():
    if request.method == "GET":
        return render_template("password.html")
    else:
        if not request.form.get("password"):
            return apology("must provide password", 403)
        password = generate_password_hash(request.form.get("password"))
        db.execute("UPDATE users SET hash = ? WHERE id = ?", password, session["user_id"])
        return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
