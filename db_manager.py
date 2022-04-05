import sqlite3
from abc import ABC, abstractmethod
from sqlite3.dbapi2 import Cursor
from typing import Tuple

from settings import base_logger

logger = base_logger.getChild(__name__)


class DatabaseAccess(ABC):
    """Controls access to _database"""

    @abstractmethod
    def get_user_dates(self, user_id: str) -> list[str]:
        """Get the list of user's tracked dates"""

    @abstractmethod
    def add_date(self, user_id: str, date: str):
        """Add a date to a user"""

    @abstractmethod
    def delete_date(self, user_id: str, date: str):
        """Delete a date from a user"""


class SQLiteDatabaseAccess(DatabaseAccess):
    """Controls access to database"""

    def __init__(self, database_file: str):
        logger.debug(f"Creating SQLite DB instance with {database_file}")
        self._database = database_file

    def get_user_dates(self, user_id) -> list[str]:
        """Get the list of user's tracked dates"""

        if not self._check_table(user_id=user_id):
            logger.warning("There is no table info for user %s", user_id)
            return []

        logger.info(f"Fetching dates for User {user_id}")
        cur = self._execute(f"SELECT * FROM {user_id}")
        if not cur:
            logger.error(f"Could not retrieve dates for User {user_id}, using empty list")
            return []

        user_dates = cur.fetchall()
        return [date for date, in user_dates]

    def add_date(self, user_id: str, date: str):
        if not self._check_table(user_id=user_id):
            self._create_user_table(user_id=user_id)

        logger.info("Add date %s to User %s", date, user_id)
        self._execute(f"INSERT INTO {user_id} (Dates) VALUES (?)", (date,))

    def delete_date(self, user_id: str, date: str):
        logger.info("Delete date %s from User %s", date, user_id)
        self._execute(f"DELETE FROM {user_id} WHERE Dates=?", (date,))

    def _create_user_table(self, user_id):
        """Create a new user table."""
        logger.info("Creating new table for User %s", user_id)
        self._execute(
            f"""
            CREATE TABLE IF NOT EXISTS {user_id} (
                "Dates"	TEXT NOT NULL UNIQUE
            )
        """
        )

    def _check_table(self, user_id):
        """Check if user has a table."""
        logger.debug("Checking if user %s exists in database")
        cur = self._execute(
            "SELECT tbl_name FROM sqlite_master WHERE type='table' AND tbl_name=?", (user_id,)
        )

        return cur.fetchall() if cur else False

    def _drop_user_table(self, user_id):
        """Drop a user's table."""
        logger.info("Dropping user %s from the database", user_id)
        self._execute(f"DROP TABLE IF EXISTS {user_id}")

    def _execute(self, command: str, parameters: Tuple = ()) -> Cursor:
        """Execute SQLite command. Returns the cursor for any data fetches or None if database error"""
        with sqlite3.connect(self._database) as conn:
            cur = conn.cursor()
            try:
                cur.execute(command, parameters)
            except sqlite3.OperationalError:
                logger.error(
                    "SQLite error on command '%s'; Parameters: '%s'",
                    command,
                    parameters,
                    exc_info=True,
                )
                return None

        return cur
