import requests

from settings import TOLL_GURU_API_KEY, base_logger

logger = base_logger.getChild(__name__)


class TollGuruException(Exception):
    """Tollguru API exception"""


def get_toll_markers(polyline) -> list:
    """Use the google polyline to create a list of tolls the user will pass through and their rates."""

    try:
        toll_response = get_rates_from_tollguru(polyline)
    except TollGuruException as error:
        logger.error("Error getting tolls: %s", error, exc_info=True)
        return []

    if not toll_response["hasTolls"]:
        return []

    logger.info("Creating toll markers")
    toll_markers = []

    for toll in toll_response["tolls"]:
        toll_markers.append((toll["lat"], toll["lng"]))

    logger.debug("Markers: %s", toll_markers)

    return toll_markers


def get_rates_from_tollguru(polyline):
    """Get the toll rates from the Tollguru API"""

    # Tollguru querry url
    tolls_url = "https://dev.tollguru.com/v1/calc/route"

    # Tollguru resquest parameters
    headers = {"Content-type": "application/json", "x-api-key": TOLL_GURU_API_KEY}
    params = {
        "source": "google",
        "polyline": polyline,
    }

    # Requesting Tollguru with parameters
    logger.info("Checking Tollguru API for tolls")
    response_tollguru = requests.post(tolls_url, json=params, headers=headers, timeout=200).json()

    # checking for errors or printing rates
    if str(response_tollguru).find("message") == -1:
        return response_tollguru["route"]
    else:

        raise TollGuruException(response_tollguru["message"])
