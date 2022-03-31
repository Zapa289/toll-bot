from datetime import date

import home
import settings
from db_manager import DatabaseAccess
from file_util import delete_user_map, save_user_route_map
from google import Mapper
from user import User

logger = settings.base_logger.getChild(__name__)


def convert_dates(raw_dates: list[str]) -> list[date]:
    """Convert a list of date strings from the db into date objects"""
    dates: list[date] = []
    for raw_date in raw_dates:
        dates.append(date.fromisoformat(raw_date))
    return dates


class TollBot:
    """Manages user creation and database interactions"""

    def __init__(self, database: DatabaseAccess):
        self.database = database
        self.mapper = Mapper()

    def home_tab(self, user_id):
        """Generate home tab for a user."""
        user = self.get_user(user_id=user_id)
        return home.get_home_tab(user)

    def get_user(self, user_id) -> User:
        """Create a user with dates matching the user_id in the database."""
        user = User(user_id)
        try:
            date_list = self.database.get_user_dates(user.id)
            user.dates = convert_dates(date_list)
        except ValueError as error:
            logger.error(
                'Invalid date seen in database for user "%s": %s', user_id, error
            )

        return user

    def add_user_date(self, user_id: str, new_date: date):
        """Add a date to a user and add the date to the database."""
        logger.info("Adding new date")
        user = self.get_user(user_id)
        try:
            user.add_date(new_date)
        except ValueError:
            logger.error(
                'Unable to add date "%s{}" to User %s', new_date.isoformat(), user.id
            )
            return user
        # Only modify the database if we are working with a valid date
        self.database.add_date(user.id, new_date.isoformat())
        return user

    def delete_user_date(self, user_id, date_to_remove: date):
        """Delete date from a user and remove the date from the database."""
        logger.info("Remove date")
        user = self.get_user(user_id)

        try:
            user.delete_date(date_to_remove)
        except ValueError:
            logger.error(
                'Unable to delete date "%s" from User %s',
                date_to_remove.isoformat(),
                user.id,
            )
            return user

        # Only modify the database if we are working with a valid date
        self.database.delete_date(user.id, date_to_remove.isoformat())
        return user

    def handle_address_update(
        self, user_id: str, starting_address: str, campus_selection: str
    ):
        """Take a start and end address and then create a static map from Google Maps.
        Static map will be downloaded and saved to the image cache."""
        try:
            directions = self.mapper.get_route(starting_address, campus_selection)
        except ValueError:
            logger.error("Could not get directions")
            logger.debug(
                f"Starting Address: {starting_address}, Campus: {campus_selection}"
            )
            return

        # toll_coords = None
        datastream = self.mapper.get_static_map(directions=directions, toll_coords=None)
        if not datastream:
            logger.error("Could not get static map")
            return

        route_info = {"start": starting_address, "end": campus_selection}

        save_user_route_map(user_id, route_info, datastream)

    def handle_delete_route(self, user_id):
        """Delete image from image cache"""
        delete_user_map(user_id=user_id)
