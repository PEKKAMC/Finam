import sqlite3

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
            amount REAL NOT NULL,
            date TEXT NOT NULL,
            note TEXT,
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

def add_saving_entry(username, amount, date_str, note):
    """Adds a savings entry for a specific user."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Find user ID from username
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_id = cursor.fetchone()

    if user_id:
        user_id = user_id[0]
        cursor.execute('''
            INSERT INTO savings (user_id, amount, date, note)
            VALUES (?, ?, ?, ?)
        ''', (user_id, amount, date_str, note))
        conn.commit()
        success = True
    else:
        # User not found
        success = False

    conn.close()
    return success

def get_user_savings_entries(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Find user ID from username
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user_id = cursor.fetchone()

    entries = []
    if user_id:
        user_id = user_id[0]
        cursor.execute('''
            SELECT amount, date, note FROM savings 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,))
        entries = cursor.fetchall()

    conn.close()
    return entries

def get_total_savings(username):
    entries = get_user_savings_entries(username)
    return sum(entry[0] for entry in entries)