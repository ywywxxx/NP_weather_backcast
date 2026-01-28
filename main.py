from summarize_forecast import clean_forecast
from summarize_rawdata import clean_raw
from location_info import Location

def clean_data(location, now_dt=None):
    fc = clean_forecast(location, now_dt=now_dt)
    rw = clean_raw(location, now_dt=now_dt)

    out = {}
    for k in (set(fc.keys()) & set(rw.keys())):
        merged = {"group_key": k}

        # forecast features（保留 n）
        for kk, vv in fc[k].items():
            if kk != "group_key":
                merged[kk] = vv

        # raw features
        for kk, vv in rw[k].items():
            if kk != "group_key":
                merged[kk] = vv

        out[k] = merged

    return out


if __name__ == "__main__":
# test:
    loc = Location(
        name="Stanford",
        lat=37.4275,
        lon=-122.1697,
    )

    merged_by_group = clean_data(loc)
    for k in sorted(merged_by_group.keys()):
        print(k, merged_by_group[k])

