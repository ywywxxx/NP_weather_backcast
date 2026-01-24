# src/find_similar_day/retrieval.py
from __future__ import annotations
import numpy as np
from .metric import weighted_d2


def topk_neighbors(Q: np.ndarray, w: np.ndarray, t: int, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """
    Return (indices, distances) for top-k nearest neighbors to row t (excluding itself).
    """
    d2 = weighted_d2(Q, Q[t], w)
    d2[t] = np.inf
    idx = np.argsort(d2)[:k]
    return idx, np.sqrt(d2[idx])
