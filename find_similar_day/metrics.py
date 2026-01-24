# src/find_similar_day/metrics.py
from __future__ import annotations
import numpy as np
from .retrieval import topk_neighbors
from .metric import spearman_rho, weighted_d2


def truth_transfer(Q: np.ndarray, X_obs: np.ndarray, w: np.ndarray, k: int = 5, n_eval: int = 150, seed: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    N = Q.shape[0]
    picks = rng.integers(0, N, size=(n_eval,), dtype=np.int64)

    top1 = []
    bestk = []
    for t in picks:
        nn_idx, _ = topk_neighbors(Q, w, int(t), k=k)
        d_true = np.linalg.norm(X_obs[nn_idx] - X_obs[t], axis=1)
        top1.append(float(d_true[0]))
        bestk.append(float(np.min(d_true)))

    return {
        "top1_true_dist_mean": float(np.mean(top1)),
        "bestk_true_dist_mean": float(np.mean(bestk)),
        "top1_true_dist_median": float(np.median(top1)),
        "bestk_true_dist_median": float(np.median(bestk)),
    }


def rank_stability(Q_early: np.ndarray, Q_late: np.ndarray, w: np.ndarray,
                  k_overlap: int = 20, n_eval: int = 80, candidate_pool: int = 150, seed: int = 2) -> dict:
    rng = np.random.default_rng(seed)
    N = Q_early.shape[0]
    picks = rng.integers(0, N, size=(n_eval,), dtype=np.int64)

    rhos = []
    overlaps = []

    for t in picks:
        cand = rng.integers(0, N, size=(candidate_pool,), dtype=np.int64)
        cand = cand[cand != t]
        if cand.size < 10:
            continue

        dE = weighted_d2(Q_early[cand], Q_early[t], w)
        dL = weighted_d2(Q_late[cand], Q_late[t], w)

        rhos.append(spearman_rho(dE, dL))

        topE = cand[np.argsort(dE)[:k_overlap]]
        topL = cand[np.argsort(dL)[:k_overlap]]
        overlaps.append(len(set(topE.tolist()).intersection(set(topL.tolist()))) / float(k_overlap))

    return {
        "spearman_rho_mean": float(np.mean(rhos)) if rhos else 0.0,
        "topk_overlap_mean": float(np.mean(overlaps)) if overlaps else 0.0,
    }
