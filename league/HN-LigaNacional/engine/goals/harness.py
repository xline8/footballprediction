"""G-HN expanding, tournament-blocked dev harness and frozen virgin gate."""
import csv
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "hn_matches.csv"
OUT = Path(__file__).resolve().parent
SEED = ("2021/2022 - Apertura", "2021/2022 - Clausura")
DEV_TOURNAMENTS = (
    "2022/2023 - Apertura", "2022/2023 - Clausura",
    "2023/2024 - Apertura", "2023/2024 - Clausura",
    "2024/2025 - Apertura", "2024/2025 - Clausura",
)
PRE_VIRGIN = SEED + DEV_TOURNAMENTS
VIRGIN = ("2025/2026 - Apertura", "2025/2026 - Clausura")
RESERVED_PREFIX = "2026/2027"
HALVES_HOME_SHARE = 0.4572


def load(path=DATA, allowed=None, dev=False, virgin=False):
    """Load only regular-phase matches, with explicit read-boundary checks."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["stage"] != "regular":
                continue
            season = r["season"]
            if allowed is not None and season not in allowed:
                continue
            if dev:
                assert season not in VIRGIN and not season.startswith(RESERVED_PREFIX), (
                    "dev loader saw virgin or reserved season"
                )
            if virgin:
                assert not season.startswith(RESERVED_PREFIX), "reserved data must never be read"
            rows.append({
                "match_id": r["match_id"], "season": season,
                "date": date.fromisoformat(r["date"]),
                "hi": int(r["home_id"]), "ai": int(r["away_id"]),
                "home": r["home"], "away": r["away"],
                "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
            })
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


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
    return [hw, dr, 1.0 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    prior = [r for r in train if r["date"] < cutoff]
    assert prior and max(r["date"] for r in prior) < cutoff
    model = DC().fit(prior, cutoff)
    return model, match_counts(prior), max(r["date"] for r in prior)


def _predict(target, model, counts, arm):
    out = []
    for r in target:
        lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts)
        p = model.probs(lh, la)
        p.update({"lh": lh, "la": la})
        out.append(p)
    return out


def _naive_lambdas(train, target, history=None):
    # Trailing windows are the team's most recent 10 eligible regular-phase
    # matches strictly before the target match's date (brief definition), so
    # the history source is all pre-virgin rows, not just the pre-tournament
    # training window; the league-mean fallback still comes from `train`.
    source = train if history is None else history
    history_rows = defaultdict(list)
    for r in sorted(source, key=lambda x: (x["date"], x["match_id"])):
        history_rows[r["hi"]].append((r["date"], r["match_id"], "gf", r["yh"]))
        history_rows[r["hi"]].append((r["date"], r["match_id"], "ga", r["ya"]))
        history_rows[r["ai"]].append((r["date"], r["match_id"], "gf", r["ya"]))
        history_rows[r["ai"]].append((r["date"], r["match_id"], "ga", r["yh"]))
    league_mean = sum(r["yh"] + r["ya"] for r in train) / (2.0 * len(train))
    result = []
    for r in target:
        def component(team, kind):
            vals = [x[3] for x in history_rows[team] if x[0] < r["date"] and x[2] == kind]
            vals = vals[-10:]
            return sum(vals) / len(vals) if len(vals) >= 6 else league_mean
        lh = (component(r["hi"], "gf") + component(r["ai"], "ga")) / 2.0
        la = (component(r["ai"], "gf") + component(r["hi"], "ga")) / 2.0
        result.append((lh, la))
    return result


def _poisson_probs(lh, la):
    m = DC().matrix(lh, la, rho=0.0)[0]
    s = sum(sum(row) for row in m)
    ph = sum(m[x][y] for x in range(11) for y in range(11) if x > y) / s
    pd = sum(m[x][x] for x in range(11)) / s
    over = sum(m[x][y] for x in range(11) for y in range(11) if x + y > 2) / s
    p0h = sum(m[0][y] for y in range(11)) / s
    p0a = sum(m[x][0] for x in range(11)) / s
    return {"ph": ph, "pd": pd, "pa": 1 - ph - pd, "over25": over,
            "btts": 1 - p0h - p0a + m[0][0] / s, "lh": lh, "la": la}


def _naive_predict(train, target, history=None):
    return [_poisson_probs(lh, la) for lh, la in _naive_lambdas(train, target, history)]


def _record(arm, season, kind, rows, probs):
    out = _scores(rows, probs)
    out.update({"arm": arm, "season": season, "kind": kind})
    return out


def _shrink_audit_entry(rows, gate, shrink):
    deltas = [abs(a[k] - b[k]) for a, b in zip(gate, shrink) for k in ("lh", "la")]
    return {"n_target": len(rows), "changed_predictions": sum(max(abs(a[k] - b[k]) for k in ("lh", "la")) > 0.0 for a, b in zip(gate, shrink)),
            "max_abs_delta_lambda": max(deltas, default=0.0)}


def run_dev():
    rows = load(allowed=PRE_VIRGIN, dev=True)
    assert set(r["season"] for r in rows) == set(PRE_VIRGIN)
    assert not any(r["season"] in VIRGIN or r["season"].startswith(RESERVED_PREFIX) for r in rows)
    print(f"dev loader: {len(rows)} regular rows; virgin/reserved rows rejected")
    result = []
    shrink_audit = {}
    for season in DEV_TOURNAMENTS:
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        print(f"dev fit {season}: max train date {max(r['date'] for r in train)} before kickoff {min(r['date'] for r in target)}")
        models = {}
        preds = {}
        for arm in ("gate_zero", "shrink"):
            models[arm], counts, _ = _fit_predict(train, target, arm)
            preds[arm] = _predict(target, models[arm], counts, arm)
            result.append(_record(arm, season, "model", target, preds[arm]))
        cp, co = _clim(train)
        cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        naive = _naive_predict(train, target, rows)
        for arm in ("gate_zero", "shrink"):
            result.append(_record(arm, season, "climatology", target, cprobs))
            result.append(_record(arm, season, "naive_trailing10", target, naive))
        shrink_audit[season] = _shrink_audit_entry(target, preds["gate_zero"], preds["shrink"])

    for arm in ("gate_zero", "shrink"):
        for kind in ("model", "climatology", "naive_trailing10"):
            subset = []
            for season in DEV_TOURNAMENTS:
                target = [r for r in rows if r["season"] == season]
                subset.extend(target)
            probs = []
            if kind == "model":
                # Reconstruct pooled predictions using the per-block fits.
                for season in DEV_TOURNAMENTS:
                    target = [r for r in rows if r["season"] == season]
                    train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
                    model, counts, _ = _fit_predict(train, target, arm)
                    probs.extend(_predict(target, model, counts, arm))
            elif kind == "climatology":
                for season in DEV_TOURNAMENTS:
                    target = [r for r in rows if r["season"] == season]
                    train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
                    cp, co = _clim(train)
                    probs.extend({"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target)
            else:
                for season in DEV_TOURNAMENTS:
                    target = [r for r in rows if r["season"] == season]
                    train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
                    probs.extend(_naive_predict(train, target, rows))
            result.append(_record(arm, "pooled", kind, subset, probs))
    pooled_gate = []
    pooled_shrink = []
    for season in DEV_TOURNAMENTS:
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        pooled_gate.extend(_predict(target, *_fit_predict(train, target, "gate_zero")[:2], "gate_zero"))
        pooled_shrink.extend(_predict(target, *_fit_predict(train, target, "shrink")[:2], "shrink"))
    shrink_audit["pooled"] = _shrink_audit_entry(subset, pooled_gate, pooled_shrink)
    _write_dev(result, shrink_audit)
    return {"results": result, "shrink_audit": shrink_audit}


def _write_dev(result, shrink_audit):
    (OUT / "results_dev.json").write_text(json.dumps({"results": result, "shrink_audit": shrink_audit}, indent=2, sort_keys=True) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows({k: r.get(k) for k in fields} for r in result)


def _result_rows(result):
    return result["results"] if isinstance(result, dict) else result


def dev_passes(result, arm):
    rows = _result_rows(result)
    model = next(r for r in rows if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == "model")
    base = next(r for r in rows if r["arm"] == arm and r["season"] == "pooled" and r["kind"] == "climatology")
    return model["ll_1x2"] < base["ll_1x2"] and model["rps"] < base["rps"] and model["oull_2_5"] < base["oull_2_5"]


def _se(values):
    m = sum(values) / len(values)
    return (sum((x - m) ** 2 for x in values) / (len(values) - 1)) ** 0.5 / math.sqrt(len(values))


def _half_probs(model, lh, la, share):
    lh, la = lh * share, la * share
    matrix, total = model.matrix(lh, la)
    over = lambda line: sum(matrix[x][y] for x in range(11) for y in range(11) if x + y > line) / total
    p0h = sum(matrix[0][y] for y in range(11)) / total
    p0a = sum(matrix[x][0] for x in range(11)) / total
    return {"over15": over(1.5), "over25": over(2.5),
            "btts": 1 - p0h - p0a + matrix[0][0] / total,
            "lh": lh, "la": la}


def _write_predictions(rows, preds):
    dest = ROOT / "predictions"
    dest.mkdir(exist_ok=True)
    fields = ["match_id", "date", "season", "home", "away", "exp_home_goals", "exp_away_goals", "p_home", "p_draw", "p_away", "p_over25", "p_btts", "exp_home_goals_1h", "exp_away_goals_1h", "p_over15_1h", "p_over25_1h", "p_btts_1h", "exp_home_goals_2h", "exp_away_goals_2h", "p_over15_2h", "p_over25_2h", "p_btts_2h"]
    with open(dest / "g_hn_virgin_predictions.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r, p in zip(rows, preds):
            h1 = _half_probs(p["model"], p["lh"], p["la"], HALVES_HOME_SHARE)
            h2 = _half_probs(p["model"], p["lh"], p["la"], 1 - HALVES_HOME_SHARE)
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "season": r["season"], "home": r["home"], "away": r["away"], "exp_home_goals": p["lh"], "exp_away_goals": p["la"], "p_home": p["ph"], "p_draw": p["pd"], "p_away": p["pa"], "p_over25": p["over25"], "p_btts": p["btts"], "exp_home_goals_1h": p["lh"] * HALVES_HOME_SHARE, "exp_away_goals_1h": p["la"] * HALVES_HOME_SHARE, "p_over15_1h": _line_prob(h1, 1.5), "p_over25_1h": _line_prob(h1, 2.5), "p_btts_1h": h1["btts"], "exp_home_goals_2h": p["lh"] * (1 - HALVES_HOME_SHARE), "exp_away_goals_2h": p["la"] * (1 - HALVES_HOME_SHARE), "p_over15_2h": _line_prob(h2, 1.5), "p_over25_2h": _line_prob(h2, 2.5), "p_btts_2h": h2["btts"]})


def _line_prob(probs, line):
    return probs["over25"] if line == 2.5 else probs["over15"]


def virgin_metrics(arms, dev_result):
    rows = load(allowed=PRE_VIRGIN + VIRGIN, virgin=True)
    train = [r for r in rows if r["season"] in PRE_VIRGIN]
    target = [r for r in rows if r["season"] in VIRGIN]
    cutoff = min(r["date"] for r in target)
    train = [r for r in train if r["date"] < cutoff]
    cp, co = _clim(train)
    clim = _scores(target, [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target])
    dev_rows = _result_rows(dev_result)
    result = {"virgin_read": True, "n": len(target), "arms": {}, "winner": None, "verdict": "FAIL"}
    for arm in tuple(dict.fromkeys(("gate_zero",) + tuple(arms))):
        model, counts, max_train_date = _fit_predict(train, target, arm)
        preds = []
        for r in target:
            lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, counts)
            p = model.probs(lh, la); p.update({"lh": lh, "la": la, "model": model}); preds.append(p)
        met = _scores(target, preds)
        cal_hw = sum(r["yh"] > r["ya"] for r in target) / len(target) - sum(p["ph"] for p in preds) / len(preds)
        cal_ou = sum(r["yh"] + r["ya"] > 2.5 for r in target) / len(target) - sum(p["over25"] for p in preds) / len(preds)
        hw_se = _se([p["ph"] - (r["yh"] > r["ya"]) for p, r in zip(preds, target)])
        ou_se = _se([p["over25"] - (r["yh"] + r["ya"] > 2.5) for p, r in zip(preds, target)])
        signs = {}
        for season in DEV_TOURNAMENTS:
            row = next(x for x in dev_rows if x["arm"] == arm and x["season"] == season and x["kind"] == "model")
            gz = next(x for x in dev_rows if x["arm"] == "gate_zero" and x["season"] == season and x["kind"] == "model")
            signs[season] = {"arm_ll": row["ll_1x2"], "gate_zero_ll": gz["ll_1x2"], "no_worse": row["ll_1x2"] <= gz["ll_1x2"]}
        clean_hw, clean_ou = abs(cal_hw) <= .01, abs(cal_ou) <= .01
        provisional_hw = not clean_hw and abs(cal_hw) <= .01 + hw_se
        provisional_ou = not clean_ou and abs(cal_ou) <= .01 + ou_se
        result["arms"][arm] = {"metrics": met, "climatology": clim, "max_train_date": max_train_date.isoformat(), "calibration": {"home_win_diff": cal_hw, "home_win_se": hw_se, "home_win_clean": clean_hw, "home_win_provisional": provisional_hw, "over25_diff": cal_ou, "over25_se": ou_se, "over25_clean": clean_ou, "over25_provisional": provisional_ou}, "legs": {"leg_1_1x2_vs_gate_zero_and_climatology": False, "leg_2_calibration": (clean_hw or provisional_hw) and (clean_ou or provisional_ou), "leg_3_dev_season_sign": arm == "gate_zero" or sum(x["no_worse"] for x in signs.values()) >= 3}, "dev_season_sign": signs, "params": {"a": dict(model.a), "d": dict(model.d), "h": model.h, "rho": model.rho, "mu": model.mu, "arm": arm, "match_counts": dict(counts)}, "_preds": preds}
    gz = result["arms"]["gate_zero"]["metrics"]["ll_1x2"]
    for info in result["arms"].values():
        info["legs"]["leg_1_1x2_vs_gate_zero_and_climatology"] = info["metrics"]["ll_1x2"] <= gz and info["metrics"]["ll_1x2"] <= clim["ll_1x2"]
    passing = [a for a, x in result["arms"].items() if all(x["legs"].values())]
    if passing:
        winner = min(passing, key=lambda a: (result["arms"][a]["metrics"]["ll_1x2"], 0 if a == "gate_zero" else 1))
        result["winner"], result["verdict"] = winner, "PASS"
        params = result["arms"][winner]["params"]
        recon = DC_from_params(params)
        pp = []
        for r in target:
            lh, la = adjusted_lambdas(recon, r["hi"], r["ai"], winner, params["match_counts"])
            p = recon.probs(lh, la); p.update({"lh": lh, "la": la, "model": recon}); pp.append(p)
        _write_predictions(target, pp)
        (OUT / "fitted_params_virgin.json").write_text(json.dumps(params, indent=2, sort_keys=True) + "\n")
    for info in result["arms"].values():
        info.pop("params", None); info.pop("_preds", None)
    result["climatology"] = clim
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def DC_from_params(params):
    m = DC(); m.a.update(params["a"]); m.d.update(params["d"]); m.h = params["h"]; m.rho = params["rho"]; m.mu = params["mu"]; return m
