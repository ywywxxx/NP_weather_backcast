from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from location_info import Location
from NOAA_drive import get_raw_data
from summarize_rawdata import process_raw_data


def test_raw_pipeline_stanford():
    loc = Location(name="Stanford", lat=37.4275, lon=-122.1697)
    now_dt = datetime.now(ZoneInfo(loc.timezone))

    # 这一步拿到的 JSON 已经包含 skyCover/snowLevel/... 等字段
    gridpoints_json = get_raw_data(loc)

    # 直接喂给 process_raw_data
    out = process_raw_data(gridpoints_json, location=loc, now_dt=now_dt)

    keys = sorted(out.keys())
    print(f"Total groups: {len(keys)}")

    for k in keys[:10]:
        row = out[k]
        print(
            "key=", row["group_key"],
            " skyCover_mean=", row.get("skyCover_mean"),
            " snowLevel_mean=", row.get("snowLevel_mean"),
            " snowfallAmount_sum=", row.get("snowfallAmount_sum"),
            " quantitativePrecipitation_sum=", row.get("quantitativePrecipitation_sum"),
            " iceAccumulation_sum=", row.get("iceAccumulation_sum"),
        )


if __name__ == "__main__":
    test_raw_pipeline_stanford()
