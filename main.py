from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time

from checktime import CheckTime
from location_info import Location
from forecast import clean_data
from backcast import get_yesterday_data
from WeatherSql import WeatherSql


def get_due_run_slot(loc: Location, window_sec: int = 60):
    """
    Return which run slot is due right now:
      1 -> run1, 2 -> run2, 3 -> run3, 4 -> run4
    Return None if not within the window of any run time.
    """
    tz = ZoneInfo(loc.timezone)
    now = datetime.now(tz)

    ct = CheckTime(loc, day=now.date())
    run_times = {1: ct.run1, 2: ct.run2, 3: ct.run3, 4: ct.run4}

    w = timedelta(seconds=window_sec)
    for slot, rt in run_times.items():
        if abs(now - rt) <= w:
            return slot
    return None


def run_ingestion_for_location(
    name: str, lat: float, lon: float,
    window_sec: int = 60,
    force: bool = False,
) -> None:
    loc = Location(name=name, lat=lat, lon=lon)

    slot = get_due_run_slot(loc, window_sec=window_sec)

    # if not forcing, only run when a slot is due
    if (slot is None) and (not force):
        return

    sql = WeatherSql(name)
    try:
        # forecast always when we run
        forecast_group = clean_data(loc)
        for k in sorted(forecast_group.keys()):
            sql.insert_forecast(forecast_group[k])

        # backcast only at run1 (or if you want it at startup too, see note below)
        if slot == 1:
            backcast = get_yesterday_data(loc)
            sql.insert_backcast(backcast)

        print(f"[{name}] ran (slot={slot}, force={force})")

    finally:
        sql.close()



def main() -> None:
    POINTS = [
        ("Yosemite_Horsetail",37.7291,-119.6285 ),
        ("Stanford", 37.4275, -122.1697),
        # ("Point2", lat2, lon2),
    ]

    for name, lat, lon in POINTS:
        run_ingestion_for_location(name, lat, lon, force=True)

    # then the normal schedule
    while True:
        for name, lat, lon in POINTS:
            run_ingestion_for_location(name, lat, lon, window_sec=60)
        time.sleep(30)


if __name__ == "__main__":
    main()
