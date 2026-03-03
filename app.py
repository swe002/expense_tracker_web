from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "expense_secret_key"

DB = "expense.db"


# ===============================
# DATABASE CONNECTION
# ===============================
def get_db():
    return sqlite3.connect(DB)


# ===============================
# CREATE TABLES (AUTO FIX ERRORS)
# ===============================
def create_tables():
    conn = get_db()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # EXPENSE TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        amount REAL,
        category TEXT,
        description TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


create_tables()


# ===============================
# LOGIN
# ===============================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (u, p)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = u
            return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")


# ===============================
# REGISTER
# ===============================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        u = request.form["username"]
        p = request.form["password"]

        conn = get_db()
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (u, p)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists"

        conn.close()
        return redirect("/")

    return render_template("register.html")


# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ======================
    # EXPENSE LIST
    # ======================
    cur.execute("""
        SELECT id,title,amount,category,description,date
        FROM expenses
        WHERE user_id=?
        ORDER BY id DESC
    """, (user_id,))
    expenses = cur.fetchall()

    # ======================
    # TOTAL EXPENSE
    # ======================
    cur.execute(
        "SELECT IFNULL(SUM(amount),0) FROM expenses WHERE user_id=?",
        (user_id,)
    )
    total = cur.fetchone()[0]

    # ======================
    # MONTHLY CHART DATA
    # ======================
    cur.execute("""
        SELECT substr(date,1,7) AS month,
               SUM(amount)
        FROM expenses
        WHERE user_id=?
        GROUP BY month
        ORDER BY month
    """, (user_id,))

    monthly_data = [
        {"month": row[0], "total": row[1]}
        for row in cur.fetchall()
    ]

    # ======================
    # CATEGORY CHART DATA ⭐ FIX
    # ======================
    cur.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id=?
        GROUP BY category
    """, (user_id,))

    category_data = [
        {"category": row[0], "total": row[1]}
        for row in cur.fetchall()
    ]

    conn.close()

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total=total,
        monthly_data=monthly_data,
        category_data=category_data   # ⭐ IMPORTANT LINE
    )
# ADD EXPENSE
# ===============================
@app.route("/add", methods=["POST"])
def add():

    if "user_id" not in session:
        return redirect("/")

    user_id = session["user_id"]

    title = request.form["title"]
    amount = request.form["amount"]
    category = request.form["category"]
    description = request.form.get("description", "")
    date = request.form["date"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO expenses
        (user_id,title,amount,category,description,date)
        VALUES(?,?,?,?,?,?)
    """, (user_id, title, amount, category, description, date))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ===============================
# DELETE EXPENSE
# ===============================
@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ===============================
# LOGOUT
# ===============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    app.run(debug=True)