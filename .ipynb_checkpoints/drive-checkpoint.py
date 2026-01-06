import os
import requests
from time import sleep

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
