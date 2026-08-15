import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import TableStyle
from reportlab.lib import colors
from openpyxl import Workbook
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    send_file
)
from datetime import datetime, date
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from config import Config
from models import db
from models.user import User
from models.transaction import Transaction
from models.budget import Budget
app = Flask(__name__)
load_dotenv()
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
app.config.from_object(Config)
db.init_app(app)
with app.app_context():
    db.create_all()
# ==========================================================
# HOME
# ==========================================================
@app.route("/")
def home():
    return render_template("index.html")
# ==========================================================
# REGISTER
# ==========================================================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        if password != confirm_password:
            flash(
                "Passwords do not match!",
                "danger"
            )
            return redirect(
                url_for("register")
            )
        existing_user = User.query.filter_by(
            email=email
        ).first()
        if existing_user:
            flash(
                "Email already exists!",
                "danger"
            )
            return redirect(
                url_for("register")
            )
        hashed_password = generate_password_hash(
            password
        )
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash(
            "Registration Successful! Please Login.",
            "success"
        )
        return redirect(
            url_for("login")
        )
    return render_template(
        "register.html"
    )
# ==========================================================
# LOGIN
# ==========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(
            email=email
        ).first()
        if user and check_password_hash(
            user.password,
            password
        ):
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash(
                "Login Successful!",
                "success"
            )
            return redirect(
                url_for("dashboard")
            )
        flash(
            "Invalid Email or Password!",
            "danger"
        )
        return redirect(
            url_for("login")
        )
    return render_template(
        "login.html"
    )
# ==========================================================
# DASHBOARD
# ==========================================================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    # ===========================
    # Income & Expense
    # ===========================
    incomes = Transaction.query.filter_by(
        user_id=user_id,
        type="Income"
    ).all()
    expenses = Transaction.query.filter_by(
        user_id=user_id,
        type="Expense"
    ).all()
    total_income = sum(t.amount for t in incomes)
    total_expense = sum(t.amount for t in expenses)
    balance = total_income - total_expense
    # ===========================
    # Current Month Budget
    # ===========================
    current_month = datetime.now().month
    current_year = datetime.now().year
    budget = Budget.query.filter_by(
        user_id=user_id,
        month=current_month,
        year=current_year
    ).first()
    if budget:
        monthly_budget = budget.monthly_budget
    else:
        monthly_budget = 0
    remaining_budget = monthly_budget - total_expense
    if monthly_budget > 0:
        budget_percentage = (
            total_expense / monthly_budget
        ) * 100
        if budget_percentage > 100:
            budget_percentage = 100
    else:
        budget_percentage = 0
    # ===========================
    # Savings
    # ===========================
    savings = balance
    # ===========================
    # Financial Health Percentage
    # ===========================
    if total_income > 0:
        savings_percentage = (savings / total_income) * 100
        if savings_percentage > 100:
            savings_percentage = 100
        if savings_percentage < 0:
            savings_percentage = 0
    else:
        savings_percentage = 0
    # ===========================
    # Alerts
    # ===========================
    budget_exceeded = False
    if monthly_budget > 0 and total_expense > monthly_budget:
        budget_exceeded = True
    low_balance = False
    if balance <= 1000:
        low_balance = True
    # ===========================
    # Expense Category Pie Chart
    # ===========================
    expense_categories = {}
    for expense in expenses:
        if expense.category in expense_categories:
            expense_categories[expense.category] += expense.amount
        else:
            expense_categories[expense.category] = expense.amount
    pie_labels = list(expense_categories.keys())
    pie_values = list(expense_categories.values())
    # ===========================
    # Monthly Analytics
    # ===========================
    monthly_income = [0] * 12
    monthly_expense = [0] * 12
    all_transactions = Transaction.query.filter_by(
        user_id=user_id
    ).all()
    for transaction in all_transactions:
        month = transaction.date.month - 1
        if transaction.type == "Income":
            monthly_income[month] += transaction.amount
        else:
            monthly_expense[month] += transaction.amount
    # ===========================
    # Recent Transactions
    # ===========================
    recent_transactions = (
        Transaction.query
        .filter_by(user_id=user_id)
        .order_by(Transaction.date.desc())
        .limit(5)
        .all()
    )
    # ===========================
    # Dashboard
    # ===========================
    # ===========================
    # Dynamic Greeting
    # ===========================
    current_hour = datetime.now().hour
    if current_hour < 12:
        greeting = "Good Morning ☀️"
    elif current_hour < 17:
        greeting = "Good Afternoon 🌤️"
    else:
        greeting = "Good Evening 🌙"
    return render_template(
        "dashboard.html",
        greeting=greeting,
        username=session["user_name"],
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        savings=savings,
        savings_percentage=savings_percentage,
        monthly_budget=monthly_budget,
        remaining_budget=remaining_budget,
        budget_percentage=budget_percentage,
        budget_exceeded=budget_exceeded,
        low_balance=low_balance,
        chart_income=total_income,
        chart_expense=total_expense,
        pie_labels=pie_labels,
        pie_values=pie_values,
        month_labels=[
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec"
        ],
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        recent_transactions=recent_transactions
    )
@app.route("/ai-chat")
def ai_chat():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("ai_chat.html")
# ==========================================================
# ADD INCOME
# ==========================================================
@app.route("/add-income", methods=["GET", "POST"])
def add_income():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        transaction = Transaction(
            user_id=session["user_id"],
            type="Income",
            title=request.form["title"],
            category=request.form["category"],
            amount=float(request.form["amount"]),
            date=datetime.now(),
            notes=request.form["notes"]
        )
        db.session.add(transaction)
        db.session.commit()
        flash("Income Added Successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_income.html")
# ==========================================================
# ADD EXPENSE
# ==========================================================
@app.route("/add-expense", methods=["GET", "POST"])
def add_expense():
    if "user_id" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        transaction = Transaction(
            user_id=session["user_id"],
            type="Expense",
            title=request.form["title"],
            category=request.form["category"],
            amount=float(request.form["amount"]),
            date=datetime.now(),
            notes=request.form["notes"]
        )
        db.session.add(transaction)
        db.session.commit()
        flash("Expense Added Successfully!", "success")
        return redirect(url_for("dashboard"))
    return render_template("add_expense.html")
# ==========================================================
# TRANSACTION HISTORY
# ==========================================================
@app.route("/transactions")
def transactions():
    if "user_id" not in session:
        return redirect(url_for("login"))
    query = Transaction.query.filter_by(
        user_id=session["user_id"]
    )
    # -----------------------------
    # Search by Title
    # -----------------------------
    search = request.args.get("search")
    if search:
        query = query.filter(
            Transaction.title.ilike(f"%{search}%")
        )
    # -----------------------------
    # Filter by Type
    # -----------------------------
    transaction_type = request.args.get("type")
    if transaction_type:
        query = query.filter(
            Transaction.type == transaction_type
        )
    # -----------------------------
    # Filter by Category
    # -----------------------------
    category = request.args.get("category")
    if category:
        query = query.filter(
            Transaction.category.ilike(f"%{category}%")
        )
    # -----------------------------
    # Filter by Date Range
    # -----------------------------
    from_date = request.args.get("from_date")
    if from_date:
        query = query.filter(
            Transaction.date >= datetime.strptime(
                from_date,
                "%Y-%m-%d"
            )
        )
    to_date = request.args.get("to_date")
    if to_date:
        query = query.filter(
            Transaction.date <= datetime.strptime(
                to_date,
                "%Y-%m-%d"
            )
        )
    # -----------------------------
    # Filter by Amount
    # -----------------------------
    min_amount = request.args.get("min_amount")
    if min_amount:
        query = query.filter(
            Transaction.amount >= float(min_amount)
        )
    max_amount = request.args.get("max_amount")
    if max_amount:
        query = query.filter(
            Transaction.amount <= float(max_amount)
        )
    # -----------------------------
    # Sorting
    # -----------------------------
    sort = request.args.get("sort")
    order = request.args.get("order", "desc")
    if sort == "amount":
        if order == "asc":
            query = query.order_by(Transaction.amount.asc())
        else:
            query = query.order_by(Transaction.amount.desc())
    else:
        if order == "asc":
            query = query.order_by(Transaction.date.asc())
        else:
            query = query.order_by(Transaction.date.desc())
    transactions = query.all()
    return render_template(
        "transactions.html",
        transactions=transactions
    )
# ==========================================================
# DELETE TRANSACTION
# ==========================================================
@app.route("/delete-transaction/<int:id>")
def delete_transaction(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    transaction = Transaction.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        flash(
            "Transaction Deleted Successfully!",
            "success"
        )
    else:
        flash(
            "Transaction Not Found!",
            "danger"
        )
    return redirect(url_for("transactions"))
# ==========================================================
# EDIT TRANSACTION
# ==========================================================
@app.route("/edit-transaction/<int:id>", methods=["GET", "POST"])
def edit_transaction(id):
    if "user_id" not in session:
        return redirect(url_for("login"))
    transaction = Transaction.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()
    if not transaction:
        flash(
            "Transaction Not Found!",
            "danger"
        )
        return redirect(url_for("transactions"))
    if request.method == "POST":
        transaction.title = request.form["title"]
        transaction.category = request.form["category"]
        transaction.amount = float(
            request.form["amount"]
        )
        transaction.notes = request.form["notes"]
        db.session.commit()
        flash(
            "Transaction Updated Successfully!",
            "success"
        )
        return redirect(
            url_for("transactions")
        )
    return render_template(
        "edit_transaction.html",
        transaction=transaction
    )
# ==========================================================
# DAILY REPORT
# ==========================================================
@app.route("/daily-report")
def daily_report():
    if "user_id" not in session:
        return redirect(url_for("login"))
    today = date.today()
    transactions = (
        Transaction.query
        .filter_by(user_id=session["user_id"])
        .all()
    )
    daily_transactions = []
    for transaction in transactions:
        if transaction.date == today:
            daily_transactions.append(transaction)
    total_income = sum(
        t.amount
        for t in daily_transactions
        if t.type == "Income"
    )
    total_expense = sum(
        t.amount
        for t in daily_transactions
        if t.type == "Expense"
    )
    balance = total_income - total_expense
    return render_template(
        "daily_report.html",
        transactions=daily_transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        today=today
    )
# ==========================================================
# MONTHLY REPORT
# ==========================================================
@app.route("/monthly-report")
def monthly_report():
    if "user_id" not in session:
        return redirect(url_for("login"))
    today = date.today()
    transactions = (
        Transaction.query
        .filter_by(user_id=session["user_id"])
        .all()
    )
    monthly_transactions = []
    for transaction in transactions:
        if (
            transaction.date.month == today.month and
            transaction.date.year == today.year
        ):
            monthly_transactions.append(transaction)
    total_income = sum(
        t.amount
        for t in monthly_transactions
        if t.type == "Income"
    )
    total_expense = sum(
        t.amount
        for t in monthly_transactions
        if t.type == "Expense"
    )
    balance = total_income - total_expense
    return render_template(
        "monthly_report.html",
        transactions=monthly_transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        today=today
    )
# ==========================================================
# SET MONTHLY BUDGET
# ==========================================================
@app.route("/set-budget", methods=["GET", "POST"])
def set_budget():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Current month and year
    month = datetime.now().month
    year = datetime.now().year

    # -----------------------------------------
    # SAVE / UPDATE BUDGET
    # -----------------------------------------
    if request.method == "POST":

        amount = float(request.form["amount"])

        budget = Budget.query.filter_by(
            user_id=user_id,
            month=month,
            year=year
        ).first()

        if budget:

            budget.monthly_budget = amount

        else:

            budget = Budget(
                user_id=user_id,
                monthly_budget=amount,
                month=month,
                year=year
            )

            db.session.add(budget)

        db.session.commit()

        flash(
            "Budget Saved Successfully!",
            "success"
        )

        return redirect(url_for("set_budget"))

    # -----------------------------------------
    # GET CURRENT BUDGET
    # -----------------------------------------

    budget = Budget.query.filter_by(
        user_id=user_id,
        month=month,
        year=year
    ).first()

    # If no budget exists
    if budget:

        budget_amount = float(
            budget.monthly_budget or 0
        )

    else:

        budget_amount = 0.0

    # -----------------------------------------
    # GET CURRENT MONTH EXPENSES
    # -----------------------------------------

    transactions = Transaction.query.filter_by(
        user_id=user_id
    ).all()

    current_month_expenses = []

    for transaction in transactions:

        if transaction.type == "Expense":

            transaction_date = transaction.date

            if transaction_date:

                if (
                    transaction_date.month == month
                    and transaction_date.year == year
                ):

                    current_month_expenses.append(
                        transaction
                    )

    # -----------------------------------------
    # TOTAL SPENT
    # -----------------------------------------

    spent_amount = sum(
        float(transaction.amount or 0)
        for transaction in current_month_expenses
    )

    # -----------------------------------------
    # REMAINING
    # -----------------------------------------

    remaining_amount = (
        budget_amount - spent_amount
    )

    # Don't show negative remaining
    # as a confusing positive value
    if remaining_amount < 0:

        remaining_amount = 0.0

    # -----------------------------------------
    # BUDGET PERCENTAGE
    # -----------------------------------------

    if budget_amount > 0:

        budget_percentage = (
            spent_amount / budget_amount
        ) * 100

    else:

        budget_percentage = 0.0

    # -----------------------------------------
    # CATEGORY SPENDING
    # -----------------------------------------

    food_spent = 0.0
    transport_spent = 0.0
    shopping_spent = 0.0

    for transaction in current_month_expenses:

        category = (
            transaction.category or ""
        ).strip().lower()

        amount = float(
            transaction.amount or 0
        )

        # Food
        if category in [
            "food",
            "food & dining",
            "food and dining",
            "groceries",
            "restaurant"
        ]:

            food_spent += amount

        # Transport
        elif category in [
            "transport",
            "transportation",
            "travel",
            "fuel"
        ]:

            transport_spent += amount

        # Shopping
        elif category in [
            "shopping",
            "online shopping",
            "personal shopping"
        ]:

            shopping_spent += amount

    # -----------------------------------------
    # CATEGORY BUDGET PERCENTAGES
    #
    # These are percentages of the overall
    # monthly budget.
    # -----------------------------------------

    if budget_amount > 0:

        food_percentage = (
            food_spent / budget_amount
        ) * 100

        transport_percentage = (
            transport_spent / budget_amount
        ) * 100

        shopping_percentage = (
            shopping_spent / budget_amount
        ) * 100

    else:

        food_percentage = 0.0
        transport_percentage = 0.0
        shopping_percentage = 0.0

    # -----------------------------------------
    # SEND EVERYTHING TO TEMPLATE
    # -----------------------------------------

    return render_template(
        "set_budget.html",

        budget_amount=budget_amount,

        spent_amount=spent_amount,

        remaining_amount=remaining_amount,

        budget_percentage=budget_percentage,

        food_spent=food_spent,

        food_percentage=food_percentage,

        transport_spent=transport_spent,

        transport_percentage=transport_percentage,

        shopping_spent=shopping_spent,

        shopping_percentage=shopping_percentage
    )
# ==========================================================
# EXPORT PDF
# ==========================================================
@app.route("/export-pdf")
def export_pdf():
    if "user_id" not in session:
        return redirect(url_for("login"))
    transactions = (
        Transaction.query
        .filter_by(user_id=session["user_id"])
        .order_by(Transaction.date.desc())
        .all()
    )
    os.makedirs("exports", exist_ok=True)
    pdf_path = os.path.join(
        "exports",
        "transactions.pdf"
    )
    document = SimpleDocTemplate(pdf_path)
    data = [[
        "ID",
        "Type",
        "Title",
        "Category",
        "Amount",
        "Date"
    ]]
    for transaction in transactions:
        data.append([
            transaction.id,
            transaction.type,
            transaction.title,
            transaction.category,
            f"₹{transaction.amount:.2f}",
            transaction.date.strftime("%d-%m-%Y")
        ])
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ]))
    document.build([table])
    return send_file(
        pdf_path,
        as_attachment=True
    )
# ==========================================================
# EXPORT EXCEL
# ==========================================================
@app.route("/export-excel")
def export_excel():
    if "user_id" not in session:
        return redirect(url_for("login"))
    transactions = (
        Transaction.query
        .filter_by(user_id=session["user_id"])
        .order_by(Transaction.date.desc())
        .all()
    )
    os.makedirs("exports", exist_ok=True)
    excel_path = os.path.join(
        "exports",
        "transactions.xlsx"
    )
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Transactions"
    sheet.append([
        "ID",
        "Type",
        "Title",
        "Category",
        "Amount",
        "Date",
        "Notes"
    ])
    for transaction in transactions:
        sheet.append([
            transaction.id,
            transaction.type,
            transaction.title,
            transaction.category,
            transaction.amount,
            transaction.date.strftime("%d-%m-%Y"),
            transaction.notes
        ])
    workbook.save(excel_path)
    return send_file(
        excel_path,
        as_attachment=True
    )
# ==========================================================
# PROFILE
# ==========================================================
@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    return render_template(
        "profile.html",
        user=user
    )
# ==========================================================
# EDIT PROFILE
# ==========================================================
@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        user.name = request.form["name"]
        user.email = request.form["email"]
        db.session.commit()
        session["user_name"] = user.name
        flash(
            "Profile Updated Successfully!",
            "success"
        )
        return redirect(url_for("profile"))
    return render_template(
        "edit_profile.html",
        user=user
    )
@app.route("/change-password", methods=["GET", "POST"])
def change_password():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user = User.query.get(session["user_id"])
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        if not check_password_hash(user.password, current_password):
            flash("Current password is incorrect!", "danger")
            return redirect(url_for("change_password"))
        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("change_password"))
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash("Password changed successfully!", "success")
        return redirect(url_for("profile"))
    return render_template("change_password.html")
# ==========================================================
# ASK AI
# ==========================================================
# ==========================================================
# AI CHAT API
# ==========================================================
@app.route("/ask-ai", methods=["POST"])
def ask_ai():
    if "user_id" not in session:
        return {
            "answer": "Please login first."
        }
    question = request.json.get("question")
    transactions = Transaction.query.filter_by(
        user_id=session["user_id"]
    ).all()
    if not transactions:
        return {
            "answer": "You don't have any transactions yet. Add some income or expenses first."
        }
    # ==================================================
    # Financial Summary
    # ==================================================
    total_income = sum(
        t.amount
        for t in transactions
        if t.type == "Income"
    )
    total_expense = sum(
        t.amount
        for t in transactions
        if t.type == "Expense"
    )
    savings = total_income - total_expense
    if total_income > 0:
        savings_rate = (savings / total_income) * 100
    else:
        savings_rate = 0
    # ==================================================
    # Expense Categories
    # ==================================================
    categories = {}
    for t in transactions:
        if t.type == "Expense":
            if t.category in categories:
                categories[t.category] += t.amount
            else:
                categories[t.category] = t.amount
    # ==================================================
    # Transaction Data for Gemini
    # ==================================================
    transaction_data = ""
    for t in transactions:
        transaction_data += (
            f"Type: {t.type}, "
            f"Title: {t.title}, "
            f"Category: {t.category}, "
            f"Amount: ₹{t.amount}, "
            f"Date: {t.date}\n"
        )
    # ==================================================
    # Gemini Prompt
    # ==================================================
    prompt = f"""
You are an AI Financial Advisor.
Here is the user's financial summary.
Total Income: ₹{total_income}
Total Expense: ₹{total_expense}
Current Savings: ₹{savings}
Savings Rate: {savings_rate:.1f}%
Expense Categories:
{categories}
User Question:
{question}
Instructions:
- Do NOT calculate totals.
- The totals are already provided.
- Only analyze the financial situation.
- Give exactly 4 recommendations.
- Use simple English.
- Do NOT use Markdown.
- Do NOT use *, #, ###, or ---.
- Put each recommendation on a new line.
- Keep the response under 120 words.
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=500
        )
        answer = response.choices[0].message.content
        print(answer)
        print({
            "income": total_income,
            "expense": total_expense,
            "savings": savings,
            "rate": round(savings_rate, 1),
            "categories": categories,
            "recommendation": answer
        })
        return {
            "income": total_income,
            "expense": total_expense,
            "savings": savings,
            "rate": round(savings_rate, 1),
            "categories": categories,
            "recommendation": answer
        }
    except Exception as e:
        print(e)
        return {
            "answer": f"Groq Error: {str(e)}"
        }
# ==========================================================
# FINANCIAL ANALYTICS
# ==========================================================
@app.route("/analytics")
def analytics():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get selected month and year
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    # If nothing selected, use current month/year
    if not month:
        month = datetime.now().month

    if not year:
        year = datetime.now().year

    # Get transactions for selected month/year
    transactions = Transaction.query.filter(
        Transaction.user_id == session["user_id"],
        db.extract("month", Transaction.date) == month,
        db.extract("year", Transaction.date) == year
    ).all()

    total_income = sum(
        t.amount for t in transactions
        if t.type == "Income"
    )

    total_expense = sum(
        t.amount for t in transactions
        if t.type == "Expense"
    )

    savings = total_income - total_expense

    if total_income > 0:
        savings_rate = (savings / total_income) * 100
    else:
        savings_rate = 0

    return render_template(
        "analytics.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        savings_rate=savings_rate,
        selected_month=month,
        selected_year=year
    )
# ==========================================================
# AI ASSISTANT PAGE
# ==========================================================
@app.route("/assistant")
def assistant():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("assistant.html")
# ==========================================================
# REPORTS PAGE
# ==========================================================
@app.route("/reports")
def reports():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("reports.html")
# ==========================================================
# SETTINGS PAGE
# ==========================================================
@app.route("/settings")
def settings():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("settings.html")
# ==========================================================
# LOGOUT
# ==========================================================
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged Out Successfully!", "success")
    return redirect(url_for("login"))
# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    app.run(debug=True)
