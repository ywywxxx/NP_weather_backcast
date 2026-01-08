from __future__ import annotations

from typing import Dict, Any, List, Tuple, Optional

from checktime import group_by_index


# ---------------------------
# 2) 桶内聚合：从 records 里抽 value -> mean/sum
# ---------------------------

def _agg_values(records: List[Dict[str, Any]], agg: str) -> Optional[float]:
    """
    records: NOAA raw/grid 的 values list，每条一般有 {"validTime": ".../PT1H", "value": ...}
    agg: "mean" or "sum"
    return: float or None
    """
    vals: List[float] = []
    for r in records:
        v = r.get("value", None)
        if v is None:
            continue
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            continue

    if not vals:
        return None

    if agg == "mean":
        return sum(vals) / len(vals)
    if agg == "sum":
        return sum(vals)

    raise ValueError(f"Unsupported agg={agg}")


def summarize_raw_group(raw_group: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    raw_group: dict[field] -> list[records]，这些 records 已经保证属于同一个 group key
    输出：5 个 feature（存在就算；缺字段则该 feature 不出现 或者为 None 取决于你怎么写）
    """
    out: Dict[str, Any] = {}

    if "skyCover" in raw_group:
        out["skyCover_mean"] = _agg_values(raw_group["skyCover"], agg="mean")
    if "snowLevel" in raw_group:
        out["snowLevel_mean"] = _agg_values(raw_group["snowLevel"], agg="mean")
    if "snowfallAmount" in raw_group:
        out["snowfallAmount_sum"] = _agg_values(raw_group["snowfallAmount"], agg="sum")
    if "quantitativePrecipitation" in raw_group:
        out["quantitativePrecipitation_sum"] = _agg_values(raw_group["quantitativePrecipitation"], agg="sum")
    if "iceAccumulation" in raw_group:
        out["iceAccumulation_sum"] = _agg_values(raw_group["iceAccumulation"], agg="sum")

    return out


# ---------------------------
# 3) 全局处理：对整条 raw JSON 先分组，再对齐 key，再输出 key + features
# ---------------------------

RAW_FIELDS = [
    "skyCover",
    "snowLevel",
    "snowfallAmount",
    "quantitativePrecipitation",
    "iceAccumulation",
]


def process_raw_data(raw_data_json: Dict[str, Any], location, now_dt) -> Dict[Tuple[int, int, int, int], Dict[str, Any]]:
    """
    raw_data_json: NOAA raw/grid JSON（常见：forecastGridData）
      期望结构：raw_data_json["properties"][field]["values"] 是 record list
    location, now_dt: 传给 group_by_index（你原函数会用 time2index）

    return:
      dict[group_key] -> {
        "group_key": group_key,
        5 features...
      }

    group_key = (d_now, idx_now, d_pred, idx_pred)
    """
    props = raw_data_json.get("properties", {})

    # per_field_groups[field][group_key] = [records...]
    per_field_groups: Dict[str, Dict[Tuple[int, int, int, int], List[Dict[str, Any]]]] = {}
    all_keys = set()

    # A) 每个字段分别分组
    for field in RAW_FIELDS:
        node = props.get(field)
        if not node:
            continue

        values = node.get("values", [])
        if not values:
            continue

        groups = group_by_index(values, time_key="validTime", location=location, now_dt=now_dt)
        per_field_groups[field] = groups
        all_keys.update(groups.keys())

    # B) 按 group_key 对齐五个字段，组装 raw_group，再做聚合
    out: Dict[Tuple[int, int, int, int], Dict[str, Any]] = {}

    for key in all_keys:
        raw_group: Dict[str, List[Dict[str, Any]]] = {}
        for field in RAW_FIELDS:
            g = per_field_groups.get(field)
            if g and key in g:
                raw_group[field] = g[key]

        feats = summarize_raw_group(raw_group)
        out[key] = {"group_key": key, **feats}

    return out


# features_by_group = process_raw_data(raw_json, location=loc, now_dt=now_dt)
# # features_by_group[(d_now, idx_now, d_pred, idx_pred)] -> dict


