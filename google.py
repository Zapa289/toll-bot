from dataclasses import dataclass
from settings import GOOGLE_MAPS_API_KEY, base_logger, IMAGE_SIZE
from offices import get_office
from googlemaps import Client
from googlemaps.maps import StaticMapMarker

logger = base_logger.getChild(__name__)

@dataclass
class Directions:
    directions: dict

    @property
    def _leg(self):
        return self.directions[0]['legs'][0]

    @property
    def markers(self) -> list[str]:
        start_marker = self._leg["start_location"]
        end_marker = self._leg["end_location"]

        return [start_marker, end_marker]

    @property
    def start_address(self):
        return self._leg['start_address']

    @property
    def end_address(self):
        return self._leg['end_address']

    @property
    def polyline(self):
        return self.directions[0]['overview_polyline']['points']

class Mapper:
    def __init__(self):
        self.key = GOOGLE_MAPS_API_KEY
        self.client = Client(key=self.key)

    def get_route(self, location:str, office_str: str) -> Directions:
        """Get Google Maps route between the given location and chosen office"""
        logger.info("Creating route")
        office = get_office(office_str)
        if not office:
            logger.error(f"Office {office_str} not found")
            raise ValueError("Invalid office input")

        return Directions(self.client.directions(location, f"place_id:{office.place_id}"))

    def get_static_map(self, directions: Directions, toll_coords: list=None):
        """Get a static map from google. Returns a generator to get picture contents"""
        logger.info("Get static map")

        markers = []
        markers.append(StaticMapMarker(directions.markers))
        if toll_coords:
            markers.append(StaticMapMarker(toll_coords))

        logger.debug(f"Polyline: {directions.polyline}")

        # Generate static map from polyline
        try:
            datastream = self.client.static_map(size=IMAGE_SIZE, path="enc:" + directions.polyline, markers=markers)
        except ValueError:
            logger.error("Failed to get static map", exc_info=True)
            return None

        return datastream

def main():
    mapper = Mapper(tolls=None)
    address = input("Enter an address: ")
    office = input("Office: ")
    try:
        directions = mapper.get_route(address, office)
    except ValueError:
        return

    thing = mapper.get_static_map(directions=directions)

    with open("test3.png", "wb") as file:
        for chunk in thing:
            _ = file.write(chunk)

if __name__ == "__main__":
    main()