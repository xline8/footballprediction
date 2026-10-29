"""Corner v3: ablation mu berbasis rolling SHOTS (5 match terakhir per tim).
gamma* (elastisitas) fit di validasi 19/20-20/21; test 21/22-25/26.
Komparator: base-rate liga (per liga-month, r moment) = juara log-loss.
Lulus jika NLL test model shot < NLL test base-rate.

Mode:
  python model_corners_v3.py            # walk-forward validation (backtest)
  python model_corners_v3.py --predict  # predict upcoming fixtures
Output:
  predictions_corners_shots.csv         # backtest results
  predictions_corners_upcoming.csv      # upcoming fixtures predictions
"""
import os
import csv
import json
import math
import sys
import time
from collections import defaultdict, deque
from datetime import datetime

BASE = os.path.join(os.path.expanduser("~"), "football-data")
DATA = os.path.join(BASE, "all_matches_clean.csv")
OUT = os.path.join(BASE, "predictions_corners_shots.csv")
UPCOMING_OUT = os.path.join(BASE, "predictions_corners_upcoming.csv")
PARAMS_OUT = os.path.join(BASE, "ta", "corner_params.json")
FIX_MAP = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
           "I1": "Serie_A", "F1": "Ligue_1"}
TOP5 = ["E0", "D1", "I1", "SP1", "F1"]
VAL_SEASONS = {"2019/20", "2020/21"}
TEST_SEASONS = {"2021/22", "2022/23", "2023/24", "2024/25", "2025/26"}
HL = 270.0
GRID = 50
LINES = [6.5, 7.5, 8.5, 9.5, 10.5, 11.5]
GAMMA_GRID = [0.0, 0.15, 0.3, 0.45, 0.6, 0.8]
R_MIN = 1.02
REL_LO, REL_HI = 0.6, 1.7


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


matches = []
by_div = None


def _ensure_loaded():
    """Muata data secara lazy (sekali saja) agar meng-import modul tidak berat."""
    global matches, by_div
    if by_div is not None:
        return
    loaded = []
    with open(DATA, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["Div"] not in TOP5 or not r["Date"] or r["FTR"] not in ("H", "D", "A"):
                continue
            vals = [num(r[c]) for c in ("HC", "AC", "HS", "AS")]
            if any(v is None for v in vals):
                continue
            loaded.append({
                "div": r["Div"], "date": datetime.strptime(r["Date"], "%Y-%m-%d").date(),
                "season": r["Season"], "home": r["HomeTeam"], "away": r["AwayTeam"],
                "hc": int(vals[0]), "ac": int(vals[1]),
                "hs": int(vals[2]), "as": int(vals[3]),
            })
    loaded.sort(key=lambda m: m["date"])
    bd = defaultdict(list)
    for i, m in enumerate(loaded):
        bd[m["div"]].append(i)
    matches = loaded
    by_div = bd

def rel_factors(home, away, L, dq):
    """Rolling shot-based relative factors. dq = {team: deque[(hs, as)]}."""
    if L is None or L <= 0:
        return 1.0, 1.0, 1.0, 1.0
    def f(team, idx):
        d = dq.get(team)
        if not d:
            return 1.0
        return clamp(sum(x[idx] for x in d) / len(d) / L, REL_LO, REL_HI)
    return f(home, 0), f(home, 1), f(away, 0), f(away, 1)


def stats_window(games, cutoff):
    wh = wa = wsum = ws = 0.0
    nry = dmu = 0.0
    for h, a, hc, ac, hs, asx, dt in games:
        w = 0.5 ** ((cutoff - dt).days / HL)
        wh += w * hc
        wa += w * ac
        ws += w * (hs + asx)
        wsum += 2 * w
        mu = (wh + wa) / wsum
        nry += w * (hc + ac) ** 2
    # dmu = total corner terbobot FINAL (wh + wa). Versi lama mengakumulasi
    # w * (wh + wa) di dalam loop memakai jumlah kumulatif berjalan,
    # sehingga r_base bergantung pada urutan games dan bukan estimator
    # yang dimaksud (audit ulang 2026-10-29).
    dmu = wh + wa
    base_h = wh * 2 / wsum
    base_a = wa * 2 / wsum
    base_mu = base_h + base_a
    r_base = (nry / max(dmu, 1e-9))
    L = ws / wsum
    return base_h, base_a, base_mu, r_base, L


def run_wf(seasons):
    _ensure_loaded()
    ptr = {d: 0 for d in TOP5}
    games_hist = {d: [] for d in TOP5}
    dq = defaultdict(lambda: deque(maxlen=5))
    groups = defaultdict(list)
    for i, m in enumerate(matches):
        if m["season"] in seasons:
            groups[(m["div"], m["date"].year, m["date"].month)].append(i)
    rows = []
    t0 = time.time()
    for (div, yr, mo) in sorted(groups):
        idxs = groups[(div, yr, mo)]
        start = min(matches[i]["date"] for i in idxs)
        # Anti-leakage: seluruh match dalam satu grup > berada setelah data training.
        assert all(matches[i]["date"] >= start for i in idxs), "leakage dalam grup test"
        lst = by_div[div]
        while ptr[div] < len(lst) and matches[lst[ptr[div]]]["date"] < start:
            j = lst[ptr[div]]
            mm = matches[j]
            games_hist[div].append((mm["home"], mm["away"], mm["hc"], mm["ac"],
                                    mm["hs"], mm["as"], mm["date"]))
            dq[mm["home"]].append((mm["hs"], mm["as"]))
            dq[mm["away"]].append((mm["as"], mm["hs"]))
            ptr[div] += 1
        base_h, base_a, base_mu, r_base, L = stats_window(games_hist[div], start)
        for i in idxs:
            mm = matches[i]
            fhp, fhc, fap, fac = rel_factors(mm["home"], mm["away"], L, dq)
            rows.append({
                "div": div, "date": mm["date"].isoformat(), "season": mm["season"],
                "home": mm["home"], "away": mm["away"],
                "hc": mm["hc"], "ac": mm["ac"], "y": mm["hc"] + mm["ac"],
                "base_h": base_h, "base_a": base_a, "r_cb": r_base,
                "fhp": fhp, "fhc": fhc, "fap": fap, "fac": fac,
            })
    print(f"  [wf {sorted(seasons)}] pred={len(rows):,} waktu={time.time()-t0:.0f}s")
    return rows


def pmf_k(mu, k):
    tot = []
    for x in range(GRID + 1):
        logc = math.lgamma(x + k) - math.lgamma(k) - math.lgamma(x + 1)
        tot.append(math.exp(logc + k * math.log(k / (k + mu))
                            + x * math.log(mu / (k + mu))))
    s = sum(tot)
    return [p / s for p in tot]


def k_of(r, mu):
    return mu / (r - 1.0) if r > R_MIN else 1e9


def nll_row(mu, r, y):
    p = pmf_k(mu, k_of(r, mu))[min(int(y), GRID)]
    return -math.log(max(p, 1e-12))


def mu_cs(row, gamma):
    return (row["base_h"] * (row["fhp"] * row["fac"]) ** gamma
            + row["base_a"] * (row["fap"] * row["fhc"]) ** gamma)


def _run_backtest():
    """Walk-forward validation + backtest output (original behavior)."""
    _ensure_loaded()
    print("walk-forward ...")
    rows_val = run_wf(VAL_SEASONS)
    rows_te = run_wf(TEST_SEASONS)

    print("\n-- grid gamma di validasi (pooled, mean NLL) --")
    best = None
    for g in GAMMA_GRID:
        mus = [mu_cs(r0, g) for r0 in rows_val]
        r_g = (sum((r0["y"] - mu) ** 2 for r0, mu in zip(rows_val, mus))
               / max(sum(mus), 1e-9))
        v = sum(nll_row(mu, r_g, r0["y"]) for r0, mu in zip(rows_val, mus)) / len(rows_val)
        if best is None or v < best[1]:
            best = (g, v, r_g)
        print(f"gamma={g:.2f} NLL {v:.4f} (r={r_g:.3f})")
    gstar, vstar, rstar = best
    print(f"-> gamma* = {gstar} (NLL validasi {vstar:.4f}, r={rstar:.3f})")

    print("\n=== TEST: log-loss distribusi total ===")
    nll_cb = sum(nll_row(r0["base_h"] + r0["base_a"], r0["r_cb"], r0["y"])
                 for r0 in rows_te) / len(rows_te)
    mus_cs = [mu_cs(r0, gstar) for r0 in rows_te]
    nll_cs = sum(nll_row(mu, rstar, r0["y"]) for r0, mu in zip(rows_te, mus_cs)) / len(rows_te)
    nll_pois = sum(nll_row(mu, 1.0, r0["y"]) for r0, mu in zip(rows_te, mus_cs)) / len(rows_te)
    print(f"base-rate liga (CB): {nll_cb:.4f}")
    print(f"shot-based  (CS)  : {nll_cs:.4f}  (gamma*={gstar}, r*={rstar:.3f})")
    print(f"CS Poisson        : {nll_pois:.4f}")

    print("\n=== TEST: mean mu vs aktual per liga (CS) ===")
    agg = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0])
    for r0, mu in zip(rows_te, mus_cs):
        c = agg[r0["div"]]
        c[0] += 1
        c[1] += mu
        c[2] += r0["y"]
        c[3] += (r0["y"] - mu) ** 2
        c[4] += (r0["y"] - (r0["base_h"] + r0["base_a"])) ** 2
    print(f"{'Div':6s} {'n':>6s} {'muCS':>6s} {'akt':>6s} {'RMSE_CS':>8s} {'RMSE_CB':>8s}")
    for k in TOP5:
        n = int(agg[k][0])
        print(f"{k:6s} {n:6,d} {agg[k][1]/n:6.2f} {agg[k][2]/n:6.2f} "
              f"{math.sqrt(agg[k][3]/n):8.2f} {math.sqrt(agg[k][4]/n):8.2f}")

    print("\n=== TEST: bucket P(total > 9.5) ===")
    def buckets(rows, mus, rfn):
        acc = defaultdict(lambda: [0, 0.0, 0.0])
        for r0, mu in zip(rows, mus):
            p = sum(pmf_k(mu, k_of(rfn(r0), mu))[10:])
            for lo, hi in [(0.2, 0.3), (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7), (0.7, 0.8)]:
                if lo <= p < hi:
                    acc[(lo, hi)][0] += 1
                    acc[(lo, hi)][1] += 1.0 if r0["y"] > 9.5 else 0.0
                    acc[(lo, hi)][2] += p
        return acc

    acc_cb = buckets(rows_te, [r0["base_h"] + r0["base_a"] for r0 in rows_te],
                     lambda r0: r0["r_cb"])
    acc_cs = buckets(rows_te, mus_cs, lambda r0: rstar)
    print(f"{'bucket':10s} {'n':>6s} | {'CB akt/pred':>12s} | {'CS akt/pred':>12s}")
    for key in sorted(acc_cb):
        n, s, p = acc_cb[key]
        n2, s2, p2 = acc_cs.get(key, [0, 0.0, 0.0])
        cb_txt = f"{s/n:5.2f}/{p/n:5.2f}" if n else "  -  "
        cs_txt = f"{s2/n2:5.2f}/{p2/n2:5.2f}" if n2 else "  -  "
        print(f"{key[0]:.1f}-{key[1]:.1f}    {n:6,d} | {cb_txt:>12s} | {cs_txt:>12s}")

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["div", "date", "season", "home", "away", "hc", "ac", "y_total",
                     "mu_base_cb", "mu_shots_cs", "r_cb", "r_cs",
                     "p_gt_cb_9.5", "p_gt_cs_9.5"]
                    + [f"p_gt_cs_{ln}" for ln in LINES])
        for r0, mu in zip(rows_te, mus_cs):
            pcb = sum(pmf_k(r0["base_h"] + r0["base_a"], k_of(r0["r_cb"],
                      r0["base_h"] + r0["base_a"]))[10:])
            pcs = sum(pmf_k(mu, k_of(rstar, mu))[10:])
            wr.writerow([r0["div"], r0["date"], r0["season"], r0["home"], r0["away"],
                         r0["hc"], r0["ac"], r0["y"],
                         round(r0["base_h"] + r0["base_a"], 2), round(mu, 2),
                         round(r0["r_cb"], 3), round(rstar, 3), round(pcb, 4), round(pcs, 4)]
                        + [round(sum(pmf_k(mu, k_of(rstar, mu))[int(ln) + 1:]), 4)
                           for ln in LINES])
    print("\ntersimpan:", OUT)

    # --- simpan parameter yang sudah terfit — dipakai predict_upcoming() ---
    os.makedirs(os.path.dirname(PARAMS_OUT), exist_ok=True)
    with open(PARAMS_OUT, "w") as f:
        json.dump({"gamma": gstar, "r": rstar, "hl": HL}, f)
    print("params disimpan:", PARAMS_OUT)

    return gstar, rstar


def predict_upcoming():
    """Predict corner probabilities for upcoming fixtures.

    Uses fitted gamma*/r* (from validation) + rolling shot data to predict
    total corners for each upcoming match. Reads fixtures from Understat
    _2026_fixtures.json (same source as predict_upcoming.py).
    """
    if not os.path.exists(PARAMS_OUT):
        print("  ! params tidak ada — jalankan dulu model_corners_v3.py (tanpa --predict)")
        return 0
    _ensure_loaded()
    with open(PARAMS_OUT) as f:
        params = json.load(f)
    gamma, r_star = params["gamma"], params["r"]

    # Load historical matches for training window + rolling shots
    hist = sorted(matches, key=lambda m: m["date"])
    # Build rolling shot deques from ALL historical matches (chronological)
    dq = defaultdict(lambda: deque(maxlen=5))
    # games per div for stats_window
    games_hist = defaultdict(list)
    ptr = {d: 0 for d in TOP5}

    # Load upcoming fixtures from Understat
    today = datetime.now().date()
    upcoming = []
    for div, slug in FIX_MAP.items():
        p = os.path.join(BASE, "xg_raw", f"{slug}_2026_fixtures.json")
        if not os.path.exists(p):
            print(f"  ! {p} tidak ada")
            continue
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            if d.get("isResult"):
                continue
            dt = datetime.strptime(d["datetime"], "%Y-%m-%d %H:%M:%S").date()
            if dt < today:
                continue
            # Map Understat team name -> FD name
            home = _understat_to_fd(div, d["h"]["title"])
            away = _understat_to_fd(div, d["a"]["title"])
            if not home or not away:
                continue
            upcoming.append(dict(div=div, date=dt.isoformat(),
                                 home=home, away=away))

    if not upcoming:
        print("  ! tidak ada fixture upcoming")
        return 0

    # Feed all historical matches into rolling windows + games_hist
    for m in hist:
        games_hist[m["div"]].append(
            (m["home"], m["away"], m["hc"], m["ac"], m["hs"], m["as"], m["date"]))
        dq[m["home"]].append((m["hs"], m["as"]))
        dq[m["away"]].append((m["as"], m["hs"]))

    # Compute per-div base rates
    base = {}
    for d in TOP5:
        if games_hist[d]:
            bh, ba, bmu, r_cb, L = stats_window(games_hist[d], today)
            base[d] = (bh, ba, bmu, r_cb, L)

    LINES_UPCOMING = [6.5, 7.5, 8.5, 9.5, 10.5, 11.5]
    rows = []
    for fx in sorted(upcoming, key=lambda x: (x["div"], x["date"])):
        d = fx["div"]
        bh, ba, bmu, r_cb, L = base.get(d, (9.0, 9.0, 18.0, 1.18, 10.0))
        # Rel factors from rolling shots
        fhp, fhc, fap, fac = rel_factors(fx["home"], fx["away"], L, dq)
        mu = mu_cs({"base_h": bh, "base_a": ba, "fhp": fhp, "fhc": fhc,
                     "fap": fap, "fac": fac}, gamma)
        probs = {}
        for ln in LINES_UPCOMING:
            k = k_of(r_star, mu)
            probs[f"p_gt_{ln}"] = round(sum(pmf_k(mu, k)[int(ln) + 1:]), 4)
        # Rekomendasi: garis fair dalam band 8.5–10.5 — pilih line (L) yang
        # meminimalkan |(L+0.5) − mu_shots_cs|; side Over bila p_gt_L >= 0.5,
        # selain itu Under; rec_prob = probabilitas sisi terpilih.
        rec_line = min((8.5, 9.5, 10.5), key=lambda L: abs((L + 0.5) - mu))
        p_l = probs[f"p_gt_{rec_line}"]
        rec_side = "Over" if p_l >= 0.5 else "Under"
        rec_prob = p_l if rec_side == "Over" else 1.0 - p_l
        recommendation = f"{rec_side} {rec_line}"
        rows.append({
            "div": d, "date": fx["date"], "home": fx["home"], "away": fx["away"],
            "mu_shots_cs": round(mu, 2), "r_cs": round(r_star, 3),
            "rec_line": rec_line, "rec_side": rec_side, "recommendation": recommendation,
            "rec_prob": round(rec_prob, 4),
            **probs,
        })

    cols = ["div", "date", "home", "away", "mu_shots_cs", "r_cs",
            "rec_line", "rec_side", "recommendation", "rec_prob"] + \
           [f"p_gt_{ln}" for ln in LINES_UPCOMING]
    with open(UPCOMING_OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"  {len(rows)} upcoming corner predictions -> {UPCOMING_OUT}")
    return len(rows)


def _understat_to_fd(div, name):
    """Map Understat team name to FD/normalized name."""
    nmap = {}
    for fn in ("map_full.json", "map_ext.json"):
        p = os.path.join(BASE, "xg_raw", fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                nmap.update(json.load(f))
    fd_name = nmap.get(f"{div}|{name}")
    return fd_name if fd_name else name


if __name__ == "__main__":
    if "--predict" in sys.argv:
        print("=== predict upcoming corner fixtures ===")
        predict_upcoming()
    else:
        _run_backtest()
