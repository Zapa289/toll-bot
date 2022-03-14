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
    def dates(self, date_list: list[str]):
        for date in date_list:
            if not valid_date(date):
                raise ValueError
        self._dates = sorted(date_list, key=get_date_from_str)

    def add_date(self, date: str):
        if not valid_date(date):
            raise ValueError
        self._dates.append(date)

    def delete_date(self, date: str):
        if not valid_date(date):
            raise ValueError
        self._dates.remove(date)

    def __repr__(self):
        return f"User ID {self.id}, dates: {self.dates}"

class UserDate:
    def __init__(self, date_raw: str, date_formatted: str):
        self.date_raw = date_raw
        self.date_formatted = date_formatted

    @classmethod
    def from_raw(cls, date_raw: str):
        try:
            date_formatted = datetime.strptime(date_raw, settings.RAW_DATE_FORMAT).strftime(settings.DATE_FORMAT)
        except:
            raise ValueError
        return cls(date_raw=date_raw, date_formatted=date_formatted)

    @classmethod
    def from_formatted(cls, date_formatted: str):
        try:
            date_raw = datetime.strptime(date_formatted, settings.DATE_FORMAT).strftime(settings.RAW_DATE_FORMAT)
        except:
            raise ValueError
        return cls(date_raw=date_raw, date_formatted=date_formatted)