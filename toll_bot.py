import home
import settings
from user import User
from db_manager import DatabaseAccess
from datetime import date
from google import Mapper
from file_util import save_user_route_map, delete_image

logger = settings.base_logger.getChild(__name__)

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
            logger.error(f"Invalid date seen in database for user \"{user.id}\": {e}")

        return user

    def add_user_date(self, user_id: str, new_date: date):
        logger.info("Adding new date")
        user = self.get_user(user_id)
        try:
            user.add_date(new_date)
        except ValueError:
            logger.error(f"Unable to add date \"{new_date.isoformat()}\" to user \"{user.id}\"")
            return user
        # Only modify the database if we are working with a valid date
        self.db.add_date(user.id, new_date.isoformat())
        return user

    def delete_user_date(self, user_id, date_to_remove: date):
        logger.info("Remove date")
        user = self.get_user(user_id)

        try:
            user.delete_date(date_to_remove)
        except ValueError:
            logger.error(f"Unable to delete date \"{date_to_remove.isoformat()}\" from user \"{user.id}\"")
            return user

        # Only modify the database if we are working with a valid date
        self.db.delete_date(user.id, date_to_remove.isoformat())
        return user

    def handle_address_update(self, user_id: str, starting_address: str, campus_selection: str):
        try:
            directions = self.mapper.get_route(starting_address, campus_selection)
        except ValueError:
            logger.error("Could not get directions")
            logger.debug(f"Starting Address: {starting_address}, Campus: {campus_selection}")
            return

        #toll_coords = None
        datastream = self.mapper.get_static_map(directions=directions, toll_coords=None)
        if not datastream:
            logger.error("Could not get static map")
            return

        route_info = {
            "start" : starting_address,
            "end"   : campus_selection
        }

        save_user_route_map(user_id, route_info, datastream)

    def handle_delete_route(self, user_id):
        delete_image(user_id=user_id)