#!/usr/bin/env python3
"""feature_analysis.py — evaluasi awal fitur (eksperimental).

Menjalankan fitur anti-leakage (features.build_feature_rows) dan melaporkan
kekuatan prediktif univariat tiap fitur terhadap outcome (home-win & total gol)
menggunakan korelasi point-biserial / Pearson. Ini membantu memprioritaskan
fitur mana yang layak diintegrasikan ke model — belum termasuk kesimpulan
tentang keuntungan marjinal setelah model retun.

Usage:  python feature_analysis.py [limit]
"""

import sys

import numpy as np

from features import build_feature_rows

NUM_FEATS = [
    "elo_diff", "form_pts_h", "form_pts_a",
    "goals_diff_h", "goals_diff_a",
    "xg_diff_h", "xg_diff_a", "rest_h", "rest_a",
    "n_played_h", "n_played_a",
]


def _r(x, y):
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 3 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    rows = build_feature_rows(limit=limit)
    n = len(rows)
    print(f"baris fitur: {n:,}")

    home_win = np.array([1.0 if r["ftr"] == "H" else 0.0 for r in rows])
    total_goals = np.array([(r["yh"] or 0) + (r["ya"] or 0) for r in rows])

    print(f"\n{'fitur':<16}{'r(home-win)':>12}{'r(total gol)':>13}")
    print("-" * 42)
    results = []
    for feat in NUM_FEATS:
        x = np.array([r.get(feat) for r in rows], dtype=float)
        rh = _r(x, home_win)
        rt = _r(x, total_goals)
        results.append((feat, rh, rt))
        print(f"{feat:<16}{rh:>12.3f}{rt:>13.3f}")

    print("\nTop fitur untuk home-win (|r|):")
    for feat, rh, rt in sorted(results, key=lambda t: -abs(t[1]))[:5]:
        print(f"  {feat:<16} r={rh:+.3f}")
    print("\nTop fitur untuk total gol (|r|):")
    for feat, rh, rt in sorted(results, key=lambda t: -abs(t[2]))[:5]:
        print(f"  {feat:<16} r={rt:+.3f}")


if __name__ == "__main__":
    main()
