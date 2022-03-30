from dataclasses import dataclass


@dataclass(kw_only=True)
class Office:
    """Create an office based on all the attributes in OFFICE_DATA"""

    label: str
    description: str
    address: str
    place_id: str
    location: dict


_OFFICE_DATA = [
    {
        "label": "HST",
        "description": "Houston Spring Campus",
        "address": "1701 East Mossy Oaks Road, Spring, TX",
        "place_id": "ChIJ5V5eXDg1R4YRFysbysA6tAE",
        "location": {"lat": 30.0954837, "lng": -95.4421844},
    }
]

# Create the office list
OFFICE_LIST = [Office(**office) for office in _OFFICE_DATA]


def get_office(office_str: str) -> Office | None:
    """Compare a given string against the labels in the office list. Return the matched office if any."""
    for some_office in OFFICE_LIST:
        if some_office.label == office_str:
            return some_office

    return None
