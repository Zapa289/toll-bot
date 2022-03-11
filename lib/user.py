from db_manager import DatabaseAccess
from datetime import datetime

def valid_date(date: str) -> bool:
    """Verifies date strings are correct format"""
    try:
        datetime.strptime(date, '%B %d, %Y')
    except ValueError:
        print(f"Invalid date \"{date}\", check date formatting")
        return False
    return True

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
        self._dates = date_list


    def add_date(self, date: str) -> list[str]:
        if not valid_date(date):
            raise ValueError(date=date)

        self._dates.append(date)

    def __repr__(self):
        return f"User ID {self.id}, dates: {self.dates}"

class UserManager:
    def __init__(self, db: DatabaseAccess) -> None:
        self.db = db

    def new_user(self, user_id) -> User:
        user = User(user_id)
        try:
            user.dates = self.db.get_user_dates(user.id)
        except ValueError as e:
            print(f"Invalid date seen in database for user \"{user.id}\": {e['date']}")
        return user

    def add_date(self, user: User, date: str):
        try:
            user.add_date(date)
        except ValueError:
            print(f"Unable to add date \"{date}\" to user \"{user.id}\"")
            return

        # Only modify the database if we are working with a valid date
        self.db.add_date(user.id, date)