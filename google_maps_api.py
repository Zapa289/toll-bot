import settings
from enum import Enum, auto
from googlemaps import Client
from googlemaps.maps import StaticMapMarker

class Office_Enum(Enum):
    HST = auto()


def get_poly_from_route(directions) -> str:
    return directions[0]['overview_polyline']['points']

def get_center_from_directions(directions) -> tuple:
    # SW + delta = NE
    # SW + (delta/2) = Center
    sw_bound = directions[0]['bounds']['southwest']
    ne_bound = directions[0]['bounds']['northeast']

    delta_lat = ne_bound['lat'] - sw_bound['lat']
    delta_lng = ne_bound['lng'] - sw_bound['lng']

    center_lat = sw_bound['lat'] + (delta_lat/2)
    center_lng = sw_bound['lng'] + (delta_lng/2)

    return (center_lat, center_lng)

def create_markers() -> list[StaticMapMarker]:
    markers = []

    main_markers = StaticMapMarker()
    
class Office:
    OFFICE_PLACE_IDS = {
    "HST" : { 
        "place_id": "ChIJ5V5eXDg1R4YRFysbysA6tAE",
        "location": {
            "lat": 30.0954837,
            "lng": -95.4421844
        },
        "office_id" : Office_Enum.HST
        }
    }
    def __init__(self, office_str: str):
        if not office_str in self.OFFICE_PLACE_IDS:
            raise ValueError(f"Not a valid office name: {office_str}")

        office = self.OFFICE_PLACE_IDS[office_str]
        self.place_id = office['place_id']
        self.office_id = office['office_id']
        self.location = (
            office["location"]["lat"],
            office["location"]["lng"]
        )

class Mapper:
    def __init__(self):
        self.key = settings.GOOGLE_MAPS_API_KEY
        self.client = Client(key=self.key)

    def get_static_map(self, location:str, office_str: str):
        """Get a static map from google. Returns a generator to get picture contents"""
        try:
            office = Office(office_str)
        except ValueError:
            #log the failure
            print(f"Invalid office location: {office_str}")
            return None

        # Get a route
        directions = self.client.directions(location, f"place_id:{office.place_id}")

        # Get center
        center = get_center_from_directions(directions)

        # Get polyline from route
        route_polyline = get_poly_from_route(directions)

        markers = create_markers()
        # Generate static map from polyline
        return self.client.static_map(center=center, size=500, path="enc:" + route_polyline)
    
def main():
    import file
    mapper = Mapper()
    address = input("Enter an address: ")
    office = input("Office: ")
    thing = mapper.get_static_map(address, office)
    file.create_user_map_file("test2.png", thing)

if __name__ == "__main__":
    main()