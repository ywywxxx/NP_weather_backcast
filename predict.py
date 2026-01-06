import os
import requests
from time import sleep

from zoneinfo import ZoneInfo
from astral import LocationInfo
from astral.sun import sun
from datetime import datetime, time, date, timedelta

import os
import requests
import matplotlib.dates as mdates
from time import sleep
from dateutil import parser
from dotenv import load_dotenv
import json

import numpy as np
from collections import defaultdict, Counter
import math

import drive

class WeatherPipeline:

    def __init__(self, *, drive, lat, lon, tzone, user_agent=None):
        self.drive = drive              
        self.lat = lat
        self.lon = lon
        self.tzone = tzone
        self.user_agent = user_agent or {"User-Agent": "Pikachu"}

    # ---------- utils ----------
    @staticmethod
    def _mode_or_none(values):
        vals = [v for v in values if v is not None]
        if not vals:
            return None
        return Counter(vals).most_common(1)[0][0]

    @staticmethod
    def _mph_text_to_kmh(wind_speed_text):
        # '7 mph' / '5 to 10 mph' -> 取第一个数字 * 1.60934
        if wind_speed_text is None:
            return None
        parts = str(wind_speed_text).split()
        for p in parts:
            try:
                return float(p) * 1.60934
            except ValueError:
                continue
        return None

    @staticmethod
    def _f_to_c(f):
        return (f - 32) * 5 / 9

    # ---------- 获取数据 ----------
    def fetch(self):
        raw = self.drive.getOriginalData(self.lat, self.lon, self.user_agent)
        hourlyForecast = self.drive.getHourlyForecast(self.lat, self.lon, self.user_agent)
        return raw, hourlyForecast

    # ---------- 1) forecast: periods -> grouped ----------
    def build_grouped_forecast(self, hourlyForecast):
        groups = defaultdict(list)

        for hour in hourlyForecast["properties"]["periods"]:
            dt = datetime.fromisoformat(hour["startTime"])  # aware
            d_local, idx = self.drive.time_to_date_index(dt, self.lat, self.lon, self.tzone)

            temp_c = self._f_to_c(hour["temperature"])
            pop = hour.get("probabilityOfPrecipitation", {}).get("value", None)
            wind_kmh = self._mph_text_to_kmh(hour.get("windSpeed"))
            wind_dir = hour.get("windDirection", None)
            short_fc = hour.get("shortForecast", None)

            groups[(d_local, idx)].append({
                "startTime": dt.astimezone(self.tzone),
                "temp_C": temp_c,
                "pop": pop,
                "wind_kmh": wind_kmh,
                "wind_dir": wind_dir,
                "shortForecast": short_fc,
            })

        grouped = []
        for (d_local, idx), items in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1])):
            temps = np.array([it["temp_C"] for it in items], dtype=float)
            pops = np.array([np.nan if it["pop"] is None else float(it["pop"]) for it in items], dtype=float)
            winds = np.array([np.nan if it["wind_kmh"] is None else float(it["wind_kmh"]) for it in items], dtype=float)

            start_time = min(it["startTime"] for it in items)
            end_time = max(it["startTime"] for it in items) + timedelta(hours=1)

            grouped.append({
                "date": d_local,
                "index": idx,
                "n_hours": len(items),
                "start_time": start_time,
                "end_time": end_time,

                "temp_C_mean": float(np.nanmean(temps)) if temps.size else None,
                "temp_C_min": float(np.nanmin(temps)) if temps.size else None,
                "temp_C_max": float(np.nanmax(temps)) if temps.size else None,

                "pop_max": float(np.nanmax(pops)) if pops.size and not np.all(np.isnan(pops)) else None,
                "wind_kmh_mean": float(np.nanmean(winds)) if winds.size and not np.all(np.isnan(winds)) else None,

                "wind_dir_mode": self._mode_or_none([it["wind_dir"] for it in items]),
                "shortForecast_mode": self._mode_or_none([it["shortForecast"] for it in items]),
            })

        return grouped

    # ---------- 2) raw.values -> grouped_field（键名就是 field_name，不拼 _mean/_sum） ----------
    def build_grouped_from_values(self, values, field_name, agg="mean"):
        groups = defaultdict(list)

        for hour in values:
            dt = datetime.fromisoformat(hour["validTime"].split("/")[0])  # aware(UTC)
            d_local, idx = self.drive.time_to_date_index(dt, self.lat, self.lon, self.tzone)

            groups[(d_local, idx)].append({
                "startTime": dt.astimezone(self.tzone),
                "value": hour.get("value", None)
            })

        grouped = []
        for (d_local, idx), items in sorted(groups.items(), key=lambda x: (x[0][0], x[0][1])):
            vals = np.array(
                [np.nan if it["value"] is None else float(it["value"]) for it in items],
                dtype=float
            )

            start_time = min(it["startTime"] for it in items)
            end_time = max(it["startTime"] for it in items) + timedelta(hours=1)

            if vals.size == 0 or np.all(np.isnan(vals)):
                stat = None
            else:
                if agg == "mean":
                    stat = float(np.nanmean(vals))
                elif agg == "sum":
                    stat = float(np.nansum(vals))
                else:
                    raise ValueError(f"agg must be 'mean' or 'sum', got {agg!r}")

            grouped.append({
                "date": d_local,
                "index": idx,
                "n_hours": len(items),
                "start_time": start_time,
                "end_time": end_time,
                field_name: stat,
            })

        return grouped

    # ---------- 3) merge ----------
    @staticmethod
    def _value_map(grouped_list, field_name):
        return {(r["date"], r["index"]): r.get(field_name, None) for r in grouped_list}

    def merge_field(self, grouped_forecast, grouped_field, field_name):
        m = self._value_map(grouped_field, field_name)
        for row in grouped_forecast:
            key = (row["date"], row["index"])
            row[field_name] = m.get(key, None)


    def run(self):
        raw, hourlyForecast = self.fetch()

        grouped = self.build_grouped_forecast(hourlyForecast)

        grouped_skyCover = self.build_grouped_from_values(
            raw["properties"]["skyCover"]["values"], "skyCover", agg="mean"
        )
        grouped_snowLevel = self.build_grouped_from_values(
            raw["properties"]["snowLevel"]["values"], "snowLevel", agg="mean"
        )
        grouped_snowfallAmount = self.build_grouped_from_values(
            raw["properties"]["snowfallAmount"]["values"], "snowfallAmount", agg="sum"
        )
        grouped_quantitativePrecipitation = self.build_grouped_from_values(
            raw["properties"]["quantitativePrecipitation"]["values"], "quantitativePrecipitation", agg="sum"
        )
        grouped_iceAccumulation = self.build_grouped_from_values(
            raw["properties"]["iceAccumulation"]["values"], "iceAccumulation", agg="mean"
        )

        self.merge_field(grouped, grouped_skyCover, "skyCover")
        self.merge_field(grouped, grouped_snowLevel, "snowLevel")
        self.merge_field(grouped, grouped_snowfallAmount, "snowfallAmount")
        self.merge_field(grouped, grouped_quantitativePrecipitation, "quantitativePrecipitation")
        self.merge_field(grouped, grouped_iceAccumulation, "iceAccumulation")

        return grouped
