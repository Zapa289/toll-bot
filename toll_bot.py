import home
import settings
from lib.user import User
from db_manager import DatabaseAccess
from datetime import date
from google import Mapper
from lib.util import hash_user_id, write_to_image_cache

def convert_dates(raw_dates: list[str]) -> list[date]:
    """Convert a list of date strings from the db into date objects"""
    dates: list[date] = []
    for raw_date in raw_dates:
        dates.append(date.fromisoformat(raw_date))
    return dates


class TollBot:
    def __init__(self, database: DatabaseAccess):
        self.db = database
        self.mapper = Mapper()

    def home_tab(self, user_id):
        user = self.get_user(user_id=user_id)
        return home.get_home_tab(user)

    def get_user(self, user_id) -> User:
        user = User(user_id)
        try:
            date_list = self.db.get_user_dates(user.id)
            user.dates = convert_dates(date_list)
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

    def handle_address_update(self, user_id: str, starting_address: str, campus_selection: str):
        #user = self.get_user(user_id)
        try:
            directions = self.mapper.get_route(starting_address, campus_selection)
        except ValueError as e:
            print(e)
            return
        #toll_coords = None
        datastream = self.mapper.get_static_map(directions=directions)

        filename = hash_user_id(user_id) + settings.IMAGE_FILE_TYPE
        write_to_image_cache(filename, datastream)
