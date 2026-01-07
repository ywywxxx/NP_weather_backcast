from typing import Optional
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from astral import LocationInfo
from astral.sun import sun
from location_info import Location   

class CheckTime:
    def __init__(
        self,
        location: Location,
        day: Optional[date] = None,
    ):
        self.location = location
        self.tz = ZoneInfo(location.timezone)
        if day is None:
            day = datetime.now(self.tz).date()
        self.day = day
        loc = LocationInfo(
            # name=location.name,
            # region="X",
            timezone=location.timezone,
            latitude=location.lat,
            longitude=location.lon,
        )

        s = sun(loc.observer, date=self.day, tzinfo=self.tz)

        # ===== local times =====
        self.sunrise_local = s["sunrise"].replace(second=0, microsecond=0)
        self.sunset_local = s["sunset"].replace(second=0, microsecond=0)
        self.noon_local = datetime.combine(self.day, time(12, 1), tzinfo=self.tz)
        self.midnight_local = datetime.combine(self.day, time(23, 59), tzinfo=self.tz)

        # ===== UTC times =====
        self.sunrise_UTC = self.sunrise_local.astimezone(ZoneInfo("UTC"))
        self.sunset_UTC = self.sunset_local.astimezone(ZoneInfo("UTC"))
        self.noon_UTC = self.noon_local.astimezone(ZoneInfo("UTC"))
        self.midnight_UTC = self.midnight_local.astimezone(ZoneInfo("UTC"))

        # ===== run windows: 30 min earlier =====
        delta = timedelta(minutes=30)
        self.run1 = self.sunrise_local - delta
        self.run2 = self.noon_local - delta
        self.run3 = self.sunset_local - delta
        self.run4 = self.midnight_local - delta

        # self.sunrise_local
        # self.sunset_local
        # self.sunrise_UTC
        # self.sunset_UTC
        # self.noon_UTC
        # self.midnight_UTC
        # self.run1 = self.sunrise_local -30min
        # self.run2 = 12:01pm -30min
        # self.run3 = self.sunset_local -30min
        # self.run4 = 11:59pm -30min
loc = Location("Stanford", 37.4275, -122.1697)
ct = CheckTime(loc)

print("sunrise_local:", ct.sunrise_local)
print("sunrise_UTC:", ct.sunrise_UTC)
print("run1:", ct.run1)

        



