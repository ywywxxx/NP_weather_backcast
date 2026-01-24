# src/find_similar_day/metric.py
from __future__ import annotations
import numpy as np


def softplus(x: np.ndarray) -> np.ndarray:
    x_clip = np.clip(x, -50, 50)
    return np.log1p(np.exp(x_clip))


def sigmoid(x: np.ndarray) -> np.ndarray:
    x_clip = np.clip(x, -50, 50)
    return 1.0 / (1.0 + np.exp(-x_clip))


def weighted_d2(Q: np.ndarray, q: np.ndarray, w: np.ndarray) -> np.ndarray:
    """
    Weighted squared distances from all rows in Q to vector q:
      d2[i] = sum_j w[j] * (Q[i,j] - q[j])^2
    """
    dif = Q - q[None, :]
    return np.sum(w * dif * dif, axis=1)


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """
    Minimal Spearman rank correlation (simple ranks; OK for our MVP).
    """
    assert x.shape == y.shape
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    rx -= rx.mean()
    ry -= ry.mean()
    denom = np.sqrt(np.sum(rx * rx) * np.sum(ry * ry))
    if denom == 0:
        return 0.0
    return float(np.sum(rx * ry) / denom)
