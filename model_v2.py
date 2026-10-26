"""v2: DC + blend odds pembukaan + tuning knob (half-life, frekuensi fit).
Tahap A (validasi 19/20-20/21): pilih HL, freq, w_1x2, w_ou -> v2_config.json
Tahap B (test 21/22-25/26): walk-forward final, output pure + blended.
Usage: python model_v2.py [val|final|all]"""
import os
import sys
import csv
import json
import math
import time
from collections import defaultdict
from datetime import datetime

# Konvensi kanonik untuk probabilitas & blending (lihat football_etl).
from football_etl import pois, tau, norm3, norm2, blend3, blend2
from paths import BASE

DATA = os.path.join(BASE, "all_matches_clean.csv")
CFG = os.path.join(BASE, "v2_config.json")
OUT = os.path.join(BASE, "predictions_v2.csv")
TOP5 = ["E0", "D1", "I1", "SP1", "F1"]
VAL_SEASONS = {"2019/20", "2020/21"}
TEST_SEASONS = {"2021/22", "2022/23", "2023/24", "2024/25", "2025/26"}
MAXG = 10
MAX_TRAIN = 4000
RHO_GRID = (0.0, -0.05, -0.10, -0.15)
W_GRID = [0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6]
EPS = 1e-9


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


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
            yh, ya = num(r["FTHG"]), num(r["FTAG"])
            if yh is None or ya is None:
                continue
            loaded.append({
                "div": r["Div"], "date": datetime.strptime(r["Date"], "%Y-%m-%d").date(),
                "season": r["Season"], "home": r["HomeTeam"], "away": r["AwayTeam"],
                "yh": int(yh), "ya": int(ya), "ftr": r["FTR"],
                "close": (num(r["PSCH"]), num(r["PSCD"]), num(r["PSCA"])),
                "avgc": (num(r["AvgCH"]), num(r["AvgCD"]), num(r["AvgCA"])),
                "b365c": (num(r["B365CH"]), num(r["B365CD"]), num(r["B365CA"])),
                "open": (num(r["AvgH"]), num(r["AvgD"]), num(r["AvgA"])),
                "open_b365": (num(r["B365H"]), num(r["B365D"]), num(r["B365A"])),
                "ou_c": (num(r["AvgC>2.5"]), num(r["AvgC<2.5"])),
                "ou_o": (num(r["Avg>2.5"]), num(r["Avg<2.5"])),
                "ou_o_b365": (num(r["B365>2.5"]), num(r["B365<2.5"])),
                "ahh": num(r["AHh"]),
                "ah_c": (num(r["AvgCAHH"]), num(r["AvgCAHA"])),
            })
    loaded.sort(key=lambda m: m["date"])
    bd = defaultdict(list)
    for i, m in enumerate(loaded):
        bd[m["div"]].append(i)
    matches = loaded
    by_div = bd


def closing1x2(m):
    for o in (m["close"], m["avgc"], m["b365c"]):
        p = norm3(o)
        if p:
            return p
    return None


def opening1x2(m):
    p = norm3(m["open"])
    return p or norm3(m["open_b365"])


def closing_ou(m):
    return norm2(m["ou_c"])


def opening_ou(m):
    return norm2(m["ou_o"]) or norm2(m["ou_o_b365"])


def market_ah(m):
    oh, oa = m["ah_c"]
    if oh and oa and oh > 1 and oa > 1:
        ih, ia = 1 / oh, 1 / oa
        return ih / (ih + ia)
    return None


class DC:
    def __init__(self):
        self.a = defaultdict(float)
        self.d = defaultdict(float)
        self.h = 0.28
        self.rho = -0.07

    def _lam(self, hi, ai):
        return (math.exp(self.a[hi] + self.d[ai] + self.h),
                math.exp(self.a[ai] + self.d[hi]))

    def fit(self, games, cutoff, hl):
        games = games[-MAX_TRAIN:]
        for sweep in range(14):
            obs_att = defaultdict(float); exp_att = defaultdict(float)
            obs_def = defaultdict(float); exp_def = defaultdict(float)
            sh_obs = sh_exp = 0.0
            for hi, ai, yh, ya, dt in games:
                w = 0.5 ** ((cutoff - dt).days / hl)
                lh = math.exp(self.a[hi] + self.d[ai] + self.h)
                la = math.exp(self.a[ai] + self.d[hi])
                obs_att[hi] += w * yh; exp_att[hi] += w * lh
                obs_att[ai] += w * ya; exp_att[ai] += w * la
                obs_def[ai] += w * yh; exp_def[ai] += w * lh
                obs_def[hi] += w * ya; exp_def[hi] += w * la
                sh_obs += w * yh; sh_exp += w * lh
            for t in set(obs_att) | set(exp_att):
                self.a[t] += 0.7 * math.log((obs_att[t] + 0.25) / (exp_att[t] + 0.25))
            for t in set(obs_def) | set(exp_def):
                self.d[t] += 0.7 * math.log((obs_def[t] + 0.25) / (exp_def[t] + 0.25))
            self.h += 0.7 * math.log((sh_obs + 0.25) / (sh_exp + 0.25))
        best_rho, best_ll = RHO_GRID[0], None
        for rho in RHO_GRID:
            ll = 0.0
            for hi, ai, yh, ya, dt in games:
                if yh <= 1 or ya <= 1:
                    w = 0.5 ** ((cutoff - dt).days / hl)
                    lh = math.exp(self.a[hi] + self.d[ai] + self.h)
                    la = math.exp(self.a[ai] + self.d[hi])
                    t = tau(yh, ya, lh, la, rho)
                    if t > 0:
                        ll += w * math.log(t)
            if best_ll is None or ll > best_ll:
                best_ll, best_rho = ll, rho
        self.rho = best_rho

    def probs(self, lh, la):
        m = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, self.rho)
              for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        s = sum(sum(row) for row in m)
        ph = sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1) if x > y) / s
        pd = sum(m[x][x] for x in range(MAXG + 1)) / s
        p_over = sum(m[x][y] for x in range(MAXG + 1) for y in range(MAXG + 1)
                     if x + y > 2) / s
        p0h = sum(m[0][y] for y in range(MAXG + 1)) / s
        p0a = sum(m[x][0] for x in range(MAXG + 1)) / s
        p_btts = 1.0 - p0h - p0a + m[0][0] / s
        return {"ph": ph, "pd": pd, "pa": 1 - ph - pd,
                "over": p_over, "btts": p_btts}

    def ah_probs(self, lh, la, line):
        m = [[pois(x, lh) * pois(y, la) * tau(x, y, lh, la, self.rho)
              for y in range(MAXG + 1)] for x in range(MAXG + 1)]
        s = sum(sum(row) for row in m)
        win = push = 0.0
        for x in range(MAXG + 1):
            for y in range(MAXG + 1):
                v = x - y + line
                if v > 0:
                    win += m[x][y]
                elif v == 0:
                    push += m[x][y]
        return win / s, push / s, 1 - win / s - push / s


def brier3(p, yi):
    return sum((p[k] - (1.0 if k == yi else 0.0)) ** 2 for k in range(3))


YIDX = {"H": 0, "D": 1, "A": 2}


def run_wf(seasons, hl, freq, with_extra=False):
    """Walk-forward utk daftar musim. freq: 'm' bulanan | 'w' mingguan.
    with_extra: tambahkan AH & market cols (untuk final)."""
    _ensure_loaded()
    models = {d: DC() for d in TOP5}
    ptr = {d: 0 for d in TOP5}
    games_hist = {d: [] for d in TOP5}
    groups = defaultdict(list)
    for i, m in enumerate(matches):
        if m["season"] in seasons:
            if freq == "m":
                key = (m["div"], m["date"].year, m["date"].month)
            else:
                iso = m["date"].isocalendar()
                key = (m["div"], iso[0], iso[1])
            groups[key].append(i)
    rows = []
    t0 = time.time()
    nfits = 0
    for key in sorted(groups):
        idxs = groups[key]
        start = min(matches[i]["date"] for i in idxs)
        # Anti-leakage: seluruh match dalam grup test ini berada setelah training.
        assert all(matches[i]["date"] >= start for i in idxs), "leakage dalam grup test"
        div = key[0]
        lst = by_div[div]
        while ptr[div] < len(lst) and matches[lst[ptr[div]]]["date"] < start:
            j = lst[ptr[div]]
            mm = matches[j]
            games_hist[div].append((mm["home"], mm["away"], mm["yh"], mm["ya"], mm["date"]))
            ptr[div] += 1
        model = models[div]
        if games_hist[div]:
            model.fit(games_hist[div], start, hl)
            nfits += 1
        for i in idxs:
            mm = matches[i]
            lh, la = model._lam(mm["home"], mm["away"])
            pr = model.probs(lh, la)
            row = {"i": i, "div": div, "date": mm["date"].isoformat(),
                   "season": mm["season"], "home": mm["home"], "away": mm["away"],
                   "ftr": mm["ftr"], "yh": mm["yh"], "ya": mm["ya"],
                   "lamh": lh, "lama": la, "pr": pr}
            if with_extra:
                row["ahh"] = mm["ahh"]
                row["mkt_close"] = closing1x2(mm)
                row["mkt_open"] = opening1x2(mm)
                row["mkt_ou_c"] = closing_ou(mm)
                row["mkt_ou_o"] = opening_ou(mm)
                row["mkt_ah"] = market_ah(mm)
                if mm["ahh"] is not None:
                    row["pw"], row["pp"], _ = model.ah_probs(lh, la, mm["ahh"])
                else:
                    row["pw"] = row["pp"] = None
            rows.append(row)
    print(f"  [wf seasons={sorted(seasons)} hl={hl} freq={freq}] "
          f"fits={nfits} pred={len(rows):,} waktu={time.time()-t0:.0f}s")
    return rows


def evaluate_1x2(rows):
    agg = defaultdict(float)
    cnt = defaultdict(int)
    for r in rows:
        yi = YIDX[r["ftr"]]
        p = (r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"])
        agg["dc"] += brier3(p, yi)
        agg["acc"] += max(range(3), key=lambda k: p[k]) == yi
        cnt["n"] += 1
        if r.get("mkt_close"):
            agg["close"] += brier3(r["mkt_close"], yi)
            cnt["nc"] += 1
        if r.get("mkt_open"):
            agg["open"] += brier3(r["mkt_open"], yi)
            cnt["no"] += 1
    return agg, cnt


def main_val():
    _ensure_loaded()
    print("=== TAHAP A: validasi (2019/20-2020/21) ===")
    results = {}
    for hl in (270, 540, 900):
        for freq in ("m", "w"):
            key = f"hl{hl}_{freq}"
            rows = run_wf(VAL_SEASONS, hl, freq)
            results[key] = rows
    print("\n-- grid knob (1X2 Brier, validasi) --")
    best_key, best_b = None, None
    for key, rows in results.items():
        agg, cnt = evaluate_1x2(rows)
        b = agg["dc"] / max(cnt["n"], 1)
        print(f"{key:12s} n={cnt['n']:6,d} Brier DC {b:.4f} | closing {agg['close']/max(cnt['nc'],1):.4f} | opening {agg['open']/max(cnt['no'],1):.4f}")
        if best_b is None or b < best_b:
            best_key, best_b = key, b
    hl, freq = best_key.replace("hl", "").split("_")
    hl, freq = int(hl), freq
    print(f"knob terpilih: {best_key}")
    # grid w blend pada knob terpilih (butuh kolom odds -> ulangi wf dgn with_extra)
    rows = run_wf(VAL_SEASONS, hl, freq, with_extra=True)
    print("\n-- grid w blend (validasi) --")
    so = no_ = 0.0
    sc = nc_ = 0.0
    for r in rows:
        yi = YIDX[r["ftr"]]
        if r.get("mkt_open"):
            so += brier3(r["mkt_open"], yi)
            no_ += 1
        if r.get("mkt_close"):
            sc += brier3(r["mkt_close"], yi)
            nc_ += 1
    print(f"referensi: opening sendirian {so/max(no_,1):.4f} (n={no_:,}) | "
          f"closing sendirian {sc/max(nc_,1):.4f} (n={nc_:,})")
    for w in W_GRID:
        s1 = s0 = n1 = n0 = s_ou = n_ou = 0.0
        for r in rows:
            yi = YIDX[r["ftr"]]
            if r.get("mkt_open"):
                pb = blend3((r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"]), r["mkt_open"], w)
                s1 += brier3(pb, yi)
                n1 += 1
        print(f"w={w:.1f} Brier blend 1X2 {s1/max(n1,1):.4f} (n={n1:,})")
    best_w, best_wb = None, None
    for w in W_GRID:
        s1 = n1 = 0.0
        for r in rows:
            yi = YIDX[r["ftr"]]
            if r.get("mkt_open"):
                pb = blend3((r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"]), r["mkt_open"], w)
                s1 += brier3(pb, yi)
                n1 += 1
        b = s1 / max(n1, 1)
        if best_wb is None or b < best_wb:
            best_w, best_wb = w, b
    best_wou, best_woub = None, None
    for w in W_GRID:
        s2 = n2 = 0.0
        for r in rows:
            mo = r.get("mkt_ou_o")
            if mo is None:
                continue
            yv = 1.0 if r["yh"] + r["ya"] > 2 else 0.0
            po = blend2(r["pr"]["over"], mo, w)
            s2 += (po - yv) ** 2
            n2 += 1
        b = s2 / max(n2, 1)
        if best_woub is None or b < best_woub:
            best_wou, best_woub = w, b
        print(f"w_ou={w:.1f} Brier blend OU {b:.4f} (n={n2:,})")
    print(f"→ w_1x2={best_w} (Brier {best_wb:.4f}) | w_ou={best_wou} (Brier {best_woub:.4f})")
    cfg = {"hl": hl, "freq": freq, "w_1x2": best_w, "w_ou": best_wou}
    with open(CFG, "w") as f:
        json.dump(cfg, f)
    print("config tersimpan:", CFG)


def main_final():
    _ensure_loaded()
    print("=== TAHAP B: test final (2021/22-2025/26) ===")
    with open(CFG) as f:
        cfg = json.load(f)
    print("config:", cfg)
    rows = run_wf(TEST_SEASONS, cfg["hl"], cfg["freq"], with_extra=True)
    w, wou = cfg["w_1x2"], cfg["w_ou"]
    agg = defaultdict(float)
    cnt = defaultdict(int)
    ah = {"ahm": 0.0, "ahmm": 0.0, "nah": 0, "nahm": 0}
    bt = 0.0
    bh = 0
    out_rows = []
    for r in rows:
        yi = YIDX[r["ftr"]]
        pdc = (r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"])
        pb = blend3(pdc, r["mkt_open"], w) if r["mkt_open"] else None
        agg["dc"] += brier3(pdc, yi)
        agg["acc"] += max(range(3), key=lambda k: pdc[k]) == yi
        if pb:
            agg["bl"] += brier3(pb, yi)
            agg["accbl"] += max(range(3), key=lambda k: pb[k]) == yi
            cnt["nbl"] += 1
        if r["mkt_close"]:
            agg["close"] += brier3(r["mkt_close"], yi)
            agg["accc"] += max(range(3), key=lambda k: r["mkt_close"][k]) == yi
            cnt["nc"] += 1
        if r["mkt_open"]:
            agg["open"] += brier3(r["mkt_open"], yi)
            cnt["no"] += 1
        cnt["n"] += 1
        yv = 1.0 if r["yh"] + r["ya"] > 2 else 0.0
        agg["ou_dc"] += (r["pr"]["over"] - yv) ** 2
        cnt["nou"] += 1
        pob = blend2(r["pr"]["over"], r["mkt_ou_o"], wou) if r["mkt_ou_o"] else None
        if pob is not None:
            agg["ou_bl"] += (pob - yv) ** 2
            cnt["noubl"] += 1
        if r["mkt_ou_c"] is not None:
            agg["ou_c"] += (r["mkt_ou_c"] - yv) ** 2
            cnt["nouc"] += 1
        yb = 1.0 if r["yh"] > 0 and r["ya"] > 0 else 0.0
        bt += (r["pr"]["btts"] - yb) ** 2
        bh += yb
        if r["ahh"] is not None and r.get("pw") is not None:
            diff = r["yh"] - r["ya"] + r["ahh"]
            if diff != 0:
                yc = 1.0 if diff > 0 else 0.0
                zh = r["pw"] / max(r["pw"] + (1 - r["pw"] - r["pp"]), EPS)
                ah["ahm"] += (zh - yc) ** 2
                ah["nah"] += 1
                if r["mkt_ah"] is not None:
                    ah["ahmm"] += (r["mkt_ah"] - yc) ** 2
                    ah["nahm"] += 1
        out_rows.append({
            "div": r["div"], "date": r["date"], "season": r["season"],
            "home": r["home"], "away": r["away"], "ftr": r["ftr"],
            "yh": r["yh"], "ya": r["ya"],
            "lam_h": round(r["lamh"], 3), "lam_a": round(r["lama"], 3),
            "ph_dc": round(pdc[0], 4), "pd_dc": round(pdc[1], 4), "pa_dc": round(pdc[2], 4),
            "ph_bl": None if pb is None else round(pb[0], 4),
            "pd_bl": None if pb is None else round(pb[1], 4),
            "pa_bl": None if pb is None else round(pb[2], 4),
            "p_over_dc": round(r["pr"]["over"], 4),
            "p_over_bl": None if pob is None else round(pob, 4),
            "p_btts": round(r["pr"]["btts"], 4),
            "ahh": r["ahh"],
            "p_ah_home": None if r.get("pw") is None else round(r["pw"], 4),
            "p_ah_push": None if r.get("pp") is None else round(r["pp"], 4),
            "mkt_ph": None if not r["mkt_close"] else round(r["mkt_close"][0], 4),
            "mkt_pd": None if not r["mkt_close"] else round(r["mkt_close"][1], 4),
            "mkt_pa": None if not r["mkt_close"] else round(r["mkt_close"][2], 4),
            "mkt_open_ph": None if not r["mkt_open"] else round(r["mkt_open"][0], 4),
            "mkt_open_pd": None if not r["mkt_open"] else round(r["mkt_open"][1], 4),
            "mkt_open_pa": None if not r["mkt_open"] else round(r["mkt_open"][2], 4),
            "mkt_ou": None if r["mkt_ou_c"] is None else round(r["mkt_ou_c"], 4),
            "mkt_ah": None if r["mkt_ah"] is None else round(r["mkt_ah"], 4),
        })
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        wcsv = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        wcsv.writeheader()
        wcsv.writerows(out_rows)
    print("tersimpan:", OUT)
    n, nbl, nc = cnt["n"], cnt["nbl"], cnt["nc"]
    print("\n-- 1X2 (2021/22-2025/26) --")
    print(f"DC pure    : {agg['dc']/n:.4f} (acc {agg['acc']/n*100:.1f}%) n={n:,}")
    print(f"blended    : {agg['bl']/max(nbl,1):.4f} (acc {agg['accbl']/max(nbl,1)*100:.1f}%) n={nbl:,} w={w}")
    print(f"closing mkt: {agg['close']/max(nc,1):.4f} (acc {agg['accc']/max(nc,1)*100:.1f}%) n={nc:,}")
    print(f"opening mkt: {agg['open']/max(cnt['no'],1):.4f} n={cnt['no']:,}")
    print("\n-- O/U 2.5 --")
    print(f"DC pure    : {agg['ou_dc']/cnt['nou']:.4f} n={cnt['nou']:,}")
    print(f"blended    : {agg['ou_bl']/max(cnt['noubl'],1):.4f} n={cnt['noubl']:,} w_ou={wou}")
    print(f"closing mkt: {agg['ou_c']/max(cnt['nouc'],1):.4f} n={cnt['nouc']:,}")
    print("\n-- BTTS (pure, vs base-rate) --")
    print(f"model {bt/n:.4f} | base {bh/n*(1-bh/n):.4f} | hit {bh/n*100:.1f}%")
    print("\n-- AH (pure, push dikecualikan) --")
    print(f"model {ah['ahm']/max(ah['nah'],1):.4f} | market {ah['ahmm']/max(ah['nahm'],1):.4f} | n={ah['nah']:,}")

    # Evaluasi proper scoring + per-kelas (draw = kelas paling sulit).
    from validation import eval_1x2, calibration_table
    pairs = [((r["pr"]["ph"], r["pr"]["pd"], r["pr"]["pa"]), YIDX[r["ftr"]])
             for r in rows]
    sm = eval_1x2(pairs)
    print("\n-- 1X2 proper scoring (DC pure) --")
    print(f"Brier {sm['brier']:.4f} | logloss {sm['log_loss']:.4f} | "
          f"acc {sm['accuracy']*100:.1f}% | n={sm['n']:,}")
    for k in ("H", "D", "A"):
        print(f"  logloss {k}: {sm['per_class_log_loss'][k]:.4f} "
              f"(n={sm['per_class_n'][k]})")
    cal = calibration_table([(r["pr"]["ph"], int(r["ftr"] == "H"))
                             for r in rows if r["pr"]["ph"] > 0.5])
    print("  kalibrasi P(home) untuk laga favorit kandang:")
    for lo, hi, n_, mp, fr in cal:
        print(f"    [{lo:.1f},{hi:.1f}) n={n_:>5d} pred={mp:.3f} akt={fr:.3f}")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    if phase in ("val", "all"):
        main_val()
    if phase in ("final", "all"):
        main_final()
