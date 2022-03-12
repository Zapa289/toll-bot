from abc import ABC, abstractmethod

import sqlite3
from sqlite3.dbapi2 import Cursor
from typing import Tuple

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
        self._database = database_file

    def get_user_dates(self, user_id) -> list[str]:
        """Get a list of all platforms owned by a user.
        """
        cur = self._execute("SELECT Date FROM Dates WHERE UserId=?", (user_id,))
        if not cur:
            return []

        user_dates = cur.fetchall()
        return [date for date, in user_dates]

    def add_date(self, user_id: str, date: str):
        self._execute('INSERT INTO Dates (UserId, Date) VALUES ( ?, ?)', (user_id, date))

    def delete_date(self, user_id: str, date: str):
        self._execute('DELETE FROM Dates WHERE UserId=? AND Date=?', (user_id, date))

    def _execute(self, command: str, parameters: Tuple) -> Cursor:
        """Execute SQLite command. Returns the cursor for any data fetches or None if database error"""
        with sqlite3.connect(self._database) as conn:
            cur = conn.cursor()
            try:
                cur.execute(command, parameters)
            except sqlite3.OperationalError as e:
                print(f"Error accessing database: {command}")
                print(f"SQLite3: {e}")
                return None

        return cur

def main():
    pass

if __name__ == "__main__":
    main()
