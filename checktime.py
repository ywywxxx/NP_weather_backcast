from typing import Optional
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo
from astral import LocationInfo
from astral.sun import sun
from location_info import Location   
from collections import defaultdict
from datetime import datetime


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
        """
        day: 'YYYY-MM-DD' string or date
        """
        loc = LocationInfo(
            name=location.name,
            region="X",
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

# #test:
# loc = Location("Stanford", 37.4275, -122.1697)
# ct = CheckTime(loc)

# print("day:", ct.day)
# print("sunrise_local:", ct.sunrise_local)
# print("sunrise_UTC:", ct.sunrise_UTC)
# print("run1:", ct.run1)


def time2index(t: datetime, location: Location):
    tz = ZoneInfo(location.timezone)
    t_local = t.astimezone(tz)
    d_local = t_local.date()

    ct = CheckTime(location, day=d_local)

    if t_local <= ct.sunrise_local:
        idx = 0
    elif t_local <= ct.noon_local:
        idx = 1
    elif t_local <= ct.sunset_local:
        idx = 2
    else:
        idx = 3

    return d_local, idx


def group_by_index(records, time_key, location, now_dt):
    groups = defaultdict(list)

    d_now, idx_now = time2index(now_dt, location)

    for r in records:
        if time_key == "validTime":
            dt_pred = datetime.fromisoformat(r["validTime"].split("/")[0])
        else:
            dt_pred = datetime.fromisoformat(r[time_key])

        d_pred, idx_pred = time2index(dt_pred, location)
        groups[(d_now, idx_now, d_pred, idx_pred)].append(r)

    return groups



