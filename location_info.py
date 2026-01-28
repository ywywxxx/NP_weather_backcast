import requests
from timezonefinder import TimezoneFinder 

tf = TimezoneFinder()
# Basic Library to get the gridX, gridY of the location; 


class Location:
    def __init__(
        self,
        name: str,
        lat: float,
        lon: float,
        user_agent: dict[str, str] = {"User-Agent": "Pikachu"}
    ):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.timezone = tf.timezone_at(lat=self.lat, lng=self.lon)
        self.user_agent = user_agent

        point_info = self._fetch_point_info()

        self.office = point_info["gridId"]
        self.gridX = point_info["gridX"]
        self.gridY = point_info["gridY"]

    def _fetch_point_info(self) -> dict:
        url = f"https://api.weather.gov/points/{self.lat},{self.lon}"
        headers = self.user_agent
        # headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["properties"]


if __name__ == '__main__' : 
    loc = Location( name="Stanford",     
                     lat=37.4275,     
                     lon=-122.1697, )

    print("timezone:", loc.timezone)
    print("office:", loc.office)
    print("gridX:", loc.gridX)
    print("gridY:", loc.gridY)

# class location:
#     def __init__(
#         self,
#         name: str
#         lat: float,
#         lon: float,
#         office: str
#         gridX: int
#         gridY: int

#         user_agent: str = "Pikachu",
#     ):
#         self.name = name
#         self.lat = lat
#         self.lon = lon
#         self.office = self.getOffice(lat,lon,user_agent)
#         self.gridX = self.getgridX(lat,lon,user_agent)
#         self.gridY = self.getgridY(lat,lon,user_agent)
    
#         def getOffice(lat,lon,user_agent):
#             url = f'https://api.weather.gov/points/{lat},{lon}'
#             response = requests.get(url, headers=user_agent).json()
#             office = response["properties"]["gridId"]
#             return office
#         def getgridX(lat,lon,user_agent):
#             url = f'https://api.weather.gov/points/{lat},{lon}'
#             response = requests.get(url, headers=user_agent).json()
#             gridX = response["properties"]["gridX"]
#             return gridX       
#         def getgridX(lat,lon,user_agent):
#             url = f'https://api.weather.gov/points/{lat},{lon}'
#             response = requests.get(url, headers=user_agent).json()
#             gridY = response["properties"]["gridY"]
#             return gridY        


