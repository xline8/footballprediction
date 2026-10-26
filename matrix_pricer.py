#!/usr/bin/env python3
"""matrix_pricer.py — Phase 13: scoreline matrix synthesis & derivative pricing.

Bangun matriks bivariate Poisson Dixon-Coles per match (lambda_h, lambda_a,
rho) lalu **meta-calibrasi**: region Home-Win / Draw / Away-Win diskalakan
proporsional agar jumlah prob 1X2 persis menyamai Meta Model 1.0012.

Dari matriks terkalibrasi diturunkan prob derivatif:
    - Over 2.5  = sum P(i,j) utk i+j > 2
    - Under 2.5 = 1 - Over
    - BTTS yes   = sum P(i,j) utk i>0 dan j>0
    - BTTS no    = 1 - BTTS yes

Engine murni (tanpa odds) — dipakai oleh backtest derivatif & live shadow.
"""

from __future__ import annotations

from football_etl import pois, tau

MAXG = 10
LINE = 2.5


def raw_matrix(lh, la, rho):
    """Matriks bivariate Poisson DC mentah (belum dinormalisasi penuh)."""
    return [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, rho)
             for y in range(MAXG + 1)] for x in range(MAXG + 1)]


_REGIONS = {
    "H": [(x, y) for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y],
    "D": [(x, x) for x in range(MAXG + 1)],
    "A": [(x, y) for x in range(MAXG + 1) for y in range(MAXG + 1) if x < y],
}


def calibrated_matrix(lh, la, rho, meta):
    """Skala tiap region agar sum 1X2 == meta probs (ph, pd, pa)."""
    m = raw_matrix(lh, la, rho)
    s = sum(sum(row) for row in m)
    if s <= 0:
        return None
    meta_d = {"H": meta[0], "D": meta[1], "A": meta[2]}
    f = {k: sum(m[x][y] for x, y in cells) / s for k, cells in _REGIONS.items()}
    M = [[0.0] * (MAXG + 1) for _ in range(MAXG + 1)]
    for k, cells in _REGIONS.items():
        scale = meta_d[k] / f[k] if f[k] > 0 else 0.0
        for x, y in cells:
            M[x][y] = m[x][y] / s * scale
    return M


def derivative_probs(M):
    """Dari matriks terkalibrasi: (over, under, btts_yes, btts_no)."""
    over = 0.0
    btts = 0.0
    for x in range(MAXG + 1):
        for y in range(MAXG + 1):
            p = M[x][y]
            if x + y > 2:
                over += p
            if x > 0 and y > 0:
                btts += p
    return (over, 1.0 - over, btts, 1.0 - btts)


def price(lh, la, rho, meta):
    """Satu baris: (over, under, btts_yes, btts_no)."""
    M = calibrated_matrix(lh, la, rho, meta)
    if M is None:
        return None
    return derivative_probs(M)


def _tf():
    """Self-check: 1X2 marginals menyamai meta & over+under==1, btts_pair==1."""
    meta = (0.46, 0.27, 0.27)
    out = price(1.5, 1.2, -0.07, meta)
    assert out is not None
    over, under, yes, no = out
    assert abs(over + under - 1.0) < 1e-12, (over + under)
    assert abs(yes + no - 1.0) < 1e-12, (yes + no)
    M = calibrated_matrix(1.5, 1.2, -0.07, meta)
    for k, cells in _REGIONS.items():
        region_sum = sum(M[x][y] for x, y in cells)
        idx = {"H": 0, "D": 1, "A": 2}[k]
        assert abs(region_sum - meta[idx]) < 1e-9, (k, region_sum, meta[idx])
    total = sum(sum(row) for row in M)
    assert abs(total - 1.0) < 1e-9, total
    print("matrix_pricer self-check OK:", f"over={over:.4f} under={under:.4f} "
          f"btts_yes={yes:.4f} btts_no={no:.4f}")


if __name__ == "__main__":
    _tf()
