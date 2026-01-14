import requests
from location_info import Location
from checktime import CheckTime
from datetime import timedelta
import os
from dotenv import load_dotenv
import requests
from typing import Optional

load_dotenv()  

def get_instant_data(location: Location, timestamp, api_key: Optional[str] = None):
    """
    timestamp: Unix seconds (int)
    api_key: optional; if None, read from env OW_API_KEY
    """
    if api_key is None:
        api_key = os.getenv("OpenWeather_API_KEY")

    if not api_key:
        raise ValueError("Missing OpenWeather_API_KEY.")

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


def get_yesterday_data(location: Location, api_key: Optional[str] = None):


    if api_key is None:
        api_key = os.getenv("OpenWeather_API_KEY")

    if not api_key:
        raise ValueError("Missing OpenWeather_API_KEY.")
    
    ct = CheckTime(location)

    yesterday = ct.day - timedelta(days=1)

    url = (
        "https://api.openweathermap.org/data/3.0/onecall/day_summary"
        f"?lat={ct.location.lat}&lon={ct.location.lon}"
        f"&date={yesterday}&appid={api_key}"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.json()


#test:
loc = Location("Stanford", 37.4275, -122.1697)
# ct = CheckTime(loc)
out = get_yesterday_data(loc)
print(out)
