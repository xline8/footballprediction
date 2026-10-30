#!/usr/bin/env python3
"""backtest_picks.py — backtest value-bet 1X2 dengan mesin eksperimen yang dapat
dikonfigurasi (model, de-vigging, threshold, staking).

Alur:
1. `cache_records()` — jalankan walk-forward SEKALI (DC + T3), simpan prob &
   odds per match ke `records_cache.jsonl`.
2. `evaluate_strategy(records, cfg)` — simulasi bet (aturan sama dgn make_picks:
   signal = prob model murni, harga = odds opening/day-of, edge > thr) utk satu
   konfigurasi. Return yield/hit-rate + metrik log loss/Brier/macro-F1.

Scope: pasar 1X2 (pasar utama make_picks). Corner/OU tidak disertakan di sini.

Jalankan:
  python backtest_picks.py --cache-only        # bangun cache (sekali)
  python backtest_picks.py --devig shin --thr 0.02
  python backtest_picks.py --model blend --blend-w 0.3 --stake kelly --kelly 0.25
"""

import csv
import json
import math
import os
import sys
from datetime import datetime

import numpy as np

import model_features_1x2 as mf
from features import build_feature_rows
from football_etl import load_fd_odds, normalize_name, parse_date, TOP5
from model_v2 import DC, xg_key
import model_v2
from features import _load_xg_map
from validation import eval_1x2

BASE = os.path.dirname(os.path.abspath(__file__))
RECORDS = os.path.join(BASE, "records_cache.jsonl")
YIDX = {"H": 0, "D": 1, "A": 2}
SIDES = (0, 1, 2)

DEFAULT_CFG = {
    "model": "meta",     # meta | dc | t3 | blend  (E1 meta menang)
    "blend_w": 0.3,      # bobot T3 saat model=blend (0.3 = 0.7 DC + 0.3 T3)
    "devig": "shin",     # none | mult | shin  (E1: shin menang)
    "thr": 0.15,         # E4: sweep -> 0.15 terbaik
    "stake": "flat",     # flat | kelly
    "kelly": 0.25,
    "calib": "none",     # none | platt
}


def _as_date(d):
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, str):
        return datetime.strptime(d[:10], "%Y-%m-%d").date()
    return d


def _load_hist_odds(path):
    odds = {}
    if not os.path.exists(path):
        return odds
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = parse_date(r.get("Date"))
            if not d:
                continue
            h = normalize_name(r.get("HomeTeam"))
            a = normalize_name(r.get("AwayTeam"))
            if not h or not a:
                continue
            bh, bd, ba = r.get("B365H"), r.get("B365D"), r.get("B365A")
            if bh and bd and ba:
                try:
                    odds[(r.get("Div"), d.isoformat(), h, a)] = (
                        float(bh), float(bd), float(ba))
                except ValueError:
                    continue
    return odds


def _open_dec(o):
    if isinstance(o, (tuple, list)) and len(o) >= 3:
        h, d, a = o[0], o[1], o[2]
    else:
        h, d, a = o.get("B365H"), o.get("B365D"), o.get("B365A")
        if not (h and d and a):
            h, d, a = o.get("AvgH"), o.get("AvgD"), o.get("AvgA")
    try:
        h, d, a = float(h), float(d), float(a)
    except (TypeError, ValueError):
        return None
    if min(h, d, a) <= 1.0:
        return None
    return (h, d, a)


def _fair_probs(o, method):
    """Prob market-implied de-vigged (jumlah = 1)."""
    inv = tuple(1.0 / x for x in o)
    S = sum(inv)
    if method == "mult":
        return tuple(p / S for p in inv)
    if method == "shin":
        # Shin (2003): harga z agar sum p_i = 1
        # q_i = 1/o_i, W = sum(q_i). p_i = (sqrt(z^2+4(1-z) q_i^2/W) - z)/(2(1-z))
        def f(z):
            tot = 0.0
            for q in inv:
                tot += (math.sqrt(z * z + 4 * (1 - z) * q * q / S) - z) / (2 * (1 - z))
            return tot - 1.0
        # f(0) = sqrt(S)-1 > 0; f(0.999) < 0 -> akar unik di (0, 0.999)
        lo, hi = 0.0, 0.999
        if f(lo) <= 0.0 or f(hi) >= 0.0:
            return tuple(p / S for p in inv)
        for _ in range(80):
            mid = (lo + hi) / 2.0
            if f(mid) > 0.0:
                lo = mid
            else:
                hi = mid
        z = (lo + hi) / 2.0
        out = []
        for q in inv:
            out.append((math.sqrt(z * z + 4 * (1 - z) * q * q / S) - z) / (2 * (1 - z)))
        return tuple(out)
    # none -> normalisasi implisit tetap dipakai di pemanggil via 1/o
    return inv


def _write_records_meta(out_path, data_stamp):
    """Tulis sidecar meta records_cache dengan MERGE, bukan timpa.

    File meta dimiliki bersama: cache_records menulis dc_fit_mode +
    data_stamp, sedangkan pipeline_orchestrator menambahkan
    data_fingerprint ke dict yang sama. Menimpa seluruh file di sini
    menghapus fingerprint setiap kali jalur make_picks_live membangun
    ulang records (ia memanggil cache_records langsung), sehingga
    rebuild orchestrator berikutnya terpicu lagi — residu ping-pong
    M2 yang tersisa setelah ronde 6 (audit ronde 7).
    """
    meta_path = os.path.splitext(out_path)[0] + ".meta.json"
    meta = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}
    meta.update({"dc_fit_mode": model_v2.DC_FIT_MODE,
                 "data_stamp": data_stamp})
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)


def cache_records(out_path=RECORDS):
    rows = build_feature_rows(limit=None)
    X, y, dates = mf._rows_to_arrays(rows)
    months = sorted({d[:7] for d in dates})
    odds = _load_hist_odds(os.path.join(BASE, "all_matches_clean.csv"))
    for div in TOP5:
        for k, v in load_fd_odds(div, "2627").items():
            odds.setdefault(k, v.get("b365") or v.get("avg"))

    rec = []
    for m in months:
        train = np.array([d < m + "-01" for d in dates])
        test = np.array([d[:7] == m for d in dates])
        if train.sum() < 1500 or test.sum() == 0:
            continue
        Xtr, ytr = X[train], y[train]
        Xte, yte = X[test], y[test]
        p3 = mf._fit_multinomial(Xtr, ytr, Xte)
        test_rows = [rows[i] for i in np.where(test)[0]]
        dc_cache = {}
        xg_map = _load_xg_map()
        for idx, r in enumerate(test_rows):
            div, dstr = r["div"], r["date"]
            if div not in dc_cache:
                games = [g for g in (
                    (rr["home"], rr["away"], rr["yh"], rr["ya"],
                     xg_map.get(xg_key(div, rr["date"], rr["home"], rr["away"]), (None, None))[0],
                     xg_map.get(xg_key(div, rr["date"], rr["home"], rr["away"]), (None, None))[1],
                     _as_date(rr["date"]))
                    for rr in rows if rr["div"] == div and rr["date"] < m + "-01"
                    and rr["yh"] is not None)]
                mdl = DC()
                try:
                    mdl.fit(games[-4000:], _as_date(m + "-01"), 270.0)
                except Exception:
                    mdl = None
                dc_cache[div] = mdl
            mdl = dc_cache[div]
            if mdl is None:
                continue
            try:
                lh, la = mdl._lam(r["home"], r["away"])
                pr = mdl.probs(lh, la)
            except Exception:
                continue
            p3row = tuple(p3[idx])
            o = odds.get((div, dstr, r["home"], r["away"]))
            rec.append(dict(
                div=div, date=dstr, season=r["season"],
                home=r["home"], away=r["away"], yi=int(yte[idx]),
                ph_dc=pr["ph"], pd_dc=pr["pd"], pa_dc=pr["pa"],
                ph_t3=p3row[0], pd_t3=p3row[1], pa_t3=p3row[2],
                lam_h=lh, lam_a=la, rho=mdl.rho,
                o=_open_dec(o) if o else None,
            ))
    with open(out_path, "w", encoding="utf-8") as f:
        for r in rec:
            f.write(json.dumps(r) + "\n")
    # Stamp mode fit DC + kesegaran data latih yang menghasilkan cache;
    # dipakai _fit_meta utk rebuild. Tanpa stamp data, cache bertahan
    # melewati refresh data mingguan dan model meta diam-diam ter-fit
    # pada data basi (audit ronde 3).
    try:
        st = os.stat(os.path.join(BASE, "all_matches_clean.csv"))
        data_stamp = f"{st.st_mtime_ns}:{st.st_size}"
    except OSError:
        data_stamp = None
    _write_records_meta(out_path, data_stamp)
    print(f"cache records: {len(rec)} -> {out_path} (mode={model_v2.DC_FIT_MODE})")
    return len(rec)


def load_records(path=RECORDS):
    rec = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                r = json.loads(line)
                r["o"] = tuple(r["o"]) if r.get("o") else None
                rec.append(r)
    return rec


def _logit(p):
    p = np.clip(np.asarray(p, dtype=float), 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def _fit_logistic(F, t, iters=40):
    """Logistic regression (intercept+d slope 1 kolom fitur) via Newton."""
    Fb = np.column_stack([np.ones(len(t)), F])
    w = np.zeros(Fb.shape[1])
    for _ in range(iters):
        z = Fb @ w
        p = 1.0 / (1.0 + np.exp(-z))
        g = Fb.T @ (p - t)
        H = (Fb * (p * (1 - p))[:, None]).T @ Fb
        try:
            w -= np.linalg.solve(H + 1e-6 * np.eye(Fb.shape[1]), g)
        except np.linalg.LinAlgError:
            break
    return w


def _recalibrate(records):
    """Walk-forward Platt recalibration per kelas (leak-free), pakai bulan lalu."""
    from collections import defaultdict
    groups = defaultdict(list)
    for i, r in enumerate(records):
        groups[r["date"][:7]].append(i)
    out = [None] * len(records)
    prior = []  # list of ((ph,pd,pa), yi)
    for m in sorted(groups):
        gi = groups[m]
        if len(prior) >= 3000:
            F = np.array([_logit((q[0], q[1], q[2])) for q, _ in prior])
            y = np.array([yi for _, yi in prior])
            W = []
            for k in range(3):
                W.append(_fit_logistic(F, (y == k).astype(float)))
            Fg = np.array([_logit((records[i]["ph_dc"], records[i]["pd_dc"],
                                   records[i]["pa_dc"])) for i in gi])
            for j, i in enumerate(gi):
                s = np.array([W[k][0] + Fg[j] @ W[k][1:] for k in range(3)])
                s -= s.max()
                e = np.exp(s)
                out[i] = tuple(e / e.sum())
        # tambahkan grup ini ke prior
        for i in gi:
            r = records[i]
            prior.append(((r["ph_dc"], r["pd_dc"], r["pa_dc"]), r["yi"]))
    return out


def _model_probs(rec, cfg):
    if cfg["model"] == "meta":
        # "meta" harus berarti model meta yang sebenarnya: ph_meta bila
        # cache sudah diperkaya experiment_meta, selain itu ph_t3 —
        # output multinomial walk-forward yang ditulis cache_records
        # memang model meta itu. Versi lama jatuh per-komponen ke
        # ph_dc, dan records_cache tidak pernah memuat ph_meta, jadi
        # backtest default berlabel 'meta' diam-diam mengukur DC murni
        # (audit ronde 3).
        if rec.get("ph_meta"):
            return (rec["ph_meta"],
                    rec.get("pd_meta") or rec["pd_t3"],
                    rec.get("pa_meta") or rec["pa_t3"])
        return (rec["ph_t3"], rec["pd_t3"], rec["pa_t3"])
    if cfg["model"] == "t3":
        return (rec["ph_t3"], rec["pd_t3"], rec["pa_t3"])
    if cfg["model"] == "blend":
        w = cfg["blend_w"]
        return (w * rec["ph_t3"] + (1 - w) * rec["ph_dc"],
                w * rec["pd_t3"] + (1 - w) * rec["pd_dc"],
                w * rec["pa_t3"] + (1 - w) * rec["pa_dc"])
    return (rec["ph_dc"], rec["pd_dc"], rec["pa_dc"])


def _iter_bets(records, cfg):
    """Yield per-bet tick: (idx, im, od, edge, stake, profit)."""
    calib = _recalibrate(records) if cfg.get("calib") == "platt" else None
    for idx, rec in enumerate(records):
        pm = _model_probs(rec, cfg)
        if calib is not None and calib[idx] is not None:
            pm = calib[idx]
        o = rec["o"]
        if o is None:
            continue
        imp = [1.0 / x for x in o]
        if cfg["devig"] in ("mult", "shin"):
            fair = _fair_probs(o, cfg["devig"])
            imp = list(fair)
        for im in SIDES:
            od = o[im]
            edge = pm[im] - imp[im]
            if edge <= cfg["thr"]:
                continue
            if cfg["stake"] == "kelly":
                f = (pm[im] * od - 1.0) / (od - 1.0)
                if f <= 0:
                    continue
                stake = min(cfg["kelly"] * f, 0.5)
            else:
                stake = 1.0
            profit = stake * (od - 1.0) if im == rec["yi"] else -stake
            yield idx, im, od, edge, stake, profit


def evaluate_strategy(records, cfg):
    calib = _recalibrate(records) if cfg.get("calib") == "platt" else None
    pairs = []
    bet = {"n": 0, "wins": 0, "staked": 0.0, "profit": 0.0}
    for idx, rec in enumerate(records):
        pm = _model_probs(rec, cfg)
        if calib is not None and calib[idx] is not None:
            pm = calib[idx]
        pairs.append((pm, rec["yi"]))
    for idx, im, od, edge, stake, profit in _iter_bets(records, cfg):
        bet["n"] += 1
        bet["staked"] += stake
        if profit > 0:
            bet["wins"] += 1
        bet["profit"] += profit
    met = eval_1x2(pairs)
    res = {
        "n_bets": bet["n"],
        "wins": bet["wins"],
        "staked": bet["staked"],
        "profit": bet["profit"],
        "hit_rate": bet["wins"] / bet["n"] if bet["n"] else 0.0,
        "yield": bet["profit"] / bet["staked"] if bet["staked"] else 0.0,
        "log_loss": met["log_loss"],
        "brier": met["brier"],
        "macro_f1": met["macro_f1"],
        "accuracy": met["accuracy"],
        "n_eval": met["n"],
    }
    return res


TOP5 = {"E0", "D1", "I1", "SP1", "F1"}


def _div_group(rec):
    return "top5" if rec.get("div") in TOP5 else "other"


def _odds_bucket(od):
    if od < 1.5:
        return "<1.5"
    if od < 2.0:
        return "1.5-2.0"
    if od < 2.6:
        return "2.0-2.6"
    if od < 3.5:
        return "2.6-3.5"
    return ">=3.5"


def segment_sweep(records, cfg, min_bets=500):
    """Evaluasi ROI per segmen (liga/odds/edge). Print segmen yang n >= min_bets."""
    from collections import defaultdict
    totals = defaultdict(lambda: {"n": 0, "staked": 0.0, "profit": 0.0})
    for idx, im, od, edge, stake, profit in _iter_bets(records, cfg):
        rec = records[idx]
        for key in (
            ("div", _div_group(rec)),
            ("odds", _odds_bucket(od)),
            ("edge", f">={edge:.2f}"),
            ("div|odds", (_div_group(rec), _odds_bucket(od))),
        ):
            t = totals[key]
            t["n"] += 1
            t["staked"] += stake
            t["profit"] += profit
    print("=" * 78)
    print("SEGMENT SWEEP (ROI per segmen) — n_min =", min_bets)
    print("=" * 78)
    print(f"{'segmen':28} {'n':>7} {'yield':>9} {'n_w':>6}")
    rows = []
    for (dim, seg), t in totals.items():
        if t["n"] < min_bets:
            continue
        yield_ = t["profit"] / t["staked"] if t["staked"] else 0.0
        rows.append((dim, seg, t["n"], yield_))
    rows.sort(key=lambda r: -r[3])
    for dim, seg, n, yield_ in rows:
        flag = "  <<< POSITIVE" if yield_ > 0 else ""
        print(f"{f'{dim}={seg}':28} {n:>7} {yield_:>9.4%} {flag}")
    return rows


# Phase 5: Filtered Value Bet Strategy (validated positive pocket)
# Top5 leagues, heavy home favorite odds 1.2-1.5, model edge in [0.20, 0.22).
FILTER_CFG = {
    "divs": {"E0", "D1", "I1", "SP1", "F1"},
    "odds_lo": 1.2,
    "odds_hi": 1.5,
    "edge_lo": 0.20,
    "edge_hi": 0.22,
}


def evaluate_filtered(records, cfg, kelly=False):
    """Evaluasi strategi Filtered Value Bet (segmen positif tervalidasi)."""
    c = dict(cfg); c["stake"] = "kelly" if kelly else "flat"
    bet = {"n": 0, "wins": 0, "staked": 0.0, "profit": 0.0}
    for idx, im, od, edge, stake, profit in _iter_bets(records, c):
        rec = records[idx]
        if rec.get("div") not in FILTER_CFG["divs"]:
            continue
        if not (FILTER_CFG["odds_lo"] <= od <= FILTER_CFG["odds_hi"]):
            continue
        if not (FILTER_CFG["edge_lo"] <= edge < FILTER_CFG["edge_hi"]):
            continue
        bet["n"] += 1
        bet["staked"] += stake
        if profit > 0:
            bet["wins"] += 1
        bet["profit"] += profit
    res = {
        "n_bets": bet["n"],
        "wins": bet["wins"],
        "staked": bet["staked"],
        "profit": bet["profit"],
        "hit_rate": bet["wins"] / bet["n"] if bet["n"] else 0.0,
        "yield": bet["profit"] / bet["staked"] if bet["staked"] else 0.0,
    }
    return res


def report(res, baseline=None):
    print("=" * 70)
    print("BACKTEST VALUE-BET 1X2 (config evaluasi)")
    print("=" * 70)
    print(f"n eval match : {res['n_eval']}")
    print(f"n bet       : {res['n_bets']}")
    print(f"staked      : {res['staked']:.1f}")
    print(f"profit      : {res['profit']:.2f}")
    print(f"hit rate    : {res['hit_rate']:.4f}")
    print(f"yield (ROI): {res['yield']:.4%}")
    print(f"log loss    : {res['log_loss']:.4f}")
    print(f"brier       : {res['brier']:.4f}")
    print(f"macro_f1    : {res['macro_f1']:.4f}")
    print(f"accuracy    : {res['accuracy']:.4f}")
    if baseline:
        print("-" * 70)
        print(f"baseline     : yield {baseline['yield']:.4%} | "
              f"logloss {baseline['log_loss']:.4f} | "
              f"brier {baseline['brier']:.4f} | "
              f"F1 {baseline['macro_f1']:.4f}")
        d_y = res["yield"] - baseline["yield"]
        d_ll = res["log_loss"] - baseline["log_loss"]
        verdict = "MENANG (yield naik)" if d_y > 0 and d_ll < 0.01 else (
            "MENANG (yield naik, logloss sekadar)" if d_y > 0 else "KALAH")
        print(f"delta yield  : {d_y:.4%} | delta logloss: {d_ll:+.4f}")
        print(f"verdict      : {verdict}")
    print()


def main():
    cfg = dict(DEFAULT_CFG)
    args = sys.argv[1:]
    if "--cache-only" in args:
        cache_records()
        return
    if "--model" in args:
        cfg["model"] = args[args.index("--model") + 1]
    if "--blend-w" in args:
        cfg["blend_w"] = float(args[args.index("--blend-w") + 1])
    if "--devig" in args:
        cfg["devig"] = args[args.index("--devig") + 1]
    if "--thr" in args:
        cfg["thr"] = float(args[args.index("--thr") + 1])
    if "--stake" in args:
        cfg["stake"] = args[args.index("--stake") + 1]
    if "--kelly" in args and args.index("--kelly") + 1 < len(args) \
            and args[args.index("--kelly") + 1].replace(".", "").replace("-", "").isdigit():
        cfg["kelly"] = float(args[args.index("--kelly") + 1])
    if "--calib" in args:
        cfg["calib"] = args[args.index("--calib") + 1]
    if not os.path.exists(RECORDS):
        cache_records()
    records = load_records()
    if "--segment" in args:
        segment_sweep(records, cfg)
        return
    if "--filter" in args:
        kelly = "--kelly" in args
        r = evaluate_filtered(records, cfg, kelly=kelly)
        print("=" * 70)
        print("FILTERED VALUE BET STRATEGY (top5 heavy favorite, edge 0.20-0.22)")
        print("=" * 70)
        print(f"stake       : {'kelly' if kelly else 'flat'}")
        print(f"n bet       : {r['n_bets']}")
        print(f"hit rate    : {r['hit_rate']:.4f}")
        print(f"yield (ROI): {r['yield']:.4%}")
        return
    res = evaluate_strategy(records, cfg)
    report(res)


if __name__ == "__main__":
    main()
