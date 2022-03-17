import home
from lib.user import User
from db_manager import DatabaseAccess
from datetime import date

class TollBot:
    def __init__(self, database: DatabaseAccess):
        self.db = database

    def home_tab(self, user_id):
        user = self.get_user(user_id=user_id)
        return home.get_home_tab(user)

    def get_user(self, user_id) -> User:
        user = User(user_id)
        try:
            user.dates = self.db.get_user_dates(user.id)
        except ValueError as e:
            print(f"Invalid date seen in database for user \"{user.id}\": {e}")
        return user

    def add_user_date(self, user_id: str, new_date: date):
        print("Let's add a new date...")
        user = self.get_user(user_id)
        try:
            user.add_date(new_date)
        except ValueError:
            print(f"Unable to add date \"{new_date.isoformat()}\" to user \"{user.id}\"")
            return user
        # Only modify the database if we are working with a valid date
        self.db.add_date(user.id, new_date.isoformat())
        return user

    def delete_user_date(self, user_id, date_to_remove: date):
        print("Let's delete a date...")
        user = self.get_user(user_id)
        try:
            user.delete_date(date_to_remove)
        except ValueError:
            print(f"Unable to delete date \"{date_to_remove.isoformat()}\" from user \"{user.id}\"")
            return user
        # Only modify the database if we are working with a valid date
        self.db.delete_date(user.id, date_to_remove.isoformat())
        return user
