import home
from lib.user import User
from db_manager import DatabaseAccess

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
            print(f"Invalid date seen in database for user \"{user.id}\": {e['date']}")
        return user

    def add_user_date(self, user_id, date):
        print("Let's add a new date...")
        user = self.get_user(user_id)
        try:
            user.add_date(date)
        except ValueError:
            print(f"Unable to add date \"{date}\" to user \"{user.id}\"")
            return user
        # Only modify the database if we are working with a valid date
        self.db.add_date(user.id, date)
        return user

    def delete_user_date(self, user_id, date):
        print("Let's delete a date...")
        user = self.get_user(user_id)
        try:
            user.delete_date(date)
        except ValueError:
            print(f"Unable to delete date \"{date}\" from user \"{user.id}\"")
            return user
        # Only modify the database if we are working with a valid date
        self.db.delete_date(user.id, date)
        return user
