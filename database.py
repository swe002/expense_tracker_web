import sqlite3

DB_NAME = "expense.db"


# ------------------------------
# CONNECT DATABASE
# ------------------------------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ------------------------------
# CREATE TABLES + AUTO UPDATE
# ------------------------------
def init_db():
    conn = get_connection()
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
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )
    """)

    # -------- AUTO ADD NEW COLUMN (VERY IMPORTANT) --------
    cur.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cur.fetchall()]

    if "budget" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN budget REAL DEFAULT 0")

    conn.commit()
    conn.close()