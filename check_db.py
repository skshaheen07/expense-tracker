import sqlite3

conn = sqlite3.connect("expense_tracker.db")
cursor = conn.cursor()

print("\n========== USERS TABLE ==========\n")

cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

if users:
    for user in users:
        print(user)
else:
    print("No users found.")

print("\n========== TRANSACTIONS TABLE ==========\n")

try:
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()

    if transactions:
        for transaction in transactions:
            print(transaction)
    else:
        print("No transactions found.")

except sqlite3.OperationalError:
    print("Transactions table does not exist yet.")

conn.close()