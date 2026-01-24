# src/find_similar_day/schemas.py
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class SyntheticConfig:
    n_targets: int = 300
    D_true: int = 8
    D_feat: int = 10
    W: int = 3
    noise_obs: float = 0.35
    noise_fc_far: float = 1.25
    noise_fc_near: float = 0.65
    seed: int = 7


@dataclass(frozen=True)
class SyntheticDataset:
    Q_early: np.ndarray   # (N, W*D_feat)
    Q_late: np.ndarray    # (N, W*D_feat)
    X_obs: np.ndarray     # (N, D_feat)
    meta: np.ndarray      # (N, 2) e.g. [day_index, slot_index]
