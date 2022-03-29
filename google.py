from settings import GOOGLE_MAPS_API_KEY, base_logger
from offices import get_office
from googlemaps import Client
from googlemaps.maps import StaticMapMarker

logger = base_logger.getChild(__name__)

def get_poly_from_route(directions) -> str:
    return directions[0]['overview_polyline']['points']

def get_markers_from_directions(directions) -> list[dict]:
    """Returns a list of lat/lng dicts of the start and end of the route."""
    leg = directions[0]['legs'][0]
    start_marker = leg["start_location"]
    end_marker = leg["end_location"]

    return [start_marker, end_marker]


class Mapper:
    def __init__(self):
        self.key = GOOGLE_MAPS_API_KEY
        self.client = Client(key=self.key)

    def get_route(self, location:str, office_str: str):
        logger.info("Creating route")
        office = get_office(office_str)
        if not office:
            logger.error(f"Office {office_str} not found")
            raise ValueError("Invalid office input")

        return self.client.directions(location, f"place_id:{office.place_id}")

    def get_static_map(self, directions, toll_coords: list=None):
        """Get a static map from google. Returns a generator to get picture contents"""
        logger.info("Get static map")
        # Get polyline from route
        route_polyline = get_poly_from_route(directions)

        markers = []
        markers.append(StaticMapMarker(get_markers_from_directions(directions)))
        if toll_coords:
            markers.append(StaticMapMarker(toll_coords))

        logger.debug(f"\tPolyline: {route_polyline}\n\tMarkers: {markers}")

        # Generate static map from polyline
        try:
            datastream = self.client.static_map(size=[500,400], path="enc:" + route_polyline, markers=markers)
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