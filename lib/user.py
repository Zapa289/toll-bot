from xmlrpc.client import DateTime
import settings
from db_manager import DatabaseAccess
from datetime import datetime

def valid_date(date: str) -> bool:
    """Verifies date strings are correct format"""

    try:
        datetime.strptime(date, settings.RAW_DATE_FORMAT)
    except (ValueError, TypeError):
        print(f"Invalid date \"{date}\", check date formatting")
        return False
    return True

def get_date_from_str(date: str) -> DateTime:
    return datetime.strptime(date, settings.RAW_DATE_FORMAT)

class User:
    """Contains Slack user information"""
    def __init__(self, user_id) -> None:
        self.id = user_id
        self._dates: list[str] = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, user_id: str):
        if user_id[0] != "U":
            raise ValueError("Not a valid User ID!")
        self._id = user_id

    @property
    def dates(self):
        return self._dates

    @dates.setter
    def dates(self, date_list: list[str]) -> list[str]:
        for date in date_list:
            if not valid_date(date):
                raise ValueError(date=date)
        self._dates = sorted(date_list, key=get_date_from_str)

    def add_date(self, date: str):
        if not valid_date(date):
            raise ValueError(date=date)
        self._dates.append(date)

    def delete_date(self, date: str):
        self._dates.remove(date)

    def __repr__(self):
        return f"User ID {self.id}, dates: {self.dates}"

class UserManager:
    def __init__(self, db: DatabaseAccess) -> None:
        self.db = db

    def get_user(self, user_id) -> User:
        user = User(user_id)
        try:
            user.dates = self.db.get_user_dates(user.id)
        except ValueError as e:
            print(f"Invalid date seen in database for user \"{user.id}\": {e['date']}")
        return user

    def add_date(self, user: User, date: str) -> User:
        try:
            user.add_date(date)
        except ValueError:
            print(f"Unable to add date \"{date}\" to user \"{user.id}\"")
            return user
        # Only modify the database if we are working with a valid date
        self.db.add_date(user.id, date)
        return user

    def delete_date(self, user: User, date: str) -> User:
        try:
            user.delete_date(date)
        except ValueError:
            print(f"Unable to delete date \"{date}\" from user \"{user.id}\"")
            return user

        # Only modify the database if we are working with a valid date
        self.db.delete_date(user.id, date)
        return user