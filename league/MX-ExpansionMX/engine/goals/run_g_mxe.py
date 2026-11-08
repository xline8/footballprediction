"""G-MXE goals engine: Dixon-Coles, goals-only, tournament-blocked walk-forward.

Prereg: league/MX-ExpansionMX/prereg/PREREG_G_MXE.md (frozen before fitting).
Usage: python3 run_g_mxe.py dev | virgin
"""
import csv, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from dc import DC
from arms import adjusted_lambdas, match_counts
from common_mxe import load, BLOCKS, agg, calib_verdict, write_json

SEED = BLOCKS[0]; SCORED = BLOCKS[1:9]; VIRGIN = BLOCKS[9]
ARMS = ("gate_zero", "shrink")
HALVES_GOALS_1H = 0.448


def games(rows):
    return [{"hi": m["home_id"], "ai": m["away_id"], "yh": m["gh"], "ya": m["ga"],
             "date": m["date"], "home": m["home"], "away": m["away"], "xgh": None, "xga": None} for m in rows]


def rps(ph, pd, pa, y):
    return ((ph - (y == 0)) ** 2 + (ph + pd - (y <= 1)) ** 2) / 2.0


def score_block(model, rows, block, counts):
    out = {a: [] for a in ARMS}; out["__clim"] = []
    prior = [m for m in rows if m["block_idx"] < BLOCKS.index(block)]
    ph_r = sum(m["gh"] > m["ga"] for m in prior) / len(prior)
    pd_r = sum(m["gh"] == m["ga"] for m in prior) / len(prior)
    pa_r = 1 - ph_r - pd_r
    ou_r = sum(m["gh"] + m["ga"] > 2.5 for m in prior) / len(prior)
    for m in [x for x in rows if x["block"] == block]:
        y = 0 if m["gh"] > m["ga"] else (1 if m["gh"] == m["ga"] else 2)
        yo = int(m["gh"] + m["ga"] > 2.5)
        for arm in ARMS:
            if arm == "gate_zero":
                lh, la = model.lambdas(m["home_id"], m["away_id"])
            else:
                lh, la = adjusted_lambdas(model, m["home_id"], m["away_id"], arm, counts)
            p = model.probs(lh, la)
            out[arm].append({"match_id": m["match_id"], "block": block, "ph": p["ph"], "pd": p["pd"],
                             "pa": p["pa"], "p_over25": p["over25"], "y": y, "yo": yo, "lh": lh, "la": la,
                             "home": m["home"], "away": m["away"], "gh": m["gh"], "ga": m["ga"],
                             "date": m["date"].isoformat()})
        out["__clim"].append({"match_id": m["match_id"], "block": block, "ph": ph_r, "pd": pd_r,
                              "pa": pa_r, "p_over25": ou_r, "y": y, "yo": yo})
    return out


def summarize(recs):
    import math
    ll = sum(-math.log(max((r["ph"], r["pd"], r["pa"])[r["y"]], 1e-12)) for r in recs) / len(recs)
    rp = sum(rps(r["ph"], r["pd"], r["pa"], r["y"]) for r in recs) / len(recs)
    ou = agg([(r["p_over25"], r["yo"]) for r in recs])
    hw = agg([(r["ph"], int(r["y"] == 0)) for r in recs])
    return {"n": len(recs), "ll_1x2": ll, "rps": rp, "ou25_ll": ou["ll"],
            "ou25_calibration_pp": ou["calibration_pp"], "ou25_calibration_se_pp": ou["calibration_se_pp"],
            "home_win_calibration_pp": hw["calibration_pp"], "home_win_calibration_se_pp": hw["calibration_se_pp"]}


def run_phase(phase):
    blocks = [SEED] + list(SCORED) if phase == "dev" else BLOCKS[:10]
    rows = load(blocks)
    targets = list(SCORED) if phase == "dev" else [VIRGIN]
    all_recs = {a: [] for a in ARMS + ("__clim",)}
    perblock = {a: {} for a in ARMS + ("__clim",)}
    pred_rows = []
    fitted = {}
    for B in targets:
        first = min(x["date"] for x in rows if x["block"] == B)
        train = [m for m in rows if m["date"] < first]
        model = DC().fit(games(train), first)
        counts = match_counts(games(train))
        fitted[B] = {"rho": model.rho, "h": model.h, "mu": model.mu,
                     "a": {str(k): v for k, v in model.a.items()},
                     "d": {str(k): v for k, v in model.d.items()},
                     "team_names": {str(k): v for k, v in model.team_names.items()},
                     "train_n": len(train)}
        recs = score_block(model, rows, B, counts)
        for a in ARMS + ("__clim",):
            perblock[a][B] = summarize(recs[a]); all_recs[a] += recs[a]
            if a in ARMS:
                pred_rows += [dict(r, arm=a) for r in recs[a]]
    out = {"protocol": {"phase": phase, "seed": SEED, "scored": targets}, "arms": {}, "climatology": {}}
    for a in ARMS:
        out["arms"][a] = {"blocks": perblock[a], "pooled": summarize(all_recs[a])}
    out["climatology"] = {"blocks": perblock["__clim"], "pooled": summarize(all_recs["__clim"])}
    if phase == "dev":
        base = out["climatology"]["pooled"]
        for a in ARMS:
            p = out["arms"][a]["pooled"]
            out["arms"][a]["dev_pass"] = p["ll_1x2"] < base["ll_1x2"] and p["rps"] < base["rps"] and p["ou25_ll"] < base["ou25_ll"]
        out["gate_zero_pass"] = out["arms"]["gate_zero"]["dev_pass"]
        out["shrink_bite"] = {"predictions_differing_from_gate_zero":
                              sum(1 for r, g in zip((x for x in pred_rows if x["arm"] == "shrink"),
                                                    (x for x in pred_rows if x["arm"] == "gate_zero"))
                                  if abs(r["ph"] - g["ph"]) > 1e-12 or abs(r["p_over25"] - g["p_over25"]) > 1e-12),
                              "n_dev_predictions": len(all_recs["gate_zero"])}
        write_json(HERE / "results_dev.json", out)
        try:
            with (HERE / "dev_predictions.csv").open("w", newline="") as f:
                fields = ["match_id", "date", "block", "home", "away", "arm", "lh", "la", "ph", "pd", "pa", "p_over25", "y", "yo"]
                w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
                for r in pred_rows:
                    w.writerow({k: r.get(k) for k in fields})
        except OSError as e:
            print(f"WRITE_FAILED dev_predictions.csv: {e}", file=sys.stderr)
    out["_fitted"] = fitted
    out["_pred_rows"] = pred_rows
    return out


def virgin():
    dev = None
    _p = HERE / "results_dev.json"
    if _p.exists() and _p.stat().st_size > 0:
        try:
            dev = json.loads(_p.read_text())
        except (ValueError, OSError):
            dev = None
    if dev is None:
        dev = run_phase("dev")
    if not dev["gate_zero_pass"]:
        out = {"virgin_read": False, "reason": "Gate Zero failed dev gate; virgin deliberately unread"}
        write_json(HERE / "results_virgin.json", out); return out
    arms = [a for a in ARMS if dev["arms"][a]["dev_pass"]]
    res = run_phase("virgin")
    out = {"virgin_read": True, "scored_arms": arms, "arms": {}, "climatology": res["climatology"]["pooled"]}
    gz = res["arms"]["gate_zero"]["pooled"]; clim = res["climatology"]["pooled"]; eligible = []
    for a in arms:
        v = res["arms"][a]["pooled"]
        ch = calib_verdict({"calibration_pp": v["home_win_calibration_pp"], "calibration_se_pp": v["home_win_calibration_se_pp"]})
        co = calib_verdict({"calibration_pp": v["ou25_calibration_pp"], "calibration_se_pp": v["ou25_calibration_se_pp"]})
        cal = "FAIL" if "FAIL" in (ch, co) else ("PROVISIONAL" if "PROVISIONAL" in (ch, co) else "PASS")
        sign = True if a == "gate_zero" else sum(dev["arms"][a]["blocks"][s]["ll_1x2"] <= dev["arms"]["gate_zero"]["blocks"][s]["ll_1x2"] for s in SCORED) * 2 >= len(SCORED)
        legs = {"ll_leg": v["ll_1x2"] <= gz["ll_1x2"] and v["ll_1x2"] <= clim["ll_1x2"],
                "calibration": cal, "cal_home_win": ch, "cal_ou25": co, "sign_leg": sign}
        out["arms"][a] = {**v, "legs": legs}
        if legs["ll_leg"] and cal in ("PASS", "PROVISIONAL") and sign:
            eligible.append(a)
    shipped = min(eligible, key=lambda a: (res["arms"][a]["pooled"]["ll_1x2"], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = shipped
    out["verdict"] = "PASS" if shipped and out["arms"][shipped]["legs"]["calibration"] == "PASS" else ("PROVISIONAL" if shipped else "FAIL")
    write_json(HERE / "results_virgin.json", out)
    if shipped:
        write_json(HERE / "fitted_params_virgin.json",
                   {"arm": shipped, "fit": res["_fitted"][VIRGIN], "halves_goals_1h_share": HALVES_GOALS_1H})
        pred_dir = HERE.parents[1] / "predictions"; pred_dir.mkdir(exist_ok=True)
        rows = [r for r in res["_pred_rows"] if r["arm"] == shipped]
        try:
            with (pred_dir / "g_mxe_virgin_predictions.csv").open("w", newline="") as f:
                fields = ["match_id", "date", "home", "away", "lh", "la", "ph", "pd", "pa", "p_over25",
                          "exp_goals", "exp_goals_1h", "exp_goals_2h", "arm"]
                w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
                for r in rows:
                    eg = r["lh"] + r["la"]
                    w.writerow({"match_id": r["match_id"], "date": r["date"], "home": r["home"], "away": r["away"],
                                "lh": r["lh"], "la": r["la"], "ph": r["ph"], "pd": r["pd"], "pa": r["pa"],
                                "p_over25": r["p_over25"], "exp_goals": eg,
                                "exp_goals_1h": eg * HALVES_GOALS_1H, "exp_goals_2h": eg * (1 - HALVES_GOALS_1H),
                                "arm": shipped})
        except OSError as e:
            print(f"WRITE_FAILED predictions: {e}", file=sys.stderr)
    return out


if __name__ == "__main__":
    if sys.argv[1] == "dev":
        o = run_phase("dev")
        print(json.dumps({a: o["arms"][a]["pooled"] for a in ARMS}, indent=1))
        print("clim", o["climatology"]["pooled"]); print("gz_pass", o["gate_zero_pass"]); print("shrink_bite", o["shrink_bite"])
    else:
        print(json.dumps(virgin(), indent=1, default=str))
