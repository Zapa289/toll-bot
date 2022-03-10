from abc import ABC, abstractmethod

import sqlite3
from sqlite3.dbapi2 import Cursor
class DatabaseAccess(ABC):
    """Controls access to _database"""

    @abstractmethod
    def get_user_dates(self, user_id: str) -> list:
        """Get the list of user's subscriptions"""

class SQLiteDatabaseAccess(DatabaseAccess):
    """Controls access to database"""

    def __init__(self, database_file: str):
        self._database = database_file  

    def get_user_dates(self, user_id) -> list[str]:
        """Get a list of all platforms owned by a user.
        """
        cur = self._execute(f'SELECT Date FROM Dates WHERE UserId={user_id}')
        user_dates = cur.fetchall()
        return [date for date, in user_dates]

    def add_date(self, user_id: str, date: str):
        self._execute('INSERT INTO Dates (UserId, Date) VALUES ( ?, ?)', (user_id, date))

    def _execute(self, command: str) -> Cursor:
        """Execute SQLite command. Returns the cursor for any data fetches."""
        with sqlite3.connect(self._database) as conn:
            cur = conn.cursor()
            #cur.execute("PRAGMA foreign_keys = ON")
            cur.execute(command)
        return cur

def main():
    pass

if __name__ == "__main__":
    main()
