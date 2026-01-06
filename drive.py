import os
import requests


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
    return gridpoints_data["properties"]["periods"]

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