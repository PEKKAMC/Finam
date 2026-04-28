import sqlite3
from datetime import date

DB_NAME = "user_data.db"


def init():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS savings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            objective_id INTEGER,
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (objective_id) REFERENCES objectives (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS objectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            reason TEXT,
            target_amount REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (name) VALUES (?)", ("Admin",))

    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users


def add_user(name):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def delete_user(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def add_saving_entry(username, amount, date_str, objective_id=None):
    """Adds a savings entry linked to an objective (or None for general)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_row = cursor.fetchone()

    if user_row:
        user_id = user_row[0]
        # Convert objective_id 0 (General) to None for DB
        obj_id_val = None if objective_id == 0 else objective_id

        cursor.execute('''
            INSERT INTO savings (user_id, objective_id, amount, date)
            VALUES (?, ?, ?, ?)
        ''', (user_id, obj_id_val, amount, date_str))
        conn.commit()
        success = True
    else:
        success = False

    conn.close()
    return success


def get_user_savings_entries(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_row = cursor.fetchone()

    entries = []
    if user_row:
        user_id = user_row[0]
        cursor.execute('''
            SELECT amount, date FROM savings 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,))
        entries = cursor.fetchall()

    conn.close()
    return entries


def get_total_savings(username):
    """Total savings across EVERYTHING."""
    entries = get_user_savings_entries(username)
    return sum(entry[0] for entry in entries)


def get_objective_progress(objective_id):
    """Calculates how much money has been specifically added to this objective."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM savings WHERE objective_id = ?", (objective_id,))
    res = cursor.fetchone()[0]
    conn.close()
    return res if res else 0.0


def add_objective(username, title, reason, target_amount):
    """Adds a savings objective/goal."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_row = cursor.fetchone()

    if user_row:
        user_id = user_row[0]
        created_at = date.today().strftime("%Y-%m-%d")
        cursor.execute('''
            INSERT INTO objectives (user_id, title, reason, target_amount, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, title, reason, target_amount, created_at))
        conn.commit()
        success = True
    else:
        success = False

    conn.close()
    return success


def get_user_objectives(username):
    """Retrieves all objectives: (id, title, reason, target_amount)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_row = cursor.fetchone()

    entries = []
    if user_row:
        user_id = user_row[0]
        cursor.execute('''
            SELECT id, title, reason, target_amount FROM objectives 
            WHERE user_id = ? 
        ''', (user_id,))
        entries = cursor.fetchall()

    conn.close()
    return entries


def get_total_target_amount(username):
    """Sum of all objective targets."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_row = cursor.fetchone()

    total_target = 0.0
    if user_row:
        user_id = user_row[0]
        cursor.execute('SELECT SUM(target_amount) FROM objectives WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()[0]
        total_target = result if result else 0.0

    conn.close()
    return total_target


def get_user_activity(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_row = cursor.fetchone()

    if not user_row:
        return []

    user_id = user_row[0]
    activities = []

    cursor.execute('''
        SELECT s.amount, s.date, o.title
        FROM savings s
        LEFT JOIN objectives o ON s.objective_id = o.id
        WHERE s.user_id = ?
    ''', (user_id,))

    for row in cursor.fetchall():
        amount, date_str, obj_title = row
        target_name = obj_title if obj_title else "General Savings"
        activities.append({
            "type": "saving",
            "date": date_str,
            "desc": f"Added {amount:,.0f} VND to '{target_name}'",
            "amount": amount
        })

    cursor.execute('SELECT title, created_at, target_amount FROM objectives WHERE user_id = ?', (user_id,))
    for row in cursor.fetchall():
        title, created_at, target = row
        activities.append({
            "type": "objective",
            "date": created_at,
            "desc": f"Created objective '{title}' (Target: {target:,.0f} VND)"
        })

    activities.sort(key=lambda x: x["date"], reverse=True)
    conn.close()
    return activities