#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
backtest_value.py -- Value-bet backtest flat-stake dari predictions_v2.csv
kepada closing odds DESIMAL ASLI (margin inclusive) dari all_matches_clean.csv.

Aturan disiplin:
- Signal = prob model MURNI (ph_dc/pd_dc/pa_dc, p_over_dc, p_ah_home) -- BUKAN blended.
- Payout = odds closing asli (PSCH/PSCD/PSCA, AvgC>2.5, AvgCAHH), BUKAN dari prob decoded.
- Edge_k = p_model_k - 1/odds_k_asli; bet saat edge > threshold (grid 0.00/0.01/0.03/0.05/0.08).
- Flat stake 1 unit. 1X2: satu bet per sisi terpilih (H/D/A independen).
  O/U: Only over side. AH: sisi home; push = refund (lapor versi excl-push & incl-push).
- Settlement AH support quarter-line (half win / half loss).

Output: value_bets.csv (union semua pool threshold = semua bet dgn edge > 0)
        + tabel hasil ke stdout. Anti-leakage: semua input pre-kickoff.
Runtime target: < 60 detik.
"""
import csv
import math
import os
import time
from collections import Counter

import numpy as np

import paths

PROJ = paths.BASE
PRED = os.path.join(PROJ, "predictions_v2.csv")
RAW = os.path.join(PROJ, "all_matches_clean.csv")
OUT = os.path.join(PROJ, "value_bets.csv")

T_GRID = [0.00, 0.01, 0.03, 0.05, 0.08]
SEED = 42
NBOOT = 1000
MIN_N_BEST = 30  # minimal n utk memilih 'threshold terbaik' per pasar
# kolom odds closing ASLI di all_matches_clean.csv (header beda nama dari predictions)
RAW_COLS = ["PSCH", "PSCD", "PSCA", "AvgC>2.5", "AHh", "AvgCAHH"]

t0 = time.time()


def fnum(x):
    if x is None:
        return None
    x = str(x).strip()
    if not x:
        return None
    try:
        v = float(x)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


# ============================================================ 1. LOAD PREDICTIONS
with open(PRED, newline="", encoding="utf-8-sig") as fh:
    rd = csv.DictReader(fh)
    PRED_FIELDS = list(rd.fieldnames)
    preds = list(rd)
n_pred = len(preds)


def pkey(p):
    return (p["div"].strip(), p["date"].strip(), p["season"].strip(),
            p["home"].strip(), p["away"].strip())


keys = [pkey(p) for p in preds]
keyset = set(keys)
dupc = Counter(keys)
n_dupkeys = sum(v - 1 for v in dupc.values() if v > 1)

# ============================== 2. STREAM RAW (odds closing asli) & JOIN
# raw: Div, Season, Date, HomeTeam, AwayTeam
oddsmap = {}
n_raw = 0
n_rawmatched = 0
with open(RAW, newline="", encoding="utf-8-sig") as fh:
    rd = csv.DictReader(fh)
    RAW_FIELDS = list(rd.fieldnames)
    for row in rd:
        n_raw += 1
        k = (str(row.get("Div", "")).strip(), str(row.get("Date", "")).strip(),
             str(row.get("Season", "")).strip(), str(row.get("HomeTeam", "")).strip(),
             str(row.get("AwayTeam", "")).strip())
        if k not in keyset:
            continue
        n_rawmatched += 1
        vals = {c: fnum(row.get(c)) for c in RAW_COLS}
        if k not in oddsmap:
            oddsmap[k] = vals
        else:  # duplikat: simpan baris dgn odds paling lengkap
            if sum(v is not None for v in vals.values()) > sum(
                    v is not None for v in oddsmap[k].values()):
                oddsmap[k] = vals
n_join = len(oddsmap)

# ==================================================== 3. BANGUN DAFTAR BET
bets = []
opp = Counter()        # peluang bet tersetel per pasar
miss = Counter()       # peluang gagal: odds closing kosong/invalid
unsettled = Counter()  # peluang gagal: outcome hilang
line_mismatch = 0
n_ftr_score_mismatch = 0
max_probsum_dev = 0.0

for i, p in enumerate(preds):
    k = keys[i]
    od = oddsmap.get(k)
    ftr = (p.get("ftr") or "").strip().upper()
    yh, ya = fnum(p.get("yh")), fnum(p.get("ya"))
    home, away = p["home"].strip(), p["away"].strip()
    # sanity 1X2 prob murni menjumlah ~1
    s3 = [fnum(p.get(c)) for c in ("ph_dc", "pd_dc", "pa_dc")]
    if all(v is not None for v in s3):
        max_probsum_dev = max(max_probsum_dev, abs(sum(s3) - 1.0))
    # konsistensi ftr vs skor
    if yh is not None and ya is not None and ftr in ("H", "D", "A"):
        exp = "H" if yh > ya else ("A" if ya > yh else "D")
        if exp != ftr:
            n_ftr_score_mismatch += 1

    def add(market, side, team, line, odds_v, pm, ret):
        bets.append(dict(div=p["div"].strip(), season=p["season"].strip(),
                         date=p["date"].strip(), home=home, away=away, mid=i,
                         market=market, side=side, team=team, line=line,
                         odds=odds_v, p_model=pm, p_imp=1.0 / odds_v,
                         edge=pm - 1.0 / odds_v, ret=ret))

    # ---- 1X2 (sisi H/D/A independen) ----
    if any(v is not None for v in s3):
        for side, pcol, ocol in (("H", "ph_dc", "PSCH"), ("D", "pd_dc", "PSCD"),
                                 ("A", "pa_dc", "PSCA")):
            pm = fnum(p.get(pcol))
            if pm is None:
                miss["1X2_model_prob_missing"] += 1
                continue
            ov = od.get(ocol) if od else None
            if ov is None or ov <= 1.0:
                miss["1X2_no_closing_odds"] += 1
            elif ftr not in ("H", "D", "A"):
                unsettled["1X2_ftr_missing"] += 1
            else:
                opp["1X2"] += 1
                team = home if side == "H" else (away if side == "A" else "Draw")
                add("1X2", side, team, None, ov, pm, ov if ftr == side else 0.0)

    # ---- O/U (over 2.5 saja) ----
    pm = fnum(p.get("p_over_dc"))
    if pm is None:
        miss["OU_model_prob_missing"] += 1
    else:
        ov = od.get("AvgC>2.5") if od else None
        if ov is None or ov <= 1.0:
            miss["OU_no_closing_odds"] += 1
        elif yh is None or ya is None:
            unsettled["OU_score_missing"] += 1
        else:
            opp["OU"] += 1
            add("OU", "Over", home + " v " + away, 2.5, ov, pm,
                ov if (yh + ya) > 2.5 else 0.0)

    # ---- AH (sisi home, line raw AHh) ----
    pm = fnum(p.get("p_ah_home"))
    if pm is None:
        miss["AH_model_prob_missing"] += 1
    else:
        ahline = od.get("AHh") if od else None
        ahodds = od.get("AvgCAHH") if od else None
        pline = fnum(p.get("ahh"))
        if ahline is None or ahodds is None or ahodds <= 1.0:
            miss["AH_no_closing_odds"] += 1
        elif yh is None or ya is None:
            unsettled["AH_score_missing"] += 1
        elif pline is None or abs(pline - ahline) > 1e-6:
            line_mismatch += 1
        else:
            opp["AH"] += 1
            q = round(((yh - ya) + ahline) * 4)  # margin dalam kuartal anti-float
            if q == 0:
                ret, push = 1.0, True
            elif q > 0:
                ret, push = (1.0 + (ahodds - 1.0) / 2.0 if q == 1 else ahodds), False
            else:
                ret, push = (0.5 if q == -1 else 0.0), False
            bets.append(dict(div=p["div"].strip(), season=p["season"].strip(),
                             date=p["date"].strip(), home=home, away=away, mid=i,
                             market="AH", side="AH_home", team=home, line=ahline,
                             odds=ahodds, p_model=pm, p_imp=1.0 / ahodds,
                             edge=pm - 1.0 / ahodds, ret=ret, push=push))

assert len(bets) == sum(opp.values()), "bets != opp"

# ============================================== 4. AGREGASI PER THRESHOLD
agg = {}
for b in bets:
    e = b["edge"]
    for t in T_GRID:
        if e > t:
            a = agg.setdefault((b["market"], t), dict(n=0, rt=0.0, npush=0))
            a["n"] += 1
            a["rt"] += b["ret"]
            if b.get("push"):
                a["npush"] += 1


def roi_view(market, t, excl_push):
    a = agg.get((market, t))
    if not a:
        return 0, 0.0, float("nan")
    n, rt, npush = a["n"], a["rt"], a["npush"]
    if excl_push and market == "AH":
        n, rt = n - npush, rt - npush  # push: stake 1, return 1 -> keluarkan
    return n, rt, (rt - n) / n if n else float("nan")


# ============================================== 5. CETAK HASIL
W = 78
print("=" * W)
print("VERIFIKASI DATA")
print("=" * W)
print(f"baris predictions_v2.csv                : {n_pred}")
print(f"baris all_matches_clean.csv             : {n_raw}")
print(f"join sukses (match pred dgn odds asli)  : {n_join} ({100.0*n_join/n_pred:.2f}%)")
print(f"baris raw yg cocok kunci (scan)         : {n_rawmatched}")
print(f"kunci pred duplikat                     : {n_dupkeys}")
print(f"|ph_dc+pd_dc+pa_dc - 1| max             : {max_probsum_dev:.2e}")
print(f"ftr vs skor tidak konsisten             : {n_ftr_score_mismatch}")
print(f"peluang per pasar (valid & tersetel)    : {dict(opp)}")
print(f"peluang tanpa odds closing              : {dict(miss)}")
print(f"peluang outcome hilang                  : {dict(unsettled)}")
print(f"mismatch line AH pred vs raw            : {line_mismatch}")
print()
print("=" * W)
print("TABEL 1: ROI & n per threshold PER PASAR (1 unit/bet; ROI=profit/stake)")
print("=" * W)
print(f"{'pasar':<16}{'thr':>6}{'n':>8}{'profit(u)':>12}{'ROI%':>10}{'push':>7}")
best_thr = {}
for mkt in ("1X2", "OU", "AH"):
    for t in T_GRID:
        a = agg[(mkt, t)]
        for excl in ([False, True] if mkt == "AH" else [False]):
            n, rt, roi = roi_view(mkt, t, excl)
            label = mkt + (" excl-push" if excl else (" incl-push" if mkt == "AH" else ""))
            print(f"{label:<16}{t:>6.2f}{n:>8d}{rt-n:>12.1f}{roi*100:>9.2f}%{a['npush']:>7d}")
            if mkt == "AH" and excl is False:
                continue
    # pilih threshold terbaik (ROI maks, n>=MIN_N_BEST; AH pakai definisi excl-push)
    cands = []
    for t in T_GRID:
        n, rt, roi = roi_view(mkt, t, excl_push=True)
        cands.append((t, n, roi))
    ok = [c for c in cands if c[1] >= MIN_N_BEST]
    pick = max(ok or cands, key=lambda c: c[2])
    best_thr[mkt] = pick[0]
    tag = "" if ok else "  [!tanpa n>=" + str(MIN_N_BEST) + ", diambil n max]"
    print(f"  >> threshold terbaik {mkt}: {pick[0]:.2f} (n={pick[1]}, ROI={pick[2]*100:.2f}%){tag}")

BINS = [(1.0, 1.5), (1.5, 2.0), (2.0, 2.5), (2.5, 3.0), (3.0, 4.0), (4.0, 6.0), (6.0, math.inf)]


def bin_label(o):
    for lo, hi in BINS:
        if lo <= o < hi:
            return f"[{lo:g},{hi:g})" if math.isfinite(hi) else f"[{lo:g}+)"
    return "NA"


print()
print("=" * W)
print("TABEL 2: ROI per LIGA di threshold terbaik per pasar")
print("=" * W)
league_rows = {}
season_rows = {}
pools = {}
for mkt in ("1X2", "OU", "AH"):
    tbest = best_thr[mkt]
    tier = mkt == "AH"
    pool = [b for b in bets if b["market"] == mkt and b["edge"] > tbest
            and not (tier and b.get("push"))]
    pool.sort(key=lambda b: (b["date"], b["mid"], b["side"]))
    pools[(mkt, tbest, "excl")] = pool
    pools[(mkt, tbest, "incl")] = ([b for b in bets if b["market"] == mkt and b["edge"] > tbest]
                                   if tier else pool)
    for b in pool:
        g = league_rows.setdefault((mkt, b["div"]), [0, 0.0])
        g[0] += 1
        g[1] += b["ret"] - 1.0
    for b in pools[(mkt, tbest, "incl")]:
        g = season_rows.setdefault((mkt, b["season"]), [0, 0.0])
        g[0] += 1
        g[1] += b["ret"] - 1.0
    print(f"-- {mkt} @ edge>{tbest:.2f} (AH excl-push)")
    for key in sorted(league_rows):
        if key[0] != mkt:
            continue
        n, prof = league_rows[key]
        print(f"   {key[1]:<8} n={n:>6d}  profit={prof:>9.1f}u  ROI={prof/n*100:>7.2f}%")

print()
print("=" * W)
print("TABEL 3: ROI per MUSIM di threshold terbaik per pasar (AH incl-push)")
print("=" * W)
for mkt in ("1X2", "OU", "AH"):
    tbest = best_thr[mkt]
    print(f"-- {mkt} @ edge>{tbest:.2f}")
    for key in sorted(season_rows):
        if key[0] != mkt:
            continue
        n, prof = season_rows[key]
        print(f"   musim {key[1]:<8} n={n:>6d}  profit={prof:>9.1f}u  ROI={prof/n*100:>7.2f}%")


def bootstrap_ci(pool):
    grp = {}
    for b in pool:
        g = grp.setdefault(b["mid"], [0.0, 0.0])
        g[0] += 1.0
        g[1] += b["ret"] - 1.0
    S = np.array([g[0] for g in grp.values()])
    P = np.array([g[1] for g in grp.values()])
    m = len(S)
    if m == 0:
        return 0, float("nan"), float("nan")
    rng = np.random.default_rng(SEED)
    rois = np.empty(NBOOT)
    for j in range(NBOOT):
        idx = rng.integers(0, m, m)
        rois[j] = P[idx].sum() / S[idx].sum()
    lo, hi = np.percentile(rois, [2.5, 97.5])
    return m, float(lo), float(hi)


print()
print("=" * W)
print(f"TABEL 4: BOOTSTRAP 95% CI ROI (resample MATCH, seed={SEED}, {NBOOT} iter)")
print("=" * W)
boot_res = {}
for mkt in ("1X2", "OU", "AH"):
    for mode in (["excl", "incl"] if mkt == "AH" else ["excl"]):
        tbest = best_thr[mkt]
        pool = pools[(mkt, tbest, mode)]
        m, lo, hi = bootstrap_ci(pool)
        n, rt, roi = roi_view(mkt, tbest, mode == "excl")
        boot_res[(mkt, mode)] = (m, lo, hi)
        print(f"   {mkt:<5}{mode:<6} thr={tbest:.2f} match={m:>6d} ROI={roi*100:>7.2f}%  "
              f"CI95=[{lo*100:>6.2f}%, {hi*100:>6.2f}%]  signifikan>0: {'YA' if lo > 0 else 'tidak'}")

print()
print("=" * W)
print("TABEL 5: DRAWDOWN MAKSIMUM & KURVA CUMULATIVE ROI (kronologis, per decile)")
print("=" * W)
for mkt in ("1X2", "OU", "AH"):
    tbest = best_thr[mkt]
    pool = pools[(mkt, tbest, "excl")]
    if not pool:
        print(f"-- {mkt} @ edge>{tbest:.2f}  POOL KOSONG")
        continue
    prof = np.array([b["ret"] - 1.0 for b in pool])
    cum = np.cumsum(prof)
    rm = np.maximum.accumulate(np.concatenate(([0.0], cum)))[1:]
    dd = rm - cum
    imdd = int(dd.argmax()) if len(dd) else -1
    mdd = float(dd.max()) if len(dd) else 0.0
    tdates = f"{pool[imdd]['date']}" if imdd >= 0 else "-"
    curve = " ".join(f"{cum[min(len(pool), max(1, round(len(pool)*q/10)))-1]/min(len(pool), max(1, round(len(pool)*q/10)))*100:>6.2f}" for q in range(1, 11))
    print(f"-- {mkt} @ edge>{tbest:.2f}  n={len(pool)}  profit={cum[-1]:.1f}u  "
          f"maxDD={mdd:.1f}u (tgl {tdates})")
    print(f"   cumROI% per decile: {curve}")

print()
print("=" * W)
print("TABEL 6: SPLIT MAGNITUDO ODDS (deteksi favorite-longshot bias)")
print("=" * W)
binrows = {}
for mkt in ("1X2", "OU", "AH"):
    tbest = best_thr[mkt]
    for b in pools[(mkt, tbest, "excl")]:
        j = next((idx for idx, (lo, hi) in enumerate(BINS) if lo <= b["odds"] < hi), None)
        if j is None:
            continue
        g = binrows.setdefault((mkt, j), [0, 0.0, 0])
        g[0] += 1
        g[1] += b["ret"] - 1.0
        if b["ret"] > 0.999:  # menang (ATAU return > setengah kemenangan; dorongan tidak dihitung)
            g[2] += 1
print(f"{'pasar':<6}{'odds bin':<13}{'n':>7}{'hit':>7}{'hit_rate':>10}{'ROI%':>9}")
for mkt in ("1X2", "OU", "AH"):
    for j, (blo, bhi) in enumerate(BINS):
        g = binrows.get((mkt, j))
        lab = f"[{blo:g},{bhi:g})" if math.isfinite(bhi) else f"[{blo:g}+)"
        if not g:
            print(f"{mkt:<6}{lab:<13}{'-':>7}{'-':>7}{'-':>10}{'-':>9}")
            continue
        n, prof, hits = g
        print(f"{mkt:<6}{lab:<13}{n:>7d}{hits:>7d}{hits/n*100:>9.1f}%{prof/n*100:>8.2f}%")

# ============================================== 6. TULIS value_bets.csv (edge>0)
vpool = [b for b in bets if b["edge"] > 0.0]
vpool.sort(key=lambda b: (b["date"], b["mid"], b["market"]))
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["market", "league", "season", "date", "home", "away", "side", "team",
                "line", "odds", "p_model", "p_implied", "edge", "stake", "return"])
    for b in vpool:
        w.writerow([b["market"], b["div"], b["season"], b["date"], b["home"], b["away"],
                    b["side"], b["team"], "" if b["line"] is None else b["line"],
                    repr(b["odds"]), repr(b["p_model"]), repr(b["p_imp"]),
                    repr(b["edge"]), 1, repr(b["ret"])])

# ============================================== 7. VERIFIKASI KONSISTENSI n
chk = Counter()
with open(OUT, newline="", encoding="utf-8") as fh:
    rd = csv.DictReader(fh)
    rows_file = 0
    for row in rd:
        rows_file += 1
        e = float(row["edge"])
        for t in T_GRID:
            if e > t:
                chk[(row["market"], t)] += 1
bad = []
for mkt in ("1X2", "OU", "AH"):
    for t in T_GRID:
        if chk[(mkt, t)] != agg[(mkt, t)]["n"]:
            bad.append((mkt, t, chk[(mkt, t)], agg[(mkt, t)]["n"]))
print()
print("=" * W)
print("VERIFIKASI KONSISTENSI")
print("=" * W)
print(f"value_bets.csv baris (bet edge>0)     : {rows_file} (diharapkan {len(vpool)})")
print(f"total bet @thr 0.00 dari semua pool   : {sum(agg[(m,t)]['n'] for m in ('1X2','OU','AH') for t in [0.00])}")
print(f"cekap n per (pasar,threshold) file vs hitung: {'PASS' if not bad and rows_file == len(vpool) else 'FAIL ' + str(bad)}")
print(f"Runtime total: {time.time()-t0:.1f}s")
