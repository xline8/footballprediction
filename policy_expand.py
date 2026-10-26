#!/usr/bin/env python3
"""policy_expand.py — Phase 10 Step 2: ekspansi high-context pool utk Policy 9.4.

Skor ekspansi = w1*despo_exp + w2*fatigue_norm + w3*cont(proximity EC) + w4*riv(h2h).
Target: N >= 800, yield > +4.5%, stabil >= 3/5 tahun (2021-2025).
Stake = 0.25 * score_exp (dynamic contextual Kelly), theta = skor minimum.
"""

from collections import defaultdict

from policy_overlay import (BASELINE_KELLY, YEARS, build_expanded_maps,
                            build_maps, candidates, composite_exp, load_records,
                            RECORDS)

WEIGHTS = [
    (0.6, 0.4, 0.0, 0.0),
    (0.5, 0.3, 0.0, 0.2),
    (0.5, 0.25, 0.0, 0.25),
    (0.45, 0.35, 0.0, 0.2),
    (0.4, 0.3, 0.0, 0.3),
    (0.4, 0.2, 0.0, 0.4),
    (0.35, 0.25, 0.0, 0.4),
    (0.3, 0.3, 0.0, 0.4),
]


def sweep(theta=0.0):
    records = load_records(RECORDS)
    fmap, smap = build_maps()
    cpmap, rmap = build_expanded_maps()
    bets = list(candidates(records, fmap, smap, cpmap=cpmap, rmap=rmap))
    print(f"kandidat edge>0.05: n={len(bets)}")
    print(f"{'w1':>4} {'w2':>4} {'w3':>4} {'w4':>4} {'theta':>5} "
          f"{'N':>6} {'yield':>9} {'stable':>6}")
    for w in WEIGHTS:
        out = []
        for b in bets:
            sc = composite_exp(b, w)
            stake = BASELINE_KELLY * sc
            if stake <= 0.0 or sc < theta:
                continue
            od = b["od"]
            profit = (stake * (od - 1.0)) if b["win"] else -stake
            out.append((stake, profit, b["year"]))
        staked = sum(s for s, _, _ in out)
        profit = sum(p for _, p, _ in out)
        yl = profit / staked if staked else 0.0
        yr = defaultdict(lambda: [0.0, 0.0])
        for s, p, y in out:
            yr[y][0] += s
            yr[y][1] += p
        yrs = {y: (p / s if s else 0.0) for y, (s, p) in yr.items()}
        stable = sum(1 for y in YEARS if yrs.get(y, 0.0) > 0.0)
        flag = ""
        if len(out) >= 800 and yl > 0.045 and stable >= 3:
            flag = "  <<< HIT"
        print(f"{w[0]:>4} {w[1]:>4} {w[2]:>4} {w[3]:>4} {theta:>5} "
              f"{len(out):>6} {yl:>+9.4%} {stable:>6}/5{flag}")


if __name__ == "__main__":
    import sys
    sweep(float(sys.argv[1]) if len(sys.argv) > 1 else 0.0)
