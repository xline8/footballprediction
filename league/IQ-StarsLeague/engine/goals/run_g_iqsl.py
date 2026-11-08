"""G-IQSL goals engine. Usage: run_g_iqsl.py dev|virgin."""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
from dc import DC
from arms import adjusted_lambdas, match_counts
from common_iqsl import load, VIRGIN, agg, calib_verdict, write_json

SEED = "2021/2022"
SCORED = ("2022/2023", "2023/2024", "2024/2025")
ARMS = ("gate_zero", "shrink")
GOALS_1H_SHARE = 0.4323308271


def games(rows):
    return [{"hi": m["home_id"], "ai": m["away_id"], "yh": m["gh"], "ya": m["ga"],
             "date": m["date"], "home": m["home"], "away": m["away"],
             "xgh": None, "xga": None} for m in rows]


def rps(ph, pd, pa, y):
    c1, c2 = ph, ph + pd
    t1 = 1.0 if y == 0 else 0.0
    t2 = 1.0 if y <= 1 else 0.0
    return ((c1 - t1) ** 2 + (c2 - t2) ** 2) / 2.0


def score_season(model, rows, season, counts):
    out = {a: [] for a in ARMS}
    out["__clim"] = []
    prior = [m for m in rows if m["season"] < season]
    ph_r = sum(m["gh"] > m["ga"] for m in prior) / len(prior)
    pd_r = sum(m["gh"] == m["ga"] for m in prior) / len(prior)
    pa_r = 1 - ph_r - pd_r
    ou_r = sum(m["gh"] + m["ga"] > 2.5 for m in prior) / len(prior)
    for m in [x for x in rows if x["season"] == season]:
        y = 0 if m["gh"] > m["ga"] else (1 if m["gh"] == m["ga"] else 2)
        yo = int(m["gh"] + m["ga"] > 2.5)
        for arm in ARMS:
            if arm == "gate_zero":
                lh, la = model.lambdas(m["home_id"], m["away_id"])
            else:
                lh, la = adjusted_lambdas(model, m["home_id"], m["away_id"], arm, counts)
            p = model.probs(lh, la)
            out[arm].append({"match_id": m["match_id"], "season": season,
                             "ph": p["ph"], "pd": p["pd"], "pa": p["pa"],
                             "p_over25": p["over25"], "y": y, "yo": yo,
                             "lh": lh, "la": la, "home": m["home"], "away": m["away"],
                             "gh": m["gh"], "ga": m["ga"], "date": m["date"].isoformat()})
        out["__clim"].append({"match_id": m["match_id"], "season": season,
                              "ph": ph_r, "pd": pd_r, "pa": pa_r,
                              "p_over25": ou_r, "y": y, "yo": yo})
    return out


def summarize(recs):
    def met(rs):
        ll = sum(-math.log(max((r["ph"], r["pd"], r["pa"])[r["y"]], 1e-12))
                 for r in rs) / len(rs)
        rp = sum(rps(r["ph"], r["pd"], r["pa"], r["y"]) for r in rs) / len(rs)
        ou = agg([(r["p_over25"], r["yo"]) for r in rs])
        hw = agg([(r["ph"], int(r["y"] == 0)) for r in rs])
        return {"n": len(rs), "ll_1x2": ll, "rps": rp, "ou25_ll": ou["ll"],
                "ou25_calibration_pp": ou["calibration_pp"],
                "ou25_calibration_se_pp": ou["calibration_se_pp"],
                "home_win_calibration_pp": hw["calibration_pp"],
                "home_win_calibration_se_pp": hw["calibration_se_pp"]}
    return met


def run_phase(phase):
    seasons = (SEED,) + SCORED if phase == "dev" else (SEED,) + SCORED + (VIRGIN,)
    rows = load(seasons)
    expected = set(seasons)
    assert {m["season"] for m in rows} <= expected
    if phase == "dev":
        assert {m["season"] for m in rows} <= set((SEED,) + SCORED)
    targets = SCORED if phase == "dev" else (VIRGIN,)
    all_recs = {a: [] for a in ARMS + ("__clim",)}
    perseas = {a: {} for a in ARMS + ("__clim",)}
    pred_rows = []
    for season in targets:
        first_date = min(x["date"] for x in rows if x["season"] == season)
        train = [m for m in rows if m["date"] < first_date]
        model = DC().fit(games(train), first_date)
        counts = match_counts(games(train))
        recs = score_season(model, rows, season, counts)
        for arm in ARMS + ("__clim",):
            perseas[arm][season] = summarize(recs[arm])(recs[arm])
            all_recs[arm] += recs[arm]
            if arm in ARMS:
                pred_rows += [dict(r, arm=arm) for r in recs[arm]]
    out = {"protocol": {"phase": phase, "seed": SEED, "scored": list(targets),
                         "virgin": VIRGIN}, "arms": {}, "climatology": {}}
    for arm in ARMS:
        out["arms"][arm] = {"seasons": perseas[arm],
                             "pooled": summarize(all_recs[arm])(all_recs[arm])}
    out["climatology"] = {"seasons": perseas["__clim"],
                          "pooled": summarize(all_recs["__clim"])(all_recs["__clim"])}
    if phase == "dev":
        base = out["climatology"]["pooled"]
        for arm in ARMS:
            p = out["arms"][arm]["pooled"]
            out["arms"][arm]["dev_pass"] = (p["ll_1x2"] < base["ll_1x2"] and
                                              p["rps"] < base["rps"] and
                                              p["ou25_ll"] < base["ou25_ll"])
        out["gate_zero_pass"] = out["arms"]["gate_zero"]["dev_pass"]
        write_json(HERE / "results_dev.json", out)
        with (HERE / "dev_predictions.csv").open("w", newline="", encoding="utf-8") as f:
            fields = ["match_id", "date", "season", "home", "away", "arm", "lh", "la",
                      "ph", "pd", "pa", "p_over25", "y", "yo"]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in pred_rows:
                w.writerow({k: r.get(k) for k in fields})
    return out, pred_rows


def virgin():
    dev = json.loads((HERE / "results_dev.json").read_text())
    if not dev["gate_zero_pass"]:
        out = {"virgin_read": False,
               "reason": "Gate Zero failed dev gate; virgin deliberately unread"}
        write_json(HERE / "results_virgin.json", out)
        return out
    arms = [a for a in ARMS if dev["arms"][a]["dev_pass"]]
    res, pred_rows = run_phase("virgin")
    out = {"virgin_read": True, "scored_arms": arms, "arms": {},
           "climatology": res["climatology"]["pooled"]}
    gz = res["arms"]["gate_zero"]["pooled"]
    clim = res["climatology"]["pooled"]
    eligible = []
    for arm in arms:
        v = res["arms"][arm]["pooled"]
        cal_hw = calib_verdict({"calibration_pp": v["home_win_calibration_pp"],
                                "calibration_se_pp": v["home_win_calibration_se_pp"]})
        cal_ou = calib_verdict({"calibration_pp": v["ou25_calibration_pp"],
                                "calibration_se_pp": v["ou25_calibration_se_pp"]})
        cal = "FAIL" if "FAIL" in (cal_hw, cal_ou) else (
            "PROVISIONAL" if "PROVISIONAL" in (cal_hw, cal_ou) else "PASS")
        sign = True
        if arm != "gate_zero":
            wins = sum(1 for season in SCORED if
                       dev["arms"][arm]["seasons"][season]["ll_1x2"] <=
                       dev["arms"]["gate_zero"]["seasons"][season]["ll_1x2"])
            sign = wins * 2 >= len(SCORED)
        legs = {"ll_leg": v["ll_1x2"] <= gz["ll_1x2"] and v["ll_1x2"] <= clim["ll_1x2"],
                "calibration": cal, "cal_home_win": cal_hw, "cal_ou25": cal_ou,
                "sign_leg": sign}
        out["arms"][arm] = {**v, "legs": legs}
        if legs["ll_leg"] and cal in ("PASS", "PROVISIONAL") and sign:
            eligible.append(arm)
    shipped = min(eligible, key=lambda a: (out["arms"][a]["ll_1x2"], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = shipped
    out["verdict"] = ("PASS" if shipped and out["arms"][shipped]["legs"]["calibration"] == "PASS"
                      else "PROVISIONAL" if shipped else "FAIL")
    write_json(HERE / "results_virgin.json", out)
    if shipped:
        rows = [r for r in pred_rows if r["arm"] == shipped]
        pdir = HERE.parents[1] / "predictions"
        pdir.mkdir(exist_ok=True)
        with (pdir / "g_iqsl_virgin_predictions.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["match_id", "date", "home", "away", "arm", "lambda_home", "lambda_away",
                        "p_home", "p_draw", "p_away", "p_over25", "pred_goals_1h", "pred_goals_2h",
                        "actual_home_goals", "actual_away_goals"])
            for r in rows:
                total = r["lh"] + r["la"]
                w.writerow([r["match_id"], r["date"], r["home"], r["away"], shipped,
                            round(r["lh"], 4), round(r["la"], 4), round(r["ph"], 4),
                            round(r["pd"], 4), round(r["pa"], 4), round(r["p_over25"], 4),
                            round(total * GOALS_1H_SHARE, 4), round(total * (1 - GOALS_1H_SHARE), 4),
                            r["gh"], r["ga"]])
        write_json(HERE / "fitted_params_virgin.json", {
            "market": "goals", "arm": shipped,
            "fit_scope": "all IQSL regular matches before 2025/2026",
            "goals_1h_share": GOALS_1H_SHARE, "virgin": out["arms"][shipped]})
    return out


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ("dev", "virgin"):
        raise SystemExit("usage: run_g_iqsl.py dev|virgin")
    if sys.argv[1] == "dev":
        result, _ = run_phase("dev")
        print(json.dumps({a: result["arms"][a]["pooled"] for a in ARMS}, indent=1))
        print("clim", result["climatology"]["pooled"])
        print("gz_pass", result["gate_zero_pass"])
    else:
        print(json.dumps(virgin(), indent=1, default=str))
