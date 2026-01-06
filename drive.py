import os
import requests
from time import sleep

from zoneinfo import ZoneInfo
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, time, date

# The function to get the hourly forecast
def getHourlyForecast(latitude, longitude, user_agent={"User-Agent": "Pikachu"}):
    points_data = requests.get(
        f'https://api.weather.gov/points/{latitude},{longitude}',
        headers=user_agent
    ).json()
    office = points_data["properties"]["gridId"]
    gridX = points_data["properties"]["gridX"]
    gridY = points_data["properties"]["gridY"]

    sleep(1)    # Add 1 second delay between API requests

    # The "/hourly" is the only difference between the hourly and daily forecast URLs
    gridpoints_data = requests.get(
        f'https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecast/hourly',
        headers=user_agent
    ).json()
    return gridpoints_data

# This function is used to get the original data 
def getOriginalData(latitude, longitude, user_agent={"User-Agent": "Pikachu"}):
    points_data = requests.get(
        f'https://api.weather.gov/points/{latitude},{longitude}',
        headers=user_agent
    ).json()
    office = points_data["properties"]["gridId"]
    gridX = points_data["properties"]["gridX"]
    gridY = points_data["properties"]["gridY"]

    sleep(1)    # Add 1 second delay between API requests

    # The "/hourly" is the only difference between the hourly and daily forecast URLs
    gridpoints_data = requests.get(
        f'https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}',
        headers=user_agent
    ).json()
    return gridpoints_data


# Get the newest data ; 
def get_latest_observation(lat, lon, user_agent={"User-Agent": "Pikachu"}):
    # 1. points → observationStations
    points = requests.get(
        f"https://api.weather.gov/points/{lat},{lon}",
        headers=user_agent
    ).json()

    sleep(1)

    stations_url = points["properties"]["observationStations"]
    stations = requests.get(
        stations_url,
        headers=user_agent
    ).json()

    station_id = stations["features"][0]["properties"]["stationIdentifier"]

    sleep(1)

    # 2. latest observation
    obs = requests.get(
        f"https://api.weather.gov/stations/{station_id}/observations/latest",
        headers=user_agent
    ).json()

    return obs


# Get the observation in a specific range; 
def get_observation(lat, lon, start, end, limit=100, user_agent={"User-Agent": "Pikachu"}):
    points = requests.get(
        f"https://api.weather.gov/points/{lat},{lon}",
        headers=user_agent
    ).json()

    sleep(1)

    stations_url = points["properties"]["observationStations"]
    stations = requests.get(stations_url, headers=user_agent).json()

    station_id = stations["features"][0]["properties"]["stationIdentifier"]

    sleep(1)

    params = {"start": start, "end": end, "limit": limit}
    obs = requests.get(
        f"https://api.weather.gov/stations/{station_id}/observations",
        headers=user_agent,
        params=params
    ).json()
    return obs




# Four UTC timestamp every day ; 
def return_times(lat: float, lon: float, d: date , tz ):
    loc = LocationInfo(name="X", region="X", timezone=tz, latitude=lat, longitude=lon)
    s = sun(loc.observer, date=d, tzinfo=tz)
    
    dt_sunrise = s["sunrise"].replace(second=0, microsecond=0).astimezone(ZoneInfo('UTC')) 
    dt_1201 = datetime.combine(d, time(12, 1),tzinfo=tz).astimezone(ZoneInfo('UTC')) 
    dt_sunset =  s["sunset"].replace(second=0, microsecond=0).astimezone(ZoneInfo('UTC')) 
    dt_2359 = datetime.combine(d, time(23, 59),tzinfo=tz).astimezone(ZoneInfo('UTC')) 
    return dt_sunrise, dt_1201, dt_sunset, dt_2359


def return_local_times(lat: float, lon: float, d: date , tz ):
    loc = LocationInfo(name="X", region="X", timezone=tz, latitude=lat, longitude=lon)
    s = sun(loc.observer, date=d, tzinfo=tz)
    
    dt_sunrise = s["sunrise"].replace(second=0, microsecond=0)
    dt_1201 = datetime.combine(d, time(12, 1),tzinfo=tz)
    dt_sunset =  s["sunset"].replace(second=0, microsecond=0)
    dt_2359 = datetime.combine(d, time(23, 59),tzinfo=tz)

    return dt_sunrise, dt_1201, dt_sunset, dt_2359


# This function is universal 
def time_to_date_index(t : datetime , lat: float, lon: float, tz ): 
    t_local = t.astimezone(tz)
    d_local = t_local.date()
    dt_sunrise, dt_1201, dt_sunset, dt_2359= return_local_times( lat , lon , d_local, tz )

    if  t_local <= dt_sunrise:
        idx = 0
    elif dt_sunrise <= t_local < dt_1201:
        idx = 1
    elif dt_1201 <= t_local < dt_sunset:
        idx = 2
    else:
        idx = 3

    return d_local, idx

