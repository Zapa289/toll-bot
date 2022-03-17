from datetime import date
    
class User:
    """Contains Slack user information"""
    def __init__(self, user_id) -> None:
        self.id = user_id
        self._dates: list[date] = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, user_id: str):
        if user_id[0] != "U" or not user_id[1:].isalnum():
            raise ValueError("Not a valid User ID!")
        self._id = user_id

    @property
    def dates(self):
        return self._dates

    @dates.setter
    def dates(self, date_list: list[date]):
        self._dates = sorted(date_list)

    def add_date(self, new_date: date):
        if new_date in self._dates:
            print("Date already tracked by user")
            raise ValueError
        self._dates.append(new_date)

    def delete_date(self, del_date: date):
        try:
            self._dates.remove(del_date)
        except ValueError as e:
            print(f"Date not found in user: {del_date}")
            raise e

    def __repr__(self):
        return f"User ID {self.id}\n\tDates: {self.dates}"