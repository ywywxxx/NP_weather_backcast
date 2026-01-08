from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from location_info import Location
from NOAA_drive import get_hourly_forecast
from summarize_forecast import summarize_hourly_forecast  # 假设你把函数放在 summarize_hourly.py 里
from checktime import group_by_index            # 你之前的 group_by_index


def test_summarize_hourly_forecast_one_group():
    loc = Location(name="Stanford", lat=37.4275, lon=-122.1697)

    now_dt = datetime.now(ZoneInfo(loc.timezone))

    hourly_json = get_hourly_forecast(loc)
    periods = hourly_json["properties"]["periods"]

    # 按你的规则分组：四个输出都一致才算同一组
    groups = group_by_index(periods, time_key="startTime", location=loc, now_dt=now_dt)

    print(f"Total hourly groups: {len(groups)}")

    # 选一个最早的 group 来测（也可以改成随机）
    keys = sorted(groups.keys())
    key0 = keys[0]
    recs = groups[key0]

    print("Test group key =", key0)
    print("Group size =", len(recs))
    print("First 3 shortForecasts in this group:")
    for r in recs[:3]:
        print("  -", r.get("startTime"), "|", r.get("shortForecast"))

    feats = summarize_hourly_forecast(recs)
    print("\nSummarized features:")
    for k, v in feats.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    test_summarize_hourly_forecast_one_group()
