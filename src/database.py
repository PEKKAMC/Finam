# Copyright (c) 2026 PEKKAMC
# All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

import hashlib
import hmac
import re
import secrets
import sqlite3
from datetime import datetime
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

    def _migrate_money_columns_to_real(self) -> None:
        money_columns = {
            "objectives": "target_amount",
            "savings": "amount",
            "expenses": "amount",
            "incomes": "amount",
        }
        connection = sqlite3.connect(self.database_name)
        try:
            connection.execute("PRAGMA foreign_keys = OFF")
            connection.execute("BEGIN")
            for table, column in money_columns.items():
                table_info = connection.execute(f"PRAGMA table_info({table})").fetchall()
                column_info = next((row for row in table_info if row[1] == column), [])
                if not column_info or column_info[2].upper() == "REAL":
                    continue
                if column_info[2].upper() not in ("INT", "INTEGER"):
                    raise RuntimeError(f"Unexpected type for {table}.{column}: {column_info[2]}")

                create_sql = connection.execute(
                    "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = ?",
                    (table,),
                ).fetchone()[0]
                migration_table = f"__float_migration_{table}"
                connection.execute(f"DROP TABLE IF EXISTS {migration_table}")
                create_sql = create_sql.replace(
                    f"CREATE TABLE {table}",
                    f"CREATE TABLE {migration_table}",
                    1,
                )
                create_sql, replacements = re.subn(
                    rf"(\b{re.escape(column)}\s+)INTEGER\b",
                    r"\1REAL",
                    create_sql,
                    count=1,
                    flags=re.IGNORECASE,
                )
                if replacements != 1:
                    raise RuntimeError(f"Could not migrate {table}.{column} to REAL")

                connection.execute(create_sql)
                connection.execute(f"INSERT INTO {migration_table} SELECT * FROM {table}")
                connection.execute(f"DROP TABLE {table}")
                connection.execute(f"ALTER TABLE {migration_table} RENAME TO {table}")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize_database(self) -> None:
        Logger.debug("Initializing database tables...")
        try:
            self.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TEXT
                )
            ''')
            try:
                self.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
                Logger.info("Added created_at column to users table")
            except sqlite3.OperationalError:
                pass
            self.execute(
                "UPDATE users SET created_at = ? WHERE created_at IS NULL OR created_at = ''",
                (datetime.now().strftime("%Y-%m-%d %H:%M"),)
            )
            self.execute('''
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    history_cleared_at TEXT,
                    language TEXT DEFAULT 'vi',
                    currency TEXT DEFAULT 'VND (đ)',
                    FOREIGN KEY (user_id) REFERENCES users (id)
                 )
            ''')
            self.execute('''
                CREATE TABLE IF NOT EXISTS app_security_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    app_lock_enabled INTEGER NOT NULL DEFAULT 0,
                    pin_salt TEXT,
                    pin_hash TEXT
                )
            ''')
            self.execute(
                "INSERT OR IGNORE INTO app_security_settings (id) VALUES (1)"
            )

            try:
                self.execute("ALTER TABLE user_settings ADD COLUMN language TEXT DEFAULT 'vi'")
                Logger.info("Added language column to user_settings table")
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            try:
                self.execute("ALTER TABLE user_settings ADD COLUMN currency TEXT DEFAULT 'VND (đ)'")
                Logger.info("Added currency column to user_settings table")
            except sqlite3.OperationalError:
                # Column already exists
                pass
            
            self.execute('''
                CREATE TABLE IF NOT EXISTS objectives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    reason TEXT,
                    target_amount REAL NOT NULL,
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
                    amount REAL NOT NULL,
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
                    amount REAL NOT NULL,
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
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                note TEXT NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            self.execute('''
                CREATE TABLE IF NOT EXISTS purchase_scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    trigger TEXT,
                    reason TEXT,
                    thinking_time TEXT,
                    risk_score INTEGER NOT NULL,
                    trigger_display TEXT,
                    ai_advice TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

            self._migrate_money_columns_to_real()

            count = self.execute(
                "SELECT COUNT(*) FROM users",
                fetch_one=True
            )[0]
            if count == 0:
                self.execute(
                    "INSERT INTO users (name, created_at) VALUES (?, ?)",
                    (DefaultSettings.USERNAME, datetime.now().strftime("%Y-%m-%d %H:%M"))
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

    def get_all_users(self) -> List[Dict[str, str]]:
        rows = self.db.execute(
            "SELECT name, created_at FROM users ORDER BY id",
            fetch_all=True
        )
        return [
            {"name": row[0], "created_at": row[1] or ""}
            for row in rows
        ]

    def add_user(self, username: str, currency: str) -> bool:
        try:
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.db.execute(
                "INSERT INTO users (name, created_at) VALUES (?, ?)",
                (username, created_at)
            )
            self.set_currency(username, currency)
            return True
        except sqlite3.IntegrityError:
            return False

    def delete_user(self, username: str) -> None:
        user_id = self.get_user_id(username)
        if not user_id:
            return

        self.db.execute("DELETE FROM user_settings WHERE user_id = ?", (user_id,))
        self.db.execute("DELETE FROM purchase_scan_history WHERE user_id = ?", (user_id,))
        self.db.execute("DELETE FROM expenses WHERE user_id = ?", (user_id,))
        self.db.execute("DELETE FROM incomes WHERE user_id = ?", (user_id,))
        self.db.execute("DELETE FROM savings WHERE user_id = ?", (user_id,))
        self.db.execute("DELETE FROM objectives WHERE user_id = ?", (user_id,))
        self.db.execute("DELETE FROM users WHERE id = ?", (user_id,))

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

    def get_language(self, username: str) -> str:
        """Get the language setting for a user. Returns 'vi' by default."""
        user_id = self.get_user_id(username)
        if not user_id: return 'vi'

        result = self.db.execute(
            "SELECT language FROM user_settings WHERE user_id = ?",
            (user_id,),
            fetch_one=True
        )
        if result and result[0]:
            return result[0]
        return DefaultSettings.LANGUAGE

    def set_language(self, username: str, language: str) -> bool:
        """Set the language for a user."""
        user_id = self.get_user_id(username)
        if not user_id: return False

        exists = self.db.execute(
            "SELECT user_id FROM user_settings WHERE user_id = ?",
            (user_id,),
            fetch_one=True
        )

        try:
            if exists:
                self.db.execute(
                    "UPDATE user_settings SET language = ? WHERE user_id = ?",
                    (language, user_id)
                )
            else:
                self.db.execute(
                    "INSERT INTO user_settings (user_id, language) VALUES (?, ?)",
                    (user_id, language)
                )
            return True
        except Exception as ex:
            Logger.error(f"Failed to set language: {ex}")
            return False

    def get_currency(self, username: str) -> str:
        """Get the currency setting for a user. Returns DefaultSettings.CURRENCY by default."""
        user_id = self.get_user_id(username)
        if not user_id: return DefaultSettings.CURRENCY

        result = self.db.execute(
            "SELECT currency FROM user_settings WHERE user_id = ?",
            (user_id,),
            fetch_one=True
        )
        if result and result[0]:
            return result[0]
        return DefaultSettings.CURRENCY

    def set_currency(self, username: str, currency: str) -> bool:
        """Set the currency for a user."""
        user_id = self.get_user_id(username)
        if not user_id: return False

        exists = self.db.execute(
            "SELECT user_id FROM user_settings WHERE user_id = ?",
            (user_id,),
            fetch_one=True
        )

        try:
            if exists:
                self.db.execute(
                    "UPDATE user_settings SET currency = ? WHERE user_id = ?",
                    (currency, user_id)
                )
            else:
                self.db.execute(
                    "INSERT INTO user_settings (user_id, currency) VALUES (?, ?)",
                    (user_id, currency)
                )
            return True
        except Exception as ex:
            Logger.error(f"Failed to set currency: {ex}")
            return False


class AppSecurityDatabase:
    """Stores device-wide app lock settings needed before a user is selected."""

    _PIN_ITERATIONS = 200_000

    def __init__(self, connection: DatabaseConnection):
        self.db = connection

    def is_app_lock_enabled(self) -> bool:
        result = self.db.execute(
            "SELECT app_lock_enabled FROM app_security_settings WHERE id = 1",
            fetch_one=True
        )
        return bool(result and result[0])

    @staticmethod
    def _hash_pin(pin: str, salt: bytes) -> bytes:
        return hashlib.pbkdf2_hmac(
            "sha256",
            pin.encode("ascii"),
            salt,
            AppSecurityDatabase._PIN_ITERATIONS
        )

    def set_app_lock_pin(self, pin: str) -> bool:
        if len(pin) != 4 or not pin.isascii() or not pin.isdigit():
            return False

        salt = secrets.token_bytes(16)
        pin_hash = self._hash_pin(pin, salt)
        self.db.execute(
            """
            UPDATE app_security_settings
            SET app_lock_enabled = 1, pin_salt = ?, pin_hash = ?
            WHERE id = 1
            """,
            (salt.hex(), pin_hash.hex())
        )
        return True

    def disable_app_lock(self) -> None:
        self.db.execute(
            """
            UPDATE app_security_settings
            SET app_lock_enabled = 0, pin_salt = NULL, pin_hash = NULL
            WHERE id = 1
            """
        )

    def verify_app_lock_pin(self, pin: str) -> bool:
        if len(pin) != 4 or not pin.isascii() or not pin.isdigit():
            return False

        result = self.db.execute(
            """
            SELECT app_lock_enabled, pin_salt, pin_hash
            FROM app_security_settings
            WHERE id = 1
            """,
            fetch_one=True
        )
        if not result or not result[0] or not result[1] or not result[2]:
            return False

        try:
            salt = bytes.fromhex(result[1])
            expected_hash = bytes.fromhex(result[2])
        except ValueError as ex:
            Logger.error(f"Invalid stored app lock credentials: {ex}")
            return False

        actual_hash = self._hash_pin(pin, salt)
        return hmac.compare_digest(actual_hash, expected_hash)

# ==========================================
# SAVING PAGE LOGIC
# ==========================================

class SavingsDatabase:
    """Handles all logic related to the Saving page (objectives and objective deposits)."""

    def __init__(self, connection: DatabaseConnection, user_db: UserDatabase):
        self.db = connection
        self.user_db = user_db

    def add_saving_entry(self, username: str, amount: float, date: str, objective_id: int, note: str = "") -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        objective_id_value = None if objective_id == 0 else objective_id
        self.db.execute(
            "INSERT INTO savings (user_id, objective_id, amount, date, note) VALUES (?, ?, ?, ?, ?)",
            (user_id, objective_id_value, amount, date, note)
        )
        if objective_id_value is not None and amount > 0:
            result = self.db.execute(
                "SELECT o.target_amount, COALESCE(SUM(s.amount), 0) "
                "FROM objectives o LEFT JOIN savings s ON s.objective_id = o.id AND s.deleted_at IS NULL "
                "WHERE o.id = ? GROUP BY o.id",
                (objective_id_value,),
                fetch_one=True,
            )
            if result and 0 < result[0] <= result[1]:
                self.complete_objective(objective_id_value)
        return True

    def get_total_savings(self, username: str) -> float:
        result = self.db.execute(
            "SELECT SUM(amount) FROM savings s JOIN users u ON s.user_id = u.id WHERE u.name = ? AND s.deleted_at IS NULL",
            (username,), fetch_one=True
        )
        return float(result[0]) if result and result[0] else 0.0

    def add_objective(self, username: str, title: str, reason: str, target_amount: float) -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db.execute(
            "INSERT INTO objectives (user_id, title, reason, target_amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, reason, target_amount, created_at)
        )
        return True

    def create_goal_with_initial_deposit(self, username: str, title: str, reason: str, target_amount: float, initial_deposit: float) -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        objective_id = self.db.execute(
            "INSERT INTO objectives (user_id, title, reason, target_amount, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, title, reason, target_amount, created_at)
        )
        if objective_id and initial_deposit > 0:
            self.add_saving_entry(username, initial_deposit, created_at, objective_id, "Nạp tiền dư khởi tạo")
        return True

    def transfer_surplus(self, username: str, source_id: int, target_id: int, amount: float, note: str = "") -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.complete_objective(source_id)
        if amount > 0:
            self.add_saving_entry(username, amount, date, target_id, note or "Chuyển tiền dư từ mục tiêu hoàn thành")
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
            "UPDATE objectives SET completed_at = ? WHERE id = ? AND completed_at IS NULL",
            (completed_date, objective_id)
        )
        return True

    def get_objective_progress(self, objective_id: int) -> float:
        result = self.db.execute(
            "SELECT SUM(amount) FROM savings WHERE objective_id = ? AND deleted_at IS NULL",
            (objective_id,),
            fetch_one=True)
        return float(result[0]) if result and result[0] else 0.0

    def get_objective_target(self, objective_id: int) -> float:
        result = self.db.execute(
            "SELECT target_amount FROM objectives WHERE id = ?",
            (objective_id,),
            fetch_one=True
        )
        return float(result[0]) if result else 0.0

    def get_user_objectives(self, username: str) -> List[tuple]:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return []

        rows = self.db.execute(
            "SELECT id, title, reason, target_amount, completed_at FROM objectives WHERE user_id = ? AND deleted_at IS NULL",
            (user_id,),
            fetch_all=True
        )
        return [(row[0], row[1], row[2], float(row[3]), row[4]) for row in rows]

    def get_total_target_amount(self, username: str) -> float:
        result = self.db.execute(
            "SELECT SUM(target_amount) FROM objectives o JOIN users u ON o.user_id = u.id WHERE u.name = ? AND o.deleted_at IS NULL",
            (username,),
            fetch_one=True
        )
        return float(result[0]) if result and result[0] else 0.0

    def get_objective_activity(self, objective_id: int) -> List[Dict[str, Any]]:
        rows = self.db.execute(
            "SELECT amount, date, note FROM savings WHERE objective_id = ? AND deleted_at IS NULL ORDER BY id DESC",
            (objective_id,),
            fetch_all=True
        )
        return [{"amount": float(row[0]), "date": row[1], "note": row[2]} for row in rows]

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
        savings_rows = self.db.execute(
            "SELECT s.amount, s.date, o.title, s.note FROM savings s LEFT JOIN objectives o ON s.objective_id = o.id WHERE s.user_id = ?",
            (user_id,),
            fetch_all=True
        )

        for amount, date, title, note in savings_rows:
            activities.append({"type": "savings", "date": date, "amount": float(amount), "target_name": title, "note": note})

        objective_rows = self.db.execute(
            "SELECT title, created_at, target_amount, completed_at, deleted_at FROM objectives WHERE user_id = ?",
            (user_id,),
            fetch_all=True
        )

        for title, created_at, target, completed_at, deleted_at in objective_rows:
            activities.append({"type": "objective", "date": created_at, "title": title, "target": float(target)})
            if completed_at: activities.append({"type": "completed", "date": completed_at, "title": title})
            if deleted_at: activities.append({"type": "deleted", "date": deleted_at, "title": title})

        filtered_activities = [act for act in activities if cleared_at is None or act["date"] > cleared_at]
        filtered_activities.sort(key=lambda x: x["date"], reverse=True)
        return filtered_activities

# ==========================================
# SPENDING PAGE LOGIC
# ==========================================

class SpendingDatabase:
    """Handles all logic related to the Spending page (expenses and incomes)."""

    def __init__(self, connection: DatabaseConnection, user_db: UserDatabase):
        self.db = connection
        self.user_db = user_db

    def add_expense_entry(self, username: str, amount: float, category: str, date: str, note: str = "") -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        self.db.execute(
            "INSERT INTO expenses (user_id, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, note)
        )
        return True

    def get_total_expense(self, username: str) -> float:
        result = self.db.execute(
            "SELECT SUM(amount) FROM expenses e JOIN users u ON e.user_id = u.id WHERE u.name = ?",
            (username,),
            fetch_one=True
        )
        return float(result[0]) if result and result[0] else 0.0

    def get_user_expenses(self, username: str) -> list:
        rows = self.db.execute(
            "SELECT e.id, e.amount, e.category, e.date, e.note FROM expenses e JOIN users u ON e.user_id = u.id WHERE u.name = ? ORDER BY e.date DESC",
            (username,),
            fetch_all=True
        )
        return [{"id": row[0], "amount": float(row[1]), "category": row[2], "date": row[3], "note": row[4]} for row in rows]

    def add_income_entry(self, username: str, amount: float, category: str, date: str, note: str = "") -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id: return False

        self.db.execute(
            "INSERT INTO incomes (user_id, amount, category, date, note) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, note)
        )
        return True

    def get_total_income(self, username: str) -> float:
        result = self.db.execute(
            "SELECT SUM(amount) FROM incomes i JOIN users u ON i.user_id = u.id WHERE u.name = ?",
            (username,),
            fetch_one=True
        )
        return float(result[0]) if result and result[0] else 0.0

    def get_user_incomes(self, username: str) -> list:
        rows = self.db.execute(
            "SELECT i.id, i.amount, i.category, i.date, i.note FROM incomes i JOIN users u ON i.user_id = u.id WHERE u.name = ? ORDER BY i.date DESC",
            (username,),
            fetch_all=True
        )
        return [{"id": row[0], "amount": float(row[1]), "category": row[2], "date": row[3], "note": row[4]} for row in rows]

    def delete_entry(self, username: str, entry_id: int) -> bool:
        """Delete an expense or income entry by ID. Tries both tables and returns success."""
        user_id = self.user_db.get_user_id(username)
        if not user_id:
            return False

        try:
            # Try deleting from expenses first
            with sqlite3.connect(self.db.database_name) as connection:
                connection.execute("PRAGMA foreign_keys = ON;")
                cursor = connection.cursor()
                cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (entry_id, user_id))
                if cursor.rowcount > 0:
                    connection.commit()
                    return True

                # If not found in expenses, try incomes
                cursor.execute("DELETE FROM incomes WHERE id = ? AND user_id = ?", (entry_id, user_id))
                deleted = cursor.rowcount > 0
                connection.commit()
                return deleted
        except Exception as ex:
            Logger.error(f"Error deleting entry {entry_id} for user {username}: {ex}")
            return False

# ==========================================
# PURCHASE SCANNER LOGIC
# ==========================================

class PurchaseScannerDatabase:
    """Handles purchase scanner scan history entries."""

    def __init__(self, connection: DatabaseConnection, user_db: UserDatabase):
        self.db = connection
        self.user_db = user_db

    def add_scan_result(self, username: str, item_name: str, price: float, trigger: str, reason: str, thinking_time: str, risk_score: int, trigger_display: str, ai_advice: str) -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id:
            return False

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db.execute(
            """
            INSERT INTO purchase_scan_history (
                user_id, item_name, price, trigger, reason, thinking_time, risk_score, trigger_display, ai_advice, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, item_name, float(price), trigger, reason, thinking_time, int(risk_score), trigger_display, ai_advice, created_at),
        )
        return True

    def get_user_scan_history(self, username: str) -> list[dict]:
        user_id = self.user_db.get_user_id(username)
        if not user_id:
            return []

        rows = self.db.execute(
            """
            SELECT id, item_name, price, trigger, reason, thinking_time, risk_score, trigger_display, ai_advice, created_at
            FROM purchase_scan_history
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
            fetch_all=True,
        )
        return [
            {
                "id": row[0],
                "item_name": row[1],
                "price": row[2],
                "trigger": row[3],
                "reason": row[4],
                "thinking_time": row[5],
                "risk_score": row[6],
                "trigger_display": row[7],
                "ai_advice": row[8],
                "created_at": row[9],
            }
            for row in rows
        ]

    def delete_scan_result(self, username: str, scan_id: int) -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id or scan_id is None:
            return False

        self.db.execute(
            "DELETE FROM purchase_scan_history WHERE user_id = ? AND id = ?",
            (user_id, scan_id),
        )
        return True

    def clear_user_scan_history(self, username: str) -> bool:
        user_id = self.user_db.get_user_id(username)
        if not user_id:
            return False

        self.db.execute("DELETE FROM purchase_scan_history WHERE user_id = ?", (user_id,))
        return True

# ==========================================
# MAIN DATABASE MANAGER
# ==========================================

class DatabaseManager:
    """The central point of access for all database operations."""

    def __init__(self, database_name: str = "data.db"):
        self.connection = DatabaseConnection(database_name)

        self.users = UserDatabase(self.connection)
        self.app_security = AppSecurityDatabase(self.connection)
        self.savings = SavingsDatabase(self.connection, self.users)
        self.spending = SpendingDatabase(self.connection, self.users)
        self.scanner_history = PurchaseScannerDatabase(self.connection, self.users)

    def initialize_database(self) -> None:
        """Route the initialization call to the core connection."""

        self.connection.initialize_database()

# Instantiate the global object
db = DatabaseManager()
init = db.initialize_database
