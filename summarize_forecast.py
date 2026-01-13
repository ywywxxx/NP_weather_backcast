from __future__ import annotations
from collections import Counter
import numpy as np


from datetime import datetime
from zoneinfo import ZoneInfo
from location_info import Location
from NOAA_drive import get_hourly_forecast
from checktime import group_by_index    



"""
records: come from same index group
return: dict of features
"""

def summarize_hourly_forecast(records):
    if not records:
        return {}

    snow_words = ["snow", "flurr", "sleet", "wintry", "blizzard"]
    rain_words = ["rain", "shower", "drizzle", "thunderstorm"]

    temps_c = []
    precip_probs = []
    winds_kmh = []
    wind_dirs = []
    short_fc = []

    has_rain = 0
    has_snow = 0

    for r in records:
        # temperature: F -> C
        temp_f = r.get("temperature")
        if temp_f is not None:
            temps_c.append((temp_f - 32) * 5 / 9)

        # precip probability: None -> 0
        pop = r.get("probabilityOfPrecipitation", {}).get("value")
        precip_probs.append(0.0 if pop is None else float(pop))

        # windSpeed: '7 mph' / '5 to 10 mph' -> take the first number
        ws = r.get("windSpeed")
        if ws:
            for p in str(ws).split():
                try:
                    winds_kmh.append(float(p) * 1.60934)
                    break
                except ValueError:
                    continue

        wd = r.get("windDirection")
        if wd is not None:
            wind_dirs.append(wd)

        sf = r.get("shortForecast")
        if sf is not None:
            short_fc.append(sf)

            s = str(sf).lower()
            if any(w in s for w in snow_words):
                has_snow = 1
            if any(w in s for w in rain_words):
                has_rain = 1

            if has_snow and has_rain:
                # 两个都已经命中，没必要继续扫更多文本
                pass

    def mode_or_none(xs):
        xs = [x for x in xs if x is not None]
        return Counter(xs).most_common(1)[0][0] if xs else None

    out = {
        "has_rain": has_rain,
        "has_snow": has_snow,
        "temp_C_mean": float(np.mean(temps_c)) if temps_c else None,
        "temp_C_min": float(np.min(temps_c)) if temps_c else None,
        "temp_C_max": float(np.max(temps_c)) if temps_c else None,
        "precip_prob_max": float(np.max(precip_probs)) if precip_probs else None,
        "wind_kmh_mean": float(np.mean(winds_kmh)) if winds_kmh else None,
        "wind_dir_mode": mode_or_none(wind_dirs),
        "shortForecast_mode": mode_or_none(short_fc),
    }
    return out




def clean_forecast(location: Location, now_dt=None):
    if now_dt is None:
        now_dt = datetime.now(ZoneInfo(location.timezone))

    hourly_json = get_hourly_forecast(location)
    periods = hourly_json["properties"]["periods"]

    groups = group_by_index(periods, time_key="startTime", location=location, now_dt=now_dt)

    out = {}
    for key, recs in groups.items():
        feats = summarize_hourly_forecast(recs)
        out[key] = {"group_key": key, **feats}

    return out

# # test:
# loc = Location(
#     name="Stanford",
#     lat=37.4275,
#     lon=-122.1697,
# )

# forecast_by_group = clean_forecast(loc)
# for k in sorted(forecast_by_group.keys())[:3]:
#     print(k, forecast_by_group[k])
