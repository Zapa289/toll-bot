from googlemaps import Client

import os

# from pathlib import Path
# from dotenv import load_dotenv

# env_path = Path('.') / '.env'
# load_dotenv(dotenv_path=env_path)

class Mapper:
    def __init__(self):
        self.key = os.environ['GOOGLE_MAPS_API_KEY']
        self.client = Client(key=self.key)

        return self.client

    def get_static_map(self, location:str):
        response = self.client.geocode(location)
        return
    