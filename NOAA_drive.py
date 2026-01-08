import requests
from location_info import Location


def get_hourly_forecast(location: Location):
    url = f"https://api.weather.gov/gridpoints/{location.office}/{location.gridX},{location.gridY}/forecast/hourly"
    r = requests.get(url, headers=location.user_agent, timeout=20)
    r.raise_for_status()
    return r.json()


# This function is used to get the original data 
def get_raw_data(location):
    url = f"https://api.weather.gov/gridpoints/{location.office}/{location.gridX},{location.gridY}"
    r = requests.get(url, headers=location.user_agent, timeout=20)
    r.raise_for_status()
    return r.json()

##test:
# loc = Location("Stanford", 37.4275, -122.1697)
# data = get_hourly_forecast(loc)
# data = get_original_data(loc)


