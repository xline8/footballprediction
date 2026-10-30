"""Eksperimen: kalibrasi pasar turunan (O/U 2.5 & BTTS) — gerbang adopsi.

Pertanyaan (audit ronde 11): probabilitas turunan yang disajikan jalur
harian (p_over_dc / p_btts dari matriks Dixon-Coles, persis seperti
yang dipancarkan predict_upcoming) terukur under-predict gol pada
records walk-forward: bias -2,2 poin (O/U) dan -2,7 poin (BTTS) pooled
TOP5, D1 terburuk (-4,9 poin O/U), sementara 1X2 induknya tidak bias.
Apakah lapisan rekalibrasi turunan saja memperbaikinya di data
held-out?

Metode:
- Records skema v2 (records_cache.jsonl): p_over_dc/p_btts tersimpan
  persis seperti yang dihitung jalur prediksi, fthg/ftag tersimpan,
  jadi tidak ada join dan tidak ada rekonstruksi matriks.
- Bagian 1 mengukur ulang bias jalur yang disajikan (pooled + per
  divisi + pita probabilitas).
- Bagian 2 menguji kandidat pada split waktu yang sama dengan audit:
  fit pada date < 2023-07-01, uji pada date >= 2023-07-01.
  Kandidat: (a) Platt logistik pada logit(p), pooled; (b) isotonik
  (PAVA) pooled; (c) Platt per divisi.
- 1X2 tidak disentuh oleh konstruksi: kandidat hanya memetakan ulang
  probabilitas turunan.

Gerbang (ditentukan sebelum hasil dilihat): kandidat VALIDATED hanya
bila di data uji Brier membaik >= 0,001 pada KEDUA pasar DAN |bias|
pooled < 1 poin pada keduanya. Selain itu REJECTED.

Verdict: SEMUA KANDIDAT REJECTED oleh gerbang (run pertama pada
records skema v2). Bagian 1 mereproduksi pengukuran audit persis
(OU bias -0,0216 Brier 0,2433; BTTS -0,0279 Brier 0,2476; D1 OU
-0,0484). Tetapi pada era uji (>= 2023-07-01, n=5.650) bias mentah
sudah jauh lebih kecil (OU -0,0145; BTTS -0,0205) dan tidak ada
kandidat yang memperbaiki Brier >= 0,001 pada kedua pasar: Platt
pooled OU 0,2402 -> 0,2404 (bias terkoreksi ke +0,0032), BTTS
0,2449 -> 0,2444; isotonik OU datar dan biasnya overshoot (+0,0136);
Platt per divisi BTTS memburuk (0,2453). Bias per musim tidak stabil
(OU dari -0,045 di 2017/18 menyusut ke -0,002..-0,005 di
2024/25-2025/26, lalu -0,028 di 2023/24 dan -0,051 pada 2026/27
parsial n=394) — tidak ada konstanta koreksi yang bisa dipanen dari
data lama. Kesimpulan: jangan bangun lapisan rekalibrasi turunan
statis. Bila bias era terkini membesar lagi secara persisten,
kandidat yang sah untuk diuji adalah rekalibrasi walk-forward
bergulir (fit hanya pada musim-musim sebelumnya), yang harus
didaftarkan sebagai eksperimen baru dengan gerbangnya sendiri —
bukan dibaca dari eksperimen ini.

Run: .venv/bin/python experiments/experiment_deriv_calib.py
"""
import os
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest_picks import _fit_logistic, _logit, load_records  # noqa: E402
from football_etl import TOP5  # noqa: E402

SPLIT = "2023-07-01"


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def _brier(p, y):
    return float(np.mean((p - y) ** 2))


def _bias(p, y):
    return float(np.mean(p) - np.mean(y))


def _bands(p, y, label):
    edges = [0.0, 0.3, 0.4, 0.5, 0.6, 0.7, 1.01]
    print(f"  pita {label}:")
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi)
        if m.sum() >= 30:
            print(f"    {lo:.1f}-{min(hi, 1.0):.1f} n={int(m.sum()):>6,} "
                  f"mean_p={p[m].mean():.3f} freq={y[m].mean():.3f} "
                  f"selisih={y[m].mean() - p[m].mean():+.3f}")


def _isotonic_fit(x, y):
    """PAVA: kembalikan titik-titik (x terurut, nilai isotonik)."""
    order = np.argsort(x)
    xs, ys = x[order], y[order].astype(float)
    w = np.ones(len(ys))
    i = 0
    xs_l, ys_l, w_l = list(xs), list(ys), list(w)
    while i < len(ys_l) - 1:
        if ys_l[i] <= ys_l[i + 1]:
            i += 1
            continue
        tw = w_l[i] + w_l[i + 1]
        ys_l[i] = (ys_l[i] * w_l[i] + ys_l[i + 1] * w_l[i + 1]) / tw
        w_l[i] = tw
        del xs_l[i + 1], ys_l[i + 1], w_l[i + 1]
        if i > 0:
            i -= 1
    return np.array(xs_l), np.array(ys_l)


def _isotonic_apply(fit, x):
    xs, ys = fit
    return np.interp(x, xs, ys, left=ys[0], right=ys[-1])


def main():
    recs = [r for r in load_records()
            if r["div"] in TOP5 and r.get("fthg") is not None
            and r.get("p_over_dc") is not None]
    print(f"records TOP5 terpakai: {len(recs):,}")
    markets = {
        "OU2.5": (np.array([r["p_over_dc"] for r in recs]),
                  np.array([1.0 if r["fthg"] + r["ftag"] > 2 else 0.0
                            for r in recs])),
        "BTTS": (np.array([r["p_btts"] for r in recs]),
                 np.array([1.0 if r["fthg"] > 0 and r["ftag"] > 0 else 0.0
                           for r in recs])),
    }
    print("\n== Bagian 1: bias jalur yang disajikan (semua records) ==")
    for name, (p, y) in markets.items():
        print(f"{name}: mean_p={p.mean():.4f} freq={y.mean():.4f} "
              f"bias={_bias(p, y):+.4f} Brier={_brier(p, y):.4f}")
        _bands(p, y, name)
    by_div = defaultdict(list)
    for r in recs:
        by_div[r["div"]].append(r)
    for div in TOP5:
        rs = by_div[div]
        po = np.array([r["p_over_dc"] for r in rs])
        yo = np.array([1.0 if r["fthg"] + r["ftag"] > 2 else 0.0
                       for r in rs])
        pb = np.array([r["p_btts"] for r in rs])
        yb = np.array([1.0 if r["fthg"] > 0 and r["ftag"] > 0 else 0.0
                       for r in rs])
        print(f"  {div}: n={len(rs):,} OU bias={_bias(po, yo):+.4f} "
              f"BTTS bias={_bias(pb, yb):+.4f}")

    print("\n  bias per musim (deskriptif; pola era):")
    by_season = defaultdict(list)
    for r in recs:
        by_season[r["season"]].append(r)
    for season in sorted(by_season):
        rs = by_season[season]
        po = np.array([r["p_over_dc"] for r in rs])
        yo = np.array([1.0 if r["fthg"] + r["ftag"] > 2 else 0.0
                       for r in rs])
        pb = np.array([r["p_btts"] for r in rs])
        yb = np.array([1.0 if r["fthg"] > 0 and r["ftag"] > 0 else 0.0
                       for r in rs])
        print(f"    {season}: n={len(rs):,} OU bias={_bias(po, yo):+.4f} "
              f"BTTS bias={_bias(pb, yb):+.4f}")

    print(f"\n== Bagian 2: kandidat rekalibrasi (fit < {SPLIT}, "
          f"uji >= {SPLIT}) ==")
    tr = np.array([r["date"] < SPLIT for r in recs])
    te = ~tr
    divs = np.array([r["div"] for r in recs])
    verdicts = {}
    for name, (p, y) in markets.items():
        lp = _logit(p)
        # (a) Platt pooled
        w = _fit_logistic(lp[tr].reshape(-1, 1), y[tr])
        p_platt = _sigmoid(w[0] + w[1] * lp)
        # (b) isotonik pooled
        fit = _isotonic_fit(p[tr], y[tr])
        p_iso = _isotonic_apply(fit, p)
        # (c) Platt per divisi
        p_pd = p.copy()
        for div in TOP5:
            md = divs == div
            wd = _fit_logistic(lp[tr & md].reshape(-1, 1), y[tr & md])
            p_pd[md] = _sigmoid(wd[0] + wd[1] * lp[md])
        print(f"{name} (uji n={int(te.sum()):,}):")
        for label, pp in (("mentah", p), ("platt", p_platt),
                          ("isotonik", p_iso), ("platt-per-div", p_pd)):
            print(f"  {label:<14} Brier={_brier(pp[te], y[te]):.4f} "
                  f"bias={_bias(pp[te], y[te]):+.4f}")
        verdicts[name] = {
            k: (_brier(pp[te], y[te]), _bias(pp[te], y[te]))
            for k, pp in (("platt", p_platt), ("isotonik", p_iso),
                          ("platt-per-div", p_pd))}
        verdicts[name]["raw"] = (_brier(p[te], y[te]), _bias(p[te], y[te]))

    print("\n== Gerbang ==")
    for cand in ("platt", "isotonik", "platt-per-div"):
        ok = True
        for name in markets:
            d_brier = verdicts[name]["raw"][0] - verdicts[name][cand][0]
            if d_brier < 0.001 or abs(verdicts[name][cand][1]) >= 0.01:
                ok = False
        print(f"{cand}: {'VALIDATED' if ok else 'REJECTED'}")


if __name__ == "__main__":
    main()
