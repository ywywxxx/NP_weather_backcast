# src/find_similar_day/train.py
from __future__ import annotations
import numpy as np
from .metric import softplus, sigmoid


def init_u(dim: int, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    u = rng.normal(scale=0.01, size=(dim,)).astype(np.float64)
    u += 0.8  # so softplus(u) ~ around 1
    return u


def sample_triples_by_truth(X_obs: np.ndarray, n_triples: int, seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Triplets (t, pos, neg): pos is closer to t than neg in observation space.
    """
    rng = np.random.default_rng(seed)
    N = X_obs.shape[0]
    t_idx = rng.integers(0, N, size=(n_triples,), dtype=np.int64)
    pos_idx = np.empty_like(t_idx)
    neg_idx = np.empty_like(t_idx)

    pool_size = 40
    for i, t in enumerate(t_idx):
        pool = rng.integers(0, N, size=(pool_size,), dtype=np.int64)
        pool = pool[pool != t]
        if pool.size < 2:
            pool = np.array([(t + 1) % N, (t + 2) % N], dtype=np.int64)
        d = np.linalg.norm(X_obs[pool] - X_obs[t], axis=1)
        pos_idx[i] = pool[int(np.argmin(d))]
        neg_idx[i] = pool[int(np.argmax(d))]

    return t_idx, pos_idx, neg_idx


def train_weights_triplet(Q: np.ndarray, X_obs: np.ndarray,
                          steps: int = 600, lr: float = 0.08, margin: float = 0.6,
                          triples_per_step: int = 256, seed: int = 0) -> np.ndarray:
    """
    Learn w >= 0 in weighted L2 on signature space, using hinge triplet loss:
      L = max(0, margin + d(t,pos) - d(t,neg))
    w = softplus(u)
    """
    rng = np.random.default_rng(seed)
    dim = Q.shape[1]
    u = init_u(dim, seed=seed)
    eps = 1e-8

    for step in range(steps):
        t, p, n = sample_triples_by_truth(X_obs, n_triples=triples_per_step, seed=int(rng.integers(0, 1_000_000)))

        w = softplus(u)
        dw_du = sigmoid(u)

        Qt, Qp, Qn = Q[t], Q[p], Q[n]
        dp2 = np.sum(w * (Qt - Qp) ** 2, axis=1)
        dn2 = np.sum(w * (Qt - Qn) ** 2, axis=1)
        dp = np.sqrt(dp2 + eps)
        dn = np.sqrt(dn2 + eps)

        hinge = margin + dp - dn
        active = hinge > 0
        if not np.any(active):
            if (step + 1) % 100 == 0:
                print(f"[step {step+1}] loss=0 (no active triplets)")
            continue

        # grad_w for one sample:
        # 0.5 * ( (Qt-Qp)^2 / dp - (Qt-Qn)^2 / dn )
        d_tp = (Qt - Qp) ** 2
        d_tn = (Qt - Qn) ** 2
        act = active.astype(np.float64)[:, None]
        grad_w = 0.5 * np.mean(act * (d_tp / dp[:, None] - d_tn / dn[:, None]), axis=0)

        grad_u = grad_w * dw_du
        u = u - lr * grad_u

        if (step + 1) % 100 == 0:
            print(f"[step {step+1}] loss={float(np.mean(np.maximum(0.0, hinge))):.4f}")

    w = softplus(u)
    # normalize for readability
    w = w / (np.mean(w) + 1e-12)
    return w
