"""G-DK1 goals engine: production Dixon-Coles pattern (dc.py, ported from
DK-Superligaen/J1), goals-only observation (no xG exists in this league).
Arms: gate_zero; shrink (arms.py, sanctioned thin-data prior); x2 mover
transplant — for a team arriving from DK-Superligaen whose DK1 training
count is <12, its DC attack/defence ratings are blended toward the ratings
it earned in a DC fit on the parent tier's immediately preceding season
(same FotMob team ids), weight w = (12-n)/12 * min(1, n_parent/20).
Usage: run_g_dk1.py dev|virgin"""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from dc import DC
from arms import adjusted_lambdas, match_counts
from common_dk1 import load, PARENT, VIRGIN, bll, agg, calib_verdict, write_json

SEED = "2021/2022"; SCORED = ("2022/2023", "2023/2024", "2024/2025")
ARMS = ("gate_zero", "shrink", "x2")

def games(rows):
    return [{"hi": m["home_id"], "ai": m["away_id"], "yh": m["gh"], "ya": m["ga"],
             "date": m["date"], "home": m["home"], "away": m["away"],
             "xgh": None, "xga": None} for m in rows]

def parent_games(season):
    out = []
    with PARENT.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] != season: continue
            from datetime import date
            out.append({"hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                        "yh": int(float(r["home_goals"])), "ya": int(float(r["away_goals"])),
                        "date": date.fromisoformat(r["date"]), "home": r["home_team"],
                        "away": r["away_team"], "xgh": None, "xga": None})
    return out

def prev_season(s):
    a, b = s.split("/"); return f"{int(a)-1}/{int(b)-1}"

def x2_ratings(train_rows, season, base_model):
    """Returns (a_blend, d_blend, n_movers, n_parent_matches)."""
    pg = parent_games(prev_season(season))
    if not pg: return {}, {}, 0, 0
    pm = DC().fit(pg, max(g["date"] for g in pg))
    counts = match_counts(games(train_rows))
    pcounts = match_counts(pg)
    a_bl, d_bl = {}, {}
    movers = 0
    for t in set(counts) | set(pcounts):
        n = counts.get(t, 0)
        if t in pcounts and pcounts[t] >= 10 and n < 12:
            w = (12 - n) / 12.0 * min(1.0, pcounts[t] / 20.0)
            if w > 0:
                a_bl[t] = (1 - w) * base_model.a[t] + w * pm.a[t]
                d_bl[t] = (1 - w) * base_model.d[t] + w * pm.d[t]
                movers += 1
    return a_bl, d_bl, movers, len(pg)

def rps(ph, pd, pa, y):
    c1, c2 = ph, ph + pd
    t1 = 1.0 if y == 0 else 0.0; t2 = 1.0 if y <= 1 else 0.0
    return ((c1 - t1) ** 2 + (c2 - t2) ** 2) / 2.0

def score_season(model, rows, season, counts, x2ab):
    out = {a: [] for a in ARMS}; out["__clim"] = []
    prior = [m for m in rows if m["season"] < season]
    ph_r = sum(1 for m in prior if m["gh"] > m["ga"]) / len(prior)
    pd_r = sum(1 for m in prior if m["gh"] == m["ga"]) / len(prior)
    pa_r = 1 - ph_r - pd_r
    ou_r = sum(1 for m in prior if m["gh"] + m["ga"] > 2.5) / len(prior)
    for m in [x for x in rows if x["season"] == season]:
        y = 0 if m["gh"] > m["ga"] else (1 if m["gh"] == m["ga"] else 2)
        yo = 1 if m["gh"] + m["ga"] > 2.5 else 0
        for arm in ARMS:
            if arm == "gate_zero":
                lh, la = model.lambdas(m["home_id"], m["away_id"])
            elif arm == "shrink":
                lh, la = adjusted_lambdas(model, m["home_id"], m["away_id"], "shrink", set(), None, counts)
            else:
                lh, la = model.lambdas(m["home_id"], m["away_id"])
                a_bl, d_bl = x2ab
                if m["home_id"] in a_bl or m["away_id"] in a_bl:
                    ah = a_bl.get(m["home_id"], model.a[m["home_id"]]); da = d_bl.get(m["away_id"], model.d[m["away_id"]])
                    aa = a_bl.get(m["away_id"], model.a[m["away_id"]]); dh = d_bl.get(m["home_id"], model.d[m["home_id"]])
                    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
            p = model.probs(lh, la)
            out[arm].append({"match_id": m["match_id"], "season": season, "ph": p["ph"], "pd": p["pd"],
                             "pa": p["pa"], "p_over25": p["over25"], "y": y, "yo": yo,
                             "lh": lh, "la": la, "home": m["home"], "away": m["away"], "gh": m["gh"], "ga": m["ga"],
                             "date": m["date"].isoformat()})
        out["__clim"].append({"match_id": m["match_id"], "season": season, "ph": ph_r, "pd": pd_r,
                              "pa": pa_r, "p_over25": ou_r, "y": y, "yo": yo})
    return out

def summarize(recs):
    def met(rs):
        ll = sum(-math.log(max((r["ph"], r["pd"], r["pa"])[r["y"]], 1e-12)) for r in rs) / len(rs)
        rp = sum(rps(r["ph"], r["pd"], r["pa"], r["y"]) for r in rs) / len(rs)
        ou = agg([(r["p_over25"], r["yo"]) for r in rs])
        hw = agg([(r["ph"], 1 if r["y"] == 0 else 0) for r in rs])
        return {"n": len(rs), "ll_1x2": ll, "rps": rp, "ou25_ll": ou["ll"],
                "ou25_calibration_pp": ou["calibration_pp"], "ou25_calibration_se_pp": ou["calibration_se_pp"],
                "home_win_calibration_pp": hw["calibration_pp"], "home_win_calibration_se_pp": hw["calibration_se_pp"]}
    return met

def run_phase(phase):
    seasons = (SEED,) + SCORED if phase == "dev" else (SEED,) + SCORED + (VIRGIN,)
    rows = load(seasons)
    targets = SCORED if phase == "dev" else (VIRGIN,)
    all_recs = {a: [] for a in ARMS + ("__clim",)}
    perseas = {a: {} for a in ARMS + ("__clim",)}
    x2_info = {}
    pred_rows = []
    for S in targets:
        train = [m for m in rows if m["date"] < min(x["date"] for x in rows if x["season"] == S)]
        model = DC().fit(games(train), min(x["date"] for x in rows if x["season"] == S))
        counts = match_counts(games(train))
        x2ab = x2_ratings(train, S, model)
        x2_info[S] = {"movers_blended": x2ab[2], "parent_matches": x2ab[3]}
        recs = score_season(model, rows, S, counts, (x2ab[0], x2ab[1]))
        met = summarize(recs["gate_zero"])
        for a in ARMS + ("__clim",):
            perseas[a][S] = met(recs[a]); all_recs[a] += recs[a]
            if a in ARMS:
                pred_rows += [dict(r, arm=a) for r in recs[a]]
    out = {"protocol": {"phase": phase, "seed": SEED, "scored": list(targets), "x2_info": x2_info},
           "arms": {}, "climatology": {}}
    for a in ARMS:
        out["arms"][a] = {"seasons": perseas[a], "pooled": summarize(all_recs[a])(all_recs[a])}
    out["climatology"] = {"seasons": perseas["__clim"], "pooled": summarize(all_recs["__clim"])(all_recs["__clim"])}
    if phase == "dev":
        base = out["climatology"]["pooled"]
        for a in ARMS:
            p = out["arms"][a]["pooled"]
            out["arms"][a]["dev_pass"] = p["ll_1x2"] < base["ll_1x2"] and p["rps"] < base["rps"] and p["ou25_ll"] < base["ou25_ll"]
        out["gate_zero_pass"] = out["arms"]["gate_zero"]["dev_pass"]
        write_json(HERE / "results_dev.json", out)
        with (HERE / "dev_predictions.csv").open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["match_id", "date", "season", "home", "away", "arm", "lh", "la", "ph", "pd", "pa", "p_over25", "y", "yo"])
            w.writeheader()
            for r in pred_rows: w.writerow({k: r.get(k) for k in w.fieldnames})
    return out, pred_rows

def virgin():
    dev = json.loads((HERE / "results_dev.json").read_text())
    if not dev["gate_zero_pass"]:
        out = {"virgin_read": False, "reason": "Gate Zero failed dev gate; virgin deliberately unread"}
        write_json(HERE / "results_virgin.json", out); return out
    arms = [a for a in ARMS if dev["arms"][a]["dev_pass"]]
    res, pred_rows = run_phase("virgin")
    out = {"virgin_read": True, "scored_arms": arms, "arms": {}, "climatology": res["climatology"]["pooled"],
           "x2_info": res["protocol"]["x2_info"]}
    gz = res["arms"]["gate_zero"]["pooled"]; clim = res["climatology"]["pooled"]
    eligible = []
    for a in arms:
        v = res["arms"][a]["pooled"]
        cal_hw = calib_verdict({"calibration_pp": v["home_win_calibration_pp"], "calibration_se_pp": v["home_win_calibration_se_pp"]})
        cal_ou = calib_verdict({"calibration_pp": v["ou25_calibration_pp"], "calibration_se_pp": v["ou25_calibration_se_pp"]})
        cal = "FAIL" if "FAIL" in (cal_hw, cal_ou) else ("PROVISIONAL" if "PROVISIONAL" in (cal_hw, cal_ou) else "PASS")
        sign = True
        if a != "gate_zero":
            wins = sum(1 for s in SCORED if dev["arms"][a]["seasons"][s]["ll_1x2"] <= dev["arms"]["gate_zero"]["seasons"][s]["ll_1x2"])
            sign = wins * 2 >= len(SCORED)
        legs = {"ll_leg": v["ll_1x2"] <= gz["ll_1x2"] and v["ll_1x2"] <= clim["ll_1x2"],
                "calibration": cal, "cal_home_win": cal_hw, "cal_ou25": cal_ou, "sign_leg": sign}
        out["arms"][a] = {**v, "legs": legs}
        if legs["ll_leg"] and cal in ("PASS", "PROVISIONAL") and sign: eligible.append(a)
    shipped = min(eligible, key=lambda a: (res["arms"][a]["pooled"]["ll_1x2"], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = shipped
    out["verdict"] = ("PASS" if shipped and out["arms"][shipped]["legs"]["calibration"] == "PASS"
                      else "PROVISIONAL" if shipped else "FAIL")
    write_json(HERE / "results_virgin.json", out)
    if shipped:
        rows = [r for r in pred_rows if r["arm"] == shipped]
        pdir = HERE.parents[1] / "predictions"; pdir.mkdir(exist_ok=True)
        with (pdir / "g_dk1_virgin_predictions.csv").open("w", newline="") as f:
            w = csv.writer(f); w.writerow(["match_id", "date", "home", "away", "arm", "lambda_home", "lambda_away", "p_home", "p_draw", "p_away", "p_over25", "pred_goals_1h", "pred_goals_2h", "actual_home_goals", "actual_away_goals"])
            for r in rows:
                tot = r["lh"] + r["la"]
                w.writerow([r["match_id"], r["date"], r["home"], r["away"], shipped, round(r["lh"], 4), round(r["la"], 4),
                            round(r["ph"], 4), round(r["pd"], 4), round(r["pa"], 4), round(r["p_over25"], 4),
                            round(tot * 0.436, 3), round(tot * 0.564, 3), r["gh"], r["ga"]])
        write_json(HERE / "fitted_params_virgin.json",
                   {"market": "goals", "arm": shipped, "fit_scope": "all DK1 matches before 2025/2026",
                    "halves_share_1h": 0.436, "virgin": out["arms"][shipped]})
    return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "dev":
        o, _ = run_phase("dev"); print(json.dumps({a: o["arms"][a]["pooled"] for a in ARMS}, indent=1)); print("clim", o["climatology"]["pooled"]); print("gz_pass", o["gate_zero_pass"])
    else:
        print(json.dumps(virgin(), indent=1, default=str))
