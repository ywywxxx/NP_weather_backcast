# src/find_similar_day/synthetic.py
from __future__ import annotations
import math
import numpy as np
from .schemas import SyntheticConfig, SyntheticDataset


def make_synthetic_dataset(cfg: SyntheticConfig) -> SyntheticDataset:
    """
    Synthetic analog of your real problem:
    - each target has a latent true state Z
    - observations X_obs are Z projected + small noise
    - forecasts are Z projected + larger noise
      early window noisier, late window less noisy
    """
    rng = np.random.default_rng(cfg.seed)
    N, D_true, D_feat, W = cfg.n_targets, cfg.D_true, cfg.D_feat, cfg.W

    Z = rng.normal(size=(N, D_true)).astype(np.float64)
    A = rng.normal(size=(D_true, D_feat)).astype(np.float64) / math.sqrt(D_true)
    base = Z @ A  # (N, D_feat)

    X_obs = base + cfg.noise_obs * rng.normal(size=(N, D_feat))

    def make_window(noise_level: float) -> np.ndarray:
        parts = []
        for j in range(W):
            slot_noise = noise_level * (1.0 + 0.15 * (W - 1 - j))
            parts.append(base + slot_noise * rng.normal(size=(N, D_feat)))
        return np.concatenate(parts, axis=1)  # (N, W*D_feat)

    Q_early = make_window(cfg.noise_fc_far)
    Q_late = make_window(cfg.noise_fc_near)

    # simple meta: 4 slots/day
    slots_per_day = 4
    days = np.arange(N) // slots_per_day
    slots = (np.arange(N) % slots_per_day) + 1
    meta = np.stack([days, slots], axis=1).astype(int)

    return SyntheticDataset(Q_early=Q_early, Q_late=Q_late, X_obs=X_obs, meta=meta)
