import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

# Creating App
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-env")

@app.route("/")
def index():
    return redirect("/login")

# Database Connection
database_uri = os.getenv("DATABASE_URL")
if not database_uri:
    raise RuntimeError(
        "DATABASE_URL is not set. Please copy .env.example to .env and configure your database connection."
    )

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Creating Table & Schema
class employee(db.Model):
    __tablename__ = "employee"
    id = db.Column(db.Integer, primary_key = True )
    emp_id = db.Column(db.String(100),unique = True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique = True)
    branch_id = db.Column(db.Integer)
    role = db.Column(db.String(100))
    password = db.Column(db.String(255))
    MPIN = db.Column(db.String(255))
    

# Register Page
@app.route("/register",methods = ["GET","POST"])
def register():
    if request.method == "POST":
        emp_id = request.form.get("emp_id")
        name = request.form.get("name")
        email = request.form.get("email")
        branch_id = request.form.get("branch_id")
        role = request.form.get("role")
        password = generate_password_hash(request.form.get("password"))
        MPIN = generate_password_hash(request.form.get("MPIN"))

        # Check duplicate email
        existing_email = employee.query.filter_by(email=email).first()
        if existing_email:
            return "Email already registered"

        # Check duplicate emp_id
        existing_emp = employee.query.filter_by(emp_id=emp_id).first()
        if existing_emp:
            return "Employee ID already exists"

        # New user Creating
        new_user = employee(
            emp_id=emp_id,
            name=name,
            email=email,
            branch_id=branch_id,
            role=role,
            password=password,
            MPIN=MPIN
        )

        # Adding user to DB
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return f"Error creating user: {str(e)}"

        return redirect("/home")
    return render_template("signup.html")

# Login Page
@app.route("/login", methods = ["GET","POST"])
def login():

    if request.method == "POST":

        # Getting Data From login.html page form
        emp_id = request.form.get("emp_id")
        MPIN = request.form.get("MPIN")

        # Checking User exist or not
        user = employee.query.filter_by(emp_id=emp_id).first()

        if user and user.MPIN and check_password_hash(user.MPIN, MPIN):
            session["user"] = user.emp_id
            return redirect("/home")
        else:
            return "Invalid Credentials"
    
    return render_template("login.html")

# Home page
@app.route("/home")
def home():
    if "user" in session:
        user = employee.query.filter_by(emp_id=session["user"]).first()
        from sqlalchemy import func

        total_txn_amount = db.session.query(
            func.coalesce(func.sum(transactions.amount), 0)
        ).scalar()

        total_bank_balance = db.session.query(
            func.coalesce(func.sum(account.balance), 0)
        ).scalar()

        total_employees = employee.query.count()
        active_emis = 0
        return render_template(
            "home.html",
            name=user.name,
            total_customers=customer.query.count(),
            total_accounts=account.query.count(),
            pending_loans=loan.query.filter_by(status="pending").count(),
            fraud_count=fraud_alert.query.count(),
            total_txn_amount=total_txn_amount,
            total_bank_balance=total_bank_balance,
            total_employees=total_employees,
            active_emis=active_emis
        )
    else:
        return redirect("/login")

# Logout option
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# All Tables
class customer(db.Model):
    __tablename__ = "customer"
    customer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    address = db.Column(db.String(150))
    accounts = db.relationship("account", backref="customer", lazy=True)
    loans = db.relationship("loan", backref="customer", lazy=True)


class account(db.Model):
    __tablename__ = "account"
    account_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.customer_id"))
    account_type = db.Column(db.String(20))
    balance = db.Column(db.Numeric(12,2), nullable=False, default=0.00)
    status = db.Column(db.String(20), default="active")
    transactions = db.relationship("transactions", backref="account", lazy=True)


class transactions(db.Model):
    __tablename__ = "transactions"
    transaction_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey("account.account_id"), nullable=True)
    type = db.Column(db.String(20))
    amount = db.Column(db.Numeric(12,2), nullable=False)
    status = db.Column(db.String(20))
    risk_score = db.Column(db.Integer, default=0)
    date = db.Column(db.DateTime, server_default=db.func.now())


class loan(db.Model):
    __tablename__ = "loan"
    loan_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.customer_id"))
    amount = db.Column(db.Numeric(12,2), nullable=False)
    interest_rate = db.Column(db.Numeric(5,2), nullable=False)
    duration = db.Column(db.Integer)
    status = db.Column(db.String(20))


class fraud_alert(db.Model):
    __tablename__ = "fraud_alert"
    fraud_id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.transaction_id"))
    risk_level = db.Column(db.String(20))
    reason = db.Column(db.String(255))


# Add Customers
@app.route("/add_customer", methods=["GET","POST"])
def add_customer():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")

        new_customer = customer(name=name, email=email, phone=phone, address=address)
        db.session.add(new_customer)
        db.session.commit()

        return redirect("/home")

    return render_template("add_customer.html")


# View Customers
@app.route("/view_customers")
def view_customers():
    if "user" not in session:
        return redirect("/login")
    from sqlalchemy.orm import joinedload
    customers = customer.query.options(
        joinedload(customer.accounts),
        joinedload(customer.loans)
    ).all()
    return render_template("view_customers.html", customers=customers)


# Create Account
@app.route("/create_account", methods=["GET","POST"])
def create_account():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        from decimal import Decimal

        customer_id = int(request.form.get("customer_id"))
        account_type = request.form.get("account_type")
        initial = Decimal(request.form.get("initial_deposit", "0") or "0")

        new_account = account(
            customer_id=customer_id,
            account_type=account_type,
            balance=initial
        )

        db.session.add(new_account)
        db.session.flush()

        if initial > 0:
            txn = transactions(
                account_id=new_account.account_id,
                type="deposit",
                amount=initial,
                status="success",
                risk_score=10
            )
            db.session.add(txn)

        db.session.commit()

        return redirect("/view_customers")

    return render_template("create_account.html")


# Transactions
@app.route("/transactions")
def transactions_view():
    if "user" not in session:
        return redirect("/login")
    data = db.session.query(transactions, customer.name)\
        .join(account, transactions.account_id == account.account_id)\
        .join(customer, account.customer_id == customer.customer_id)\
        .order_by(transactions.date.desc())\
        .all()
    return render_template("transactions.html", data=data)



# Fraud Detection
@app.route("/fraud")
def fraud():
    if "user" not in session:
        return redirect("/login")
    alerts = db.session.query(fraud_alert, customer.name)\
        .join(transactions, fraud_alert.transaction_id == transactions.transaction_id)\
        .join(account, transactions.account_id == account.account_id)\
        .join(customer, account.customer_id == customer.customer_id)\
        .all()
    return render_template("fraud.html", alerts=alerts)


# Cancel Transaction (Fraud Control)
@app.route("/cancel_transaction", methods=["POST"])
def cancel_transaction():
    if "user" not in session:
        return redirect("/login")

    txn_id = request.form.get("transaction_id")
    txn = transactions.query.get(txn_id)

    if not txn:
        return "Transaction not found"

    prev_status = txn.status
    # Mark transaction as cancelled
    txn.status = "cancelled"

    # Only reverse if transaction was already SUCCESS
    acc = account.query.get(txn.account_id)

    if acc and prev_status == "success":
        if txn.type == "deposit":
            acc.balance -= txn.amount
        elif txn.type == "withdraw":
            acc.balance += txn.amount
        elif txn.type == "transfer_out":
            acc.balance += txn.amount
        elif txn.type == "transfer_in":
            acc.balance -= txn.amount

    db.session.commit()

    return redirect("/fraud")


# Approve Transaction (Fraud Control)
@app.route("/approve_transaction", methods=["POST"])
def approve_transaction():
    if "user" not in session:
        return redirect("/login")

    txn_id = request.form.get("transaction_id")
    txn = transactions.query.get(txn_id)

    if not txn:
        return "Transaction not found"

    acc = account.query.get(txn.account_id)

    if not acc:
        return "Account not found"

    # Apply transaction now
    if txn.type == "deposit":
        acc.balance += txn.amount
    elif txn.type == "withdraw":
        acc.balance -= txn.amount
    elif txn.type == "transfer_out":
        acc.balance -= txn.amount
    elif txn.type == "transfer_in":
        acc.balance += txn.amount

    txn.status = "success"
    db.session.commit()

    return redirect("/fraud")



# Security
@app.route("/freeze/<int:id>")
def freeze_account(id):
    if "user" not in session:
        return redirect("/login")
    acc = account.query.get_or_404(id)
    acc.status = "frozen"
    db.session.commit()
    return redirect("/home")

# Unfreeze Account
@app.route("/unfreeze/<int:id>")
def unfreeze_account(id):
    if "user" not in session:
        return redirect("/login")
    acc = account.query.get_or_404(id)
    acc.status = "active"
    db.session.commit()
    return redirect("/accounts")

# Delete Account
@app.route("/delete_account", methods=["POST"])
def delete_account():
    if "user" not in session:
        return redirect("/login")

    account_id = request.form.get("account_id")
    reason = request.form.get("reason")

    acc = account.query.get(account_id)

    if not acc:
        return "Account not found"

    # Safety: prevent delete if balance exists
    if acc.balance > 0:
        return "Cannot delete account with balance"

    # 🔥 Detach transactions instead of deleting
    transactions.query.filter_by(account_id=account_id).update({"account_id": None})

    # 🔥 Delete related fraud alerts (optional safety)
    # (join not needed, simple approach)
    # You can skip if not required

    db.session.delete(acc)
    db.session.commit()

    print(f"Account {account_id} deleted due to: {reason}")

    return redirect("/home")

# Loan Control
@app.route("/loan")
def loan_view():
    if "user" not in session:
        return redirect("/login")
    loans = loan.query.all()
    return render_template("loan.html", loans=loans)

# Customer Loan Details
@app.route("/customer_loans/<int:id>")
def customer_loans(id):
    if "user" not in session:
        return redirect("/login")

    data = loan.query.filter_by(customer_id=id).all()
    return render_template("customer_loans.html", data=data)


# Report
@app.route("/reports")
def reports():
    if "user" not in session:
        return redirect("/login")
    total_customers = customer.query.count()
    total_accounts = account.query.count()
    return render_template("reports.html", c=total_customers, a=total_accounts)



# Employee Management
@app.route("/employees")
def employees():
    if "user" not in session:
        return redirect("/login")
    data = employee.query.all()
    return render_template("employees.html", data=data)

# View Accounts
@app.route("/accounts")
def accounts_view():
    if "user" not in session:
        return redirect("/login")
    data = account.query.all()
    return render_template("accounts.html", data=data)

# Account Details (balance + transactions)
@app.route("/account/<int:id>")
def account_details(id):
    if "user" not in session:
        return redirect("/login")

    acc = account.query.get_or_404(id)
    txns = transactions.query.filter_by(account_id=id).all()

    return render_template("account_details.html", acc=acc, txns=txns)

# Profile Page
@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect("/login")
    return render_template("profile.html")

# Make Transaction
@app.route("/make_transaction", methods=["GET","POST"])
def make_transaction():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        account_id_raw = request.form.get("account_id")
        amount_raw = request.form.get("amount")

        if not account_id_raw or not amount_raw:
            return "Missing data"

        account_id = int(account_id_raw)
        amount = float(amount_raw)
        t_type = request.form.get("type")  # deposit / withdraw

        if t_type not in ["deposit", "withdraw"]:
            return "Invalid transaction type"

        from decimal import Decimal

        acc = account.query.get(account_id)

        # ❌ Check account
        if not acc:
            return "Account not found"

        amt = Decimal(str(amount))

        if amt <= Decimal('0'):
            return "Transaction amount must be positive"

        # ❌ Withdraw check
        if t_type == "withdraw" and acc.balance < amt:
            return "Insufficient Balance"

        # ❌ Prevent ops on frozen account
        if acc.status == "frozen":
            return "Account is frozen"

        # 🔥 Risk Score Logic
        risk = 0
        if amount > 50000:
            risk = 80
        elif amount > 20000:
            risk = 50
        else:
            risk = 10

        if risk >= 70:
            # 🚨 HOLD transaction
            new_txn = transactions(
                account_id=account_id,
                type=t_type,
                amount=amt,
                status="pending",
                risk_score=risk
            )
            db.session.add(new_txn)
            db.session.commit()

            fraud = fraud_alert(
                transaction_id=new_txn.transaction_id,
                risk_level="high",
                reason="High amount transaction - pending approval"
            )
            db.session.add(fraud)
            db.session.commit()

            return redirect("/fraud")

        # ✅ Normal transaction (low risk)
        if t_type == "deposit":
            acc.balance = acc.balance + amt
        else:
            acc.balance = acc.balance - amt

        new_txn = transactions(
            account_id=account_id,
            type=t_type,
            amount=amt,
            status="success",
            risk_score=risk
        )

        db.session.add(new_txn)
        db.session.commit()

        return redirect("/transactions")

    return render_template("transaction_form.html")


# Transfer Money
@app.route("/transfer", methods=["GET","POST"])
def transfer():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        from_raw = request.form.get("from_account")
        to_raw = request.form.get("to_account")
        amount_raw = request.form.get("amount")

        if not from_raw or not to_raw or not amount_raw:
            return "Missing data"

        from_account = int(from_raw)
        to_account = int(to_raw)
        amount = float(amount_raw)

        from decimal import Decimal
        amt = Decimal(str(amount))

        if amt <= Decimal('0'):
            return "Transfer amount must be positive"

        acc1 = account.query.get(from_account)
        acc2 = account.query.get(to_account)

        if not acc1 or not acc2:
            return "Invalid account"

        if acc1.status == "frozen" or acc2.status == "frozen":
            return "One account is frozen"

        if acc1.balance < amt:
            return "Insufficient balance"

        # 🔥 Risk Score Logic
        risk = 0
        if amount > 50000:
            risk = 80
        elif amount > 20000:
            risk = 50
        else:
            risk = 10

        if risk >= 70:
            # 🚨 HOLD transfer
            txn1 = transactions(
                account_id=from_account,
                type="transfer_out",
                amount=amt,
                status="pending",
                risk_score=risk
            )

            txn2 = transactions(
                account_id=to_account,
                type="transfer_in",
                amount=amt,
                status="pending",
                risk_score=risk
            )

            db.session.add(txn1)
            db.session.add(txn2)
            db.session.commit()

            fraud = fraud_alert(
                transaction_id=txn1.transaction_id,
                risk_level="high",
                reason="High amount transfer - pending approval"
            )
            db.session.add(fraud)
            db.session.commit()

            return redirect("/fraud")

        # ✅ Normal transfer
        acc1.balance = acc1.balance - amt
        acc2.balance = acc2.balance + amt

        txn1 = transactions(
            account_id=from_account,
            type="transfer_out",
            amount=amt,
            status="success",
            risk_score=risk
        )

        txn2 = transactions(
            account_id=to_account,
            type="transfer_in",
            amount=amt,
            status="success",
            risk_score=risk
        )

        db.session.add(txn1)
        db.session.add(txn2)
        db.session.commit()

        return redirect("/transactions")

    return render_template("transfer.html")



# Auto create tables if not exist
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ["true", "1", "yes"]
    app.run(debug=debug_mode)
