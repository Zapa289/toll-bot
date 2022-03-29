from dataclasses import dataclass
from typing import Any

@dataclass(kw_only=True)
class Office:
    """Create an office based on all the attributes in OFFICE_DATA"""
    label : str
    description : str
    address : str
    place_id : str
    location : dict[str, Any]

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
        
office_list : list[Office] = []

for office in OFFICE_DATA:
    office_list.append(Office(**office))
    
OFFICE_LIST = office_list

def get_office(office_str: str) -> Office | None:
    for some_office in OFFICE_LIST:
        if some_office.label == office_str:
            return some_office

    return None    