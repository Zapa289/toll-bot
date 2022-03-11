import home
from lib.user import UserManager
from db_manager import DatabaseAccess

class TollBot: 
    def __init__(self, database: DatabaseAccess):
        self.db = database
        self.user_manager = UserManager(self.db)

    def home_tab(self, user_id):
        user = self.user_manager.new_user(user_id=user_id)
        return home.get_home_tab(user)

    def add_date(self, user_id, date):
        print("Let's add a new date...")
        user = self.user_manager.new_user(user_id)
        self.user_manager.add_date(user, date)
