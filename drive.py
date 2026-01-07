import os
import requests
from time import sleep

from zoneinfo import ZoneInfo
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, time, date


def getgrid(latitude, longitude, user_agent={"User-Agent": "Pikachu"}):
    points_data = requests.get(
        f'https://api.weather.gov/points/{latitude},{longitude}',
        headers=user_agent
    ).json()
    office = points_data["properties"]["gridId"]
    gridX = points_data["properties"]["gridX"]
    gridY = points_data["properties"]["gridY"]

    sleep(1)
    
    return office,gridX, gridY 





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

# This function is used to get the current weather report 
def getinstantdata(latitude,longitude,timestamp,API_key):
    res_point=requests.get(
		f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={timestamp}&appid={API_key}"
	  ).json()
    return res_point 

def getdaydata(latitude,longitude,date,API_key):
    res_day=requests.get(
    f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&date={date}&appid={API_key}"
    ).json()
    return res_day
    
    


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
    elif dt_sunrise < t_local <= dt_1201:
        idx = 1
    elif dt_1201 < t_local <= dt_sunset:
        idx = 2
    else:
        idx = 3

    return d_local, idx

