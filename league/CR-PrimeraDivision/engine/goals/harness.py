"""Data loading, walk-forward evaluation, virgin metrics, and outputs for G-CR.

Adapted from league/J1/engine/goals/harness.py: single arm (Gate Zero), goals-only
(no xG in this league), regular season only, CR seasons and the frozen halves
constant 0.460 (EDA F3). Prereg: league/CR-PrimeraDivision/prereg/PREREG_G_CR.md.
"""
import csv, json, math, os, time
from datetime import date
from pathlib import Path
from dc import DC

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "cr_matches.csv"
OUT = Path(__file__).resolve().parent
HALVES_1H = 0.460
DEV_SEASONS = ("2021/2022", "2022/2023", "2023/2024")
EVAL_SEASONS = ("2022/2023", "2023/2024")
VIRGIN_SEASON = "2024/2025"


def _safe_write_text(path, text, tries=40):
    data = text.encode("utf-8")
    for _ in range(tries):
        try:
            tmp = str(path) + ".tmp%d" % os.getpid()
            with open(tmp, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            if os.path.getsize(tmp) != len(data):
                raise IOError("size mismatch")
            os.replace(tmp, path)
            if os.path.getsize(path) == len(data):
                return
        except (PermissionError, OSError):
            time.sleep(1.0)
    raise IOError("could not write %s" % path)


def load(path, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["stage"] != "regular":
                continue
            if allowed is not None and r["season"] not in allowed:
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"],
                         "date": date.fromisoformat(r["date_utc"]),
                         "hi": int(r["home_id"]), "ai": int(r["away_id"]),
                         "home": r["home_name"], "away": r["away_name"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                         "xgh": None, "xga": None})
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target):
    cutoff = min(r["date"] for r in target)
    model = DC().fit([r for r in train if r["date"] < cutoff], cutoff)
    return model


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = int(r["yh"] + r["ya"] > 2.5)
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def run_dev():
    rows = load(DATA, set(DEV_SEASONS))
    arm = "gate_zero"
    result = []
    all_rows, all_clim = [], []
    for season in EVAL_SEASONS:
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        model = _fit_predict(train, target)
        probs = [model.probs(*model.lambdas(r["hi"], r["ai"])) for r in target]
        met = _scores(target, probs)
        met.update({"arm": arm, "season": season, "kind": "model"})
        result.append(met)
        all_rows += list(zip(target, probs))
        cp, co = _clim(train)
        cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        met = _scores(target, cprobs)
        met.update({"arm": arm, "season": season, "kind": "climatology"})
        result.append(met)
        all_clim += list(zip(target, cprobs))
    met = _scores([x[0] for x in all_rows], [x[1] for x in all_rows])
    met.update({"arm": arm, "season": "pooled", "kind": "model"})
    result.append(met)
    met = _scores([x[0] for x in all_clim], [x[1] for x in all_clim])
    met.update({"arm": arm, "season": "pooled", "kind": "climatology"})
    result.append(met)
    _write_dev(result)
    _print_table(result, "dev")
    return result


def _write_dev(result):
    _safe_write_text(OUT / "results_dev.json", json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    lines = [",".join(fields)]
    for r in result:
        lines.append(",".join(str(r.get(k)) for k in fields))
    _safe_write_text(OUT / "results_dev.csv", "\n".join(lines) + "\n")


def virgin_metrics(arms=("gate_zero",), write_predictions_arm=None):
    rows = load(DATA, set(DEV_SEASONS) | {VIRGIN_SEASON})
    train = [r for r in rows if r["season"] != VIRGIN_SEASON]
    target = [r for r in rows if r["season"] == VIRGIN_SEASON]
    cp, co = _clim(train)
    result = {}
    for arm in arms:
        model = _fit_predict(train, target)
        preds = []
        for r in target:
            lh, la = model.lambdas(r["hi"], r["ai"])
            p = model.probs(lh, la)
            p.update({"lh": lh, "la": la})
            preds.append(p)
        met = _scores(target, preds)
        cal_hw = sum(p["ph"] for p in preds) / len(preds) - sum(r["yh"] > r["ya"] for r in target) / len(target)
        cal_ou = sum(p["over25"] for p in preds) / len(preds) - sum(r["yh"] + r["ya"] > 2.5 for r in target) / len(target)

        def se(vals):
            m = sum(vals) / len(vals)
            return (sum((x - m) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5 / math.sqrt(len(vals))

        met.update({
            "climatology": _scores(target, [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]),
            "calibration": {
                "home_win_diff": cal_hw,
                "home_win_se": se([p["ph"] - (r["yh"] > r["ya"]) for p, r in zip(preds, target)]),
                "over25_diff": cal_ou,
                "over25_se": se([p["over25"] - (r["yh"] + r["ya"] > 2.5) for p, r in zip(preds, target)]),
            },
            "params": {"a": {str(k): v for k, v in model.a.items()},
                       "d": {str(k): v for k, v in model.d.items()},
                       "h": model.h, "rho": model.rho, "mu": model.mu},
        })
        result[arm] = met
        if arm == write_predictions_arm:
            _write_predictions(target, preds, arm, model)
    _safe_write_text(OUT / "results_virgin.json", json.dumps(result, indent=2) + "\n")
    _print_table(result, "virgin")
    return result


def _write_predictions(rows, preds, arm, model):
    dest = ROOT / "predictions"
    dest.mkdir(exist_ok=True)
    fields = ["match_id", "date", "home_team", "away_team", "home_goals", "away_goals",
              "lam_h", "lam_a", "rho", "ph", "pd", "pa", "p_over_1_5", "p_over_2_5",
              "p_over_3_5", "p_btts", "lam_h_1h", "lam_a_1h", "p_over_1h_0_5", "p_over_1h_1_5",
              "p_over_1h_2_5", "lam_h_2h", "lam_a_2h", "p_over_2h_1_5", "p_over_2h_2_5",
              "p_over_2h_3_5", "arm"]
    out = []
    for r, p in zip(rows, preds):
        q1 = model.probs(p["lh"] * HALVES_1H, p["la"] * HALVES_1H)
        q2 = model.probs(p["lh"] * (1 - HALVES_1H), p["la"] * (1 - HALVES_1H))
        out.append({"match_id": r["match_id"], "date": r["date"].isoformat(),
                    "home_team": r["home"], "away_team": r["away"],
                    "home_goals": r["yh"], "away_goals": r["ya"],
                    "lam_h": p["lh"], "lam_a": p["la"], "rho": model.rho,
                    "ph": p["ph"], "pd": p["pd"], "pa": p["pa"],
                    "p_over_1_5": p["over15"], "p_over_2_5": p["over25"],
                    "p_over_3_5": p["over35"], "p_btts": p["btts"],
                    "lam_h_1h": p["lh"] * HALVES_1H, "lam_a_1h": p["la"] * HALVES_1H,
                    "p_over_1h_0_5": model.over(p["lh"] * HALVES_1H, p["la"] * HALVES_1H, .5),
                    "p_over_1h_1_5": q1["over15"], "p_over_1h_2_5": q1["over25"],
                    "lam_h_2h": p["lh"] * (1 - HALVES_1H), "lam_a_2h": p["la"] * (1 - HALVES_1H),
                    "p_over_2h_1_5": q2["over15"], "p_over_2h_2_5": q2["over25"],
                    "p_over_2h_3_5": q2["over35"], "arm": arm})
    import io
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=fields)
    w.writeheader()
    w.writerows(out)
    _safe_write_text(dest / "g_cr_virgin_predictions.csv", sio.getvalue())
    _safe_write_text(OUT / "fitted_params_virgin.json", json.dumps(
        {"a": {str(k): v for k, v in model.a.items()},
         "d": {str(k): v for k, v in model.d.items()},
         "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm}, indent=2) + "\n")


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for r in data:
            print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 clim_ll calibration_hw calibration_ou")
        for a, r in data.items():
            print(f'{a} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f} '
                  f'{r["climatology"]["ll_1x2"]:.6f} {r["calibration"]["home_win_diff"]:.6f} '
                  f'{r["calibration"]["over25_diff"]:.6f}')
