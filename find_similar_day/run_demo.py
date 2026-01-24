# src/find_similar_day/run_demo.py
from __future__ import annotations
import numpy as np
from .schemas import SyntheticConfig
from .synthetic import make_synthetic_dataset
from .train import train_weights_triplet
from .metrics import truth_transfer, rank_stability


def main():
    cfg = SyntheticConfig(
        n_targets=300,
        D_true=8,
        D_feat=10,
        W=3,
        noise_obs=0.35,
        noise_fc_far=1.25,
        noise_fc_near=0.65,
        seed=7,
    )
    ds = make_synthetic_dataset(cfg)

    dim = ds.Q_late.shape[1]
    w0 = np.ones((dim,), dtype=np.float64)

    print("=== BEFORE TRAINING (uniform weights) ===")
    tt0 = truth_transfer(ds.Q_late, ds.X_obs, w0)
    rs0 = rank_stability(ds.Q_early, ds.Q_late, w0)
    print("TruthTransfer (late signatures):", tt0)
    print("RankStability (early vs late): ", rs0)

    print("\n=== TRAINING (on late signatures; triplet loss from truth) ===")
    w = train_weights_triplet(ds.Q_late, ds.X_obs, steps=600, lr=0.08, margin=0.6, triples_per_step=256, seed=0)

    print("\n=== AFTER TRAINING ===s")
    tt1 = truth_transfer(ds.Q_late, ds.X_obs, w)
    rs1 = rank_stability(ds.Q_early, ds.Q_late, w)
    print("TruthTransfer (late signatures):", tt1)
    print("RankStability (early vs late): ", rs1)

    top = np.argsort(-w)[:10]
    print("\nTop-10 weight dims (index: weight):")
    for i in top:
        print(f"  {int(i):4d}: {w[i]:.4f}")


if __name__ == "__main__":
    main()
