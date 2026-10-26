#!/usr/bin/env python3
"""verify_significance.py — Bootstrap/Monte Carlo test untuk Policy 9.4.

Null: ROI <= 0%. Bootstrap 10,000 resample (with replacement) dari log bet
9.4 murni (stake dinamis = 0.25*composite). p-value = fraksi resample dgn ROI<=0.
Jika p < 0.05 -> 9.4 bukan noise (dapat longgarkan gate N>=1000).
"""

import numpy as np

from policy_overlay import (BASELINE_KELLY, build_maps, candidates,
                            composite_score, load_records, RECORDS)

N_BOOT = 10_000
SEED = 0


def build_94_bets():
    records = load_records(RECORDS)
    fmap, smap = build_maps()
    bets = []
    for b in candidates(records, fmap, smap):
        sc = composite_score(b)
        stake = BASELINE_KELLY * sc
        if stake <= 0.0:
            continue
        od = b["od"]
        profit = (stake * (od - 1.0)) if b["win"] else -stake
        bets.append((stake, profit))
    return bets


def roi(bets):
    s = sum(x[0] for x in bets)
    p = sum(x[1] for x in bets)
    return p / s if s else 0.0


def bootstrap_test(bets, n=N_BOOT, seed=SEED):
    rng = np.random.default_rng(seed)
    arr = np.asarray(bets, dtype=float)
    stakes, profits = arr[:, 0], arr[:, 1]
    m = len(bets)
    obs = roi(bets)
    le0 = 0
    n_nonzero = 0
    for _ in range(n):
        idx = rng.integers(0, m, size=m)
        s = stakes[idx].sum()
        if s <= 0:
            continue
        n_nonzero += 1
        r = profits[idx].sum() / s
        if r <= 0.0:
            le0 += 1
    p = le0 / n_nonzero if n_nonzero else 1.0
    # CI bootstrap (percentile)
    rs = np.empty(n)
    for i in range(n):
        idx = rng.integers(0, m, size=m)
        s = stakes[idx].sum()
        rs[i] = profits[idx].sum() / s if s else 0.0
    lo, hi = np.percentile(rs, [2.5, 97.5])
    return {"n_bets": m, "roi": obs, "p_value": float(p),
            "ci95": (float(lo), float(hi)), "boot_mean": float(rs.mean())}


def main():
    bets = build_94_bets()
    res = bootstrap_test(bets)
    print("=" * 66)
    print("POLICY 9.4 — BOOTSTRAP SIGNIFICANCE TEST")
    print("=" * 66)
    print(f"n bets            : {res['n_bets']}")
    print(f"ROI (weighted)    : {res['roi']:+.4%}")
    print(f"bootstrap mean     : {res['boot_mean']:+.4%}")
    print(f"CI 95% (percentile): [{res['ci95'][0]:+.4%}, {res['ci95'][1]:+.4%}]")
    print(f"p-value vs H0 ROI<=0: {res['p_value']:.4f}")
    verdict = "SIGNIFIKAN (p<0.05)" if res["p_value"] < 0.05 else "TIDAK signifikan"
    print(f"verdict            : {verdict}")
    return res


if __name__ == "__main__":
    main()
