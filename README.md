\# 💰 Expense Tracker



A full-stack personal finance management web application built with \*\*Flask, Python, SQLAlchemy, HTML, CSS, Bootstrap, and JavaScript\*\*.



The application helps users track income and expenses, monitor their financial health, analyze spending patterns, generate reports, and interact with an AI-powered financial assistant.



\---



\## 🚀 Features



\### 🔐 User Authentication

\- User registration

\- Secure login/logout

\- Password hashing

\- Change password

\- Profile management



\### 💰 Income \& Expense Management

\- Add income

\- Add expenses

\- Categorize transactions

\- Add transaction notes

\- Edit transactions

\- Delete transactions

\- View transaction history



\### 📊 Dashboard

\- Current financial overview

\- Total income

\- Total expenses

\- Current balance

\- Savings

\- Financial health indicator

\- Current-month financial analytics

\- Income vs Expense chart

\- Expense category chart

\- Monthly income/expense trend



\### 📈 Financial Analytics

\- Select a specific month and year

\- Analyze income vs expenses

\- Calculate savings rate

\- View financial performance for the selected period



\### 📄 Financial Reports

\- Daily financial report

\- Monthly financial report

\- Daily summary

\- Monthly summary

\- Transaction history

\- PDF/Excel export support



\### 🤖 AI Financial Assistant

\- AI-powered financial assistance

\- Expense analysis

\- Savings recommendations

\- Spending insights

\- Financial suggestions

\- Interactive AI chat



\### 🎯 Budget Management

\- Set monthly budget

\- Track budget usage

\- Monitor remaining budget

\- Budget warning indicators

\- Budget exceeded notifications



\### ⚙️ Settings

\- Profile settings

\- Password management

\- Application preferences



\---



\## 🛠️ Tech Stack



\### Backend

\- Python

\- Flask

\- SQLAlchemy

\- SQLite



\### Frontend

\- HTML5

\- CSS3

\- Bootstrap 5

\- JavaScript

\- Chart.js

\- Font Awesome



\### AI

\- Generative AI API

\- AI-powered financial assistant



\### Development Tools

\- Git

\- GitHub

\- VS Code

\- Python Virtual Environment



\---



\## 📁 Project Structure



```text

Expense-tracker/

│

├── app.py

├── config.py

├── check\_db.py

├── requirements.txt

├── .gitignore

├── README.md

│

├── models/

│   ├── \_\_init\_\_.py

│   ├── user.py

│   ├── transaction.py

│   └── budget.py

│

├── templates/

│   ├── dashboard.html

│   ├── login.html

│   ├── register.html

│   ├── add\_income.html

│   ├── add\_expense.html

│   ├── transactions.html

│   ├── analytics.html

│   ├── ai\_chat.html

│   ├── monthly\_report.html

│   ├── daily\_report.html

│   ├── profile.html

│   ├── settings.html

│   └── includes/

│       └── sidebar.html

│

├── static/

│   ├── css/

│   │   ├── style.css

│   │   ├── sidebar.css

│   │   ├── auth.css

│   │   └── landing.css

│   │

│   └── images/

│       └── hero.png

│

└── exports/

&#x20;   └── Generated reports

