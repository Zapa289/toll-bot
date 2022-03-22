OFFICE_DATA = [
    {
        "label" : "HST",
        "description" : "Houston Spring Campus",
        "address" : "1701 East Mossy Oaks Road, Spring, TX",
        "place_id": "ChIJ5V5eXDg1R4YRFysbysA6tAE",
        "location": {
            "lat": 30.0954837,
            "lng": -95.4421844
        }
    }
]
class Office:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

_office_list = []
for office in OFFICE_DATA:
    _office_list.append(Office(**office))

OFFICE_LIST : list[Office] = _office_list