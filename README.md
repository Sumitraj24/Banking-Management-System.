# 🏦 Banking Management System

A full-stack banking management system built with Python, Flask, SQLAlchemy, and MySQL.

---

## 🌟 Features

- **Employee Authentication**: Secure registration and login with hashed MPINs and passwords.
- **Customer Management**: Add and view customer profiles with linked accounts and loans.
- **Account Operations**: Create accounts, view live balances, and track transactions.
- **Transfers & Transactions**: Deposit, withdraw, and perform peer-to-peer bank transfers.
- **Fraud Detection & Controls**: Automatic risk-scoring logic that flags high-value transactions for manager review, with transaction approval/cancellation workflows and account freeze/unfreeze controls.
- **Reports & Analytics**: Real-time overview of total bank balances, active accounts, customers, and pending loans.

---

## 🚀 Setup & Installation

### 1. Prerequisites
- Python 3.10+
- MySQL Server 8.0+

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/banking-system.git
cd banking-system
```

### 3. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your MySQL credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/banking_system
SECRET_KEY=your_secure_random_key_here
FLASK_DEBUG=True
```

### 6. Create MySQL Database
Make sure MySQL is running, then create the database:
```sql
CREATE DATABASE banking_system;
```

### 7. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 📂 Project Structure

```
├── app.py                  # Main Flask application & routes
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python package dependencies
├── templates/              # HTML Jinja2 templates
│   ├── login.html
│   ├── signup.html
│   ├── home.html
│   ├── accounts.html
│   ├── account_details.html
│   ├── add_customer.html
│   ├── view_customers.html
│   ├── create_account.html
│   ├── transactions.html
│   ├── transaction_form.html
│   ├── transfer.html
│   ├── fraud.html
│   ├── loan.html
│   ├── customer_loans.html
│   ├── employees.html
│   ├── reports.html
│   └── profile.html
└── static/                 # Static assets (CSS)
    └── style.css
```
