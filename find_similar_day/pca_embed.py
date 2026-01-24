# src/find_similar_day/pca_embed.py
from __future__ import annotations
import numpy as np


class PCAEmbed:
    """
    Minimal PCA embedding using SVD.

    Usage:
        pca = PCAEmbed(k=8, whiten=False)
        pca.fit(Q_train)           # e.g. Q_late
        Qk = pca.transform(Q)      # project any Q into k-dim
    """

    def __init__(self, k: int = 8, whiten: bool = False):
        self.k = int(k)
        self.whiten = bool(whiten)
        self.mean_: np.ndarray | None = None      # (1, D)
        self.Uk_: np.ndarray | None = None        # (D, k)
        self.Sk_: np.ndarray | None = None        # (k,)

    def fit(self, X: np.ndarray) -> "PCAEmbed":
        X = np.asarray(X, dtype=np.float64)
        if X.ndim != 2:
            raise ValueError(f"PCAEmbed.fit expects 2D array, got shape={X.shape}")

        self.mean_ = X.mean(axis=0, keepdims=True)
        Xc = X - self.mean_

        # SVD: Xc = U S Vt, columns of V are principal directions
        # Vt shape: (D, D) (or (min(N,D), D) if full_matrices=False)
        U, S, Vt = np.linalg.svd(Xc, full_matrices=False)

        k = min(self.k, Vt.shape[0])
        self.Uk_ = Vt[:k].T.copy()     # (D, k)
        self.Sk_ = S[:k].copy()        # (k,)

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.Uk_ is None:
            raise RuntimeError("PCAEmbed.transform called before fit().")

        X = np.asarray(X, dtype=np.float64)
        Xc = X - self.mean_
        Z = Xc @ self.Uk_   # (N, k)

        if self.whiten:
            # avoid division by 0
            Z = Z / (self.Sk_[None, :] + 1e-12)

        return Z

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)
