import requests
# from time import sleep
from location_info import Location
from checktime import CheckTime
from datetime import timedelta



# This function is used to get the current weather report
import requests

def get_instant_data(location: Location, timestamp, API_key):
    """
    timestamp: Unix seconds (int)
    """
    url = (
        "https://api.openweathermap.org/data/3.0/onecall/timemachine"
        f"?lat={location.lat}&lon={location.lon}"
        f"&dt={timestamp}&appid={API_key}"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


def get_yesterday_data(checktime: CheckTime, API_key):
    yesterday = checktime.day - timedelta(days=1)

    url = (
        "https://api.openweathermap.org/data/3.0/onecall/day_summary"
        f"?lat={checktime.location.lat}&lon={checktime.location.lon}"
        f"&date={yesterday}&appid={API_key}"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()



