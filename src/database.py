# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

from datetime import datetime
import sqlite3
from typing import List, Dict, Any, Optional

from src.logger import Logger
from src.utils import DefaultSettings

# ==========================================
# DATABASE CONNECTION
# ==========================================

class DatabaseConnection:
    """Handles the raw SQLite connection and table initialization."""

    def __init__(self, database_name: str):
        self.database_name = database_name

    def execute(self, query: str, parameters: tuple = (), fetch_all: bool = False, fetch_one: bool = False) -> Any:
        with sqlite3.connect(self.database_name) as connection:
            connection.execute("PRAGMA foreign_keys = ON;")
            cursor = connection.cursor()
            cursor.execute(query, parameters)

            if fetch_all:
                return cursor.fetchall()
            if fetch_one:
                return cursor.fetchone()

            connection.commit()
            return cursor.lastrowid

    def initialize_database(self) -> None:
        Logger.debug("Initializing database tables...")
        try:
            self.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            ''')
            self.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    history_cleared_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                 )
            ''')
            self.execute('''
                CREATE TABLE IF NOT EXISTS objectives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    reason TEXT,
                    target_amount INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    deleted_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            self.execute('''
                CREATE TABLE IF NOT EXISTS savings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    objective_id INTEGER,
                    amount INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT,
                    deleted_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (objective_id) REFERENCES objectives (id)
                )
            ''')
            self.execute('''
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    note TEXT NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            self.execute('''
                CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                category TEXT NOT NULL,
                note TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            count = self.execute(
                "SELECT COUNT(*) FROM users",
                fetch_one=True
            )[0]
            if count == 0:
                self.execute(
                    "INSERT INTO users (name) VALUES (?)",
                    (DefaultSettings.DEFAULT_USERNAME,)
                )

            Logger.info("Database initialized successfully.")
        except Exception as error:
            Logger.error(f"Failed to initialize database: {error}")

# ==========================================
# USER & SETTINGS LOGIC
# ==========================================

class UserDatabase:
    """Handles all logic related to user accounts and settings."""

    def __init__(self, connection: DatabaseConnection):
        self.db = connection

    def get_all_users(self) -> List[str]:
        rows = self.db.execute(
            "SELECT name FROM users",
            fetch_all=True
        )
        return [row[0] for row in rows]

    def add_user(self, username: str) -> bool:
        try:
            self.db.execute(
                "INSERT INTO users (name) VALUES (?)",
                (username,)
            )
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_user(self, username: str) -> None:
        self.db.execute(
            "DELETE FROM users WHERE name = ?",
            (username,)
        )

    def get_user_id(self, username: str) -> Optional[int]:
        result = self.db.execute(
            "SELECT id FROM users WHERE name = ?",
            (username,),
            fetch_one=True
        )
        return result[0] if result else None

    def clear_activity_history(self, username: str) -> None:
        user_id = self.get_user_id(username)
        if not user_id: return

        cleared_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        exists = self.db.execute(
            "SELECT user_id FROM user_settings WHERE user_id = ?",
            (user_id,),
            fetch_one=True
        )

        if exists:
            self.db.execute(
                "UPDATE user_settings SET history_cleared_at = ? WHERE user_id = ?",
                (cleared_date, user_id)
            )
        else:
            self.db.execute(
                "INSERT INTO user_settings (user_id, history_cleared_at) VALUES (?, ?)",
                (user_id, cleared_date)
            )

# ==========================================
# SAVING PAGE LOGIC
# ==========================================

class SavingDatabase:
    """Handles all logic related to the Saving page (objectives and objective deposits)."""

    def __init__(self, connection: DatabaseConnection, user_db: UserDatabase):
        self.db = connection
        self.user_db = user_db

    def add_saving_entry(self, username: str, amount: int, date: str, objective_id: int, note: str = "") -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        objective_id_value = None if objective_id == 0 else objective_id
        self.db.execute(
            "INSERT INTO savings (user_id, objective_id, amount, date, note) VALUES (?, ?, ?, ?, ?)",
            (user_id, objective_id_value, amount, date, note)
        )
        return True

    def get_total_savings(self, username: str) -> int:
        result = self.db.execute(
            "SELECT SUM(amount) FROM savings s JOIN users u ON s.user_id = u.id WHERE u.name = ? AND s.deleted_at IS NULL",
            (username,), fetch_one=True
        )
        return result[0] if result and result[0] else 0

    def add_objective(self, username: str, title: str, reason: str, target_amount: int) -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db.execute(
            "INSERT INTO objectives (user_id, title, reason, target_amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, reason, target_amount, created_at)
        )
        return True

    def delete_objective(self, objective_id: int) -> bool:
        deleted_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db.execute(
            "UPDATE savings SET deleted_at = ? WHERE objective_id = ?",
            (deleted_date, objective_id)
        )
        self.db.execute(
            "UPDATE objectives SET deleted_at = ? WHERE id = ?",
            (deleted_date, objective_id)
        )
        return True

    def complete_objective(self, objective_id: int) -> bool:
        completed_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db.execute(
            "UPDATE objectives SET completed_at = ? WHERE id = ?",
            (completed_date, objective_id)
        )
        return True

    def get_objective_progress(self, objective_id: int) -> int:
        result = self.db.execute(
            "SELECT SUM(amount) FROM savings WHERE objective_id = ? AND deleted_at IS NULL",
            (objective_id,),
            fetch_one=True)
        return result[0] if result and result[0] else 0

    def get_objective_target(self, objective_id: int) -> int:
        result = self.db.execute(
            "SELECT target_amount FROM objectives WHERE id = ?",
            (objective_id,),
            fetch_one=True
        )
        return result[0] if result else 0

    def get_user_objectives(self, username: str) -> List[tuple]:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return []

        return self.db.execute(
            "SELECT id, title, reason, target_amount, completed_at FROM objectives WHERE user_id = ? AND deleted_at IS NULL",
            (user_id,),
            fetch_all=True
        )

    def get_total_target_amount(self, username: str) -> int:
        result = self.db.execute(
            "SELECT SUM(target_amount) FROM objectives o JOIN users u ON o.user_id = u.id WHERE u.name = ? AND o.deleted_at IS NULL",
            (username,),
            fetch_one=True
        )
        return result[0] if result and result[0] else 0

    def get_objective_activity(self, objective_id: int) -> List[Dict[str, Any]]:
        rows = self.db.execute(
            "SELECT amount, date, note FROM savings WHERE objective_id = ? AND deleted_at IS NULL ORDER BY id DESC",
            (objective_id,),
            fetch_all=True
        )
        return [{"amount": row[0], "date": row[1], "note": row[2]} for row in rows]

    def get_user_activity_raw(self, username: str) -> List[Dict[str, Any]]:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return []

        setting_row = self.db.execute(
            "SELECT history_cleared_at FROM user_settings WHERE user_id = ?",
            (user_id,),
            fetch_one=True
        )
        cleared_at = setting_row[0] if setting_row else None

        activities = []
        saving_rows = self.db.execute(
            "SELECT s.amount, s.date, o.title, s.note FROM savings s LEFT JOIN objectives o ON s.objective_id = o.id WHERE s.user_id = ?",
            (user_id,),
            fetch_all=True
        )

        for amount, date, title, note in saving_rows:
            activities.append({"type": "saving", "date": date, "amount": amount, "target_name": title, "note": note})

        objective_rows = self.db.execute(
            "SELECT title, created_at, target_amount, completed_at, deleted_at FROM objectives WHERE user_id = ?",
            (user_id,),
            fetch_all=True
        )

        for title, created_at, target, completed_at, deleted_at in objective_rows:
            activities.append({"type": "objective", "date": created_at, "title": title, "target": target})
            if completed_at: activities.append({"type": "completed", "date": completed_at, "title": title})
            if deleted_at: activities.append({"type": "deleted", "date": deleted_at, "title": title})

        filtered_activities = [act for act in activities if cleared_at is None or act["date"] > cleared_at]
        filtered_activities.sort(key=lambda x: x["date"], reverse=True)
        return filtered_activities

# ==========================================
# SPENDING PAGE LOGIC
# ==========================================

class SpendingDatabase:
    """Handles all logic related to the Spending page (daily expenses and incomes)."""

    def __init__(self, connection: DatabaseConnection, user_db: UserDatabase):
        self.db = connection
        self.user_db = user_db

    def add_expense_entry(self, username: str, amount: int, category: str, date: str, note: str = "") -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        self.db.execute(
            "INSERT INTO expenses (user_id, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, note)
        )
        return True

    def get_total_expense(self, username: str) -> int:
        result = self.db.execute(
            "SELECT SUM(amount) FROM expenses e JOIN users u ON e.user_id = u.id WHERE u.name = ?",
            (username,),
            fetch_one=True
        )
        return result[0] if result and result[0] else 0

    def get_user_expenses(self, username: str) -> list:
        rows = self.db.execute(
            "SELECT e.amount, e.category, e.date, e.note FROM expenses e JOIN users u ON e.user_id = u.id WHERE u.name = ? ORDER BY e.date DESC",
            (username,),
            fetch_all=True
        )
        return [{"amount": row[0], "category": row[1], "date": row[2], "note": row[3]} for row in rows]

    def add_income_entry(self, username: str, amount: int, category: str, date: str, note: str = "") -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        self.db.execute(
            "INSERT INTO incomes (user_id, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, note)
        )
        return True

    def get_total_income(self, username: str) -> int:
        result = self.db.execute(
            "SELECT SUM(amount) FROM incomes i JOIN users u ON i.user_id = u.id WHERE u.name = ?",
            (username,),
            fetch_one=True
        )
        return result[0] if result and result[0] else 0

    def get_user_incomes(self, username: str) -> list:
        rows = self.db.execute(
            "SELECT i.amount, i.category, i.date, i.note FROM incomes i JOIN users u ON i.user_id = u.id WHERE u.name = ? ORDER BY i.date DESC",
            (username,),
            fetch_all=True
        )
        return [{"amount": row[0], "category": row[1], "date": row[2], "note": row[3]} for row in rows]

# ==========================================
# MAIN DATABASE MANAGER
# ==========================================

class DatabaseManager:
    """The central point of access for all database operations."""

    def __init__(self, database_name: str = "data.db"):
        self.connection = DatabaseConnection(database_name)

        self.users = UserDatabase(self.connection)
        self.saving = SavingDatabase(self.connection, self.users)
        self.spending = SpendingDatabase(self.connection, self.users)

    def initialize_database(self) -> None:
        """Route the initialization call to the core connection."""

        self.connection.initialize_database()

# Instantiate the global object
db = DatabaseManager()
init = db.initialize_database