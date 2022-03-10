class User:
    """Contains Slack user information"""
    def __init__(self, user_id) -> None:
        self.id = user_id
        self.dates_tracked: list[str] = []

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, user_id: str):
        if user_id[0] != "U":
            raise ValueError("Not a valid User ID!")
        self._id = user_id

    # @property
    # def team(self):
    #     return self.team

    # @team.setter
    # def team(self, team_id: str):
    #     if team_id[0] != "T":
    #         raise ValueError("Not a valid Team ID!")
    #     self.team = team_id