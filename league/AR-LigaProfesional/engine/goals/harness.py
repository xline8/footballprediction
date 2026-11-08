"""G-AR walk-forward harness; dev and virgin are separate invocations."""
import csv, json, math
from datetime import date
from pathlib import Path
from dc import DC
from arms import mover_ids, x3_multipliers, adjusted_lambdas

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "ar_matches.csv"
OUT = Path(__file__).resolve().parent
DEV = ("2022", "2023", "2024", "2025 - Apertura", "2025 - Clausura", "2026 - Apertura")
ALL = ("2021",) + DEV + ("2026 - Clausura",)
VIRGIN = "2026 - Clausura"

def num(v):
    if v in (None, "", "nan", "NaN"): return None
    x = float(v); return None if math.isnan(x) else x

def load(seasons):
    out = []
    with DATA.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] not in seasons: continue
            out.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]), "home": r["home_team"], "away": r["away_team"],
                "yh": int(float(r["home_goals"])), "ya": int(float(r["away_goals"])),
                "xgh": num(r["expected_goals_home"]), "xga": num(r["expected_goals_away"]),
                "oph": num(r["expected_goals_open_play_home"]), "opa": num(r["expected_goals_open_play_away"]),
                "sph": num(r["expected_goals_set_play_home"]), "spa": num(r["expected_goals_set_play_away"])})
    return sorted(out, key=lambda x: (x["date"], x["match_id"]))

def scores(rows, ps):
    n = len(rows); ll = rps = ou = 0.0
    for r, p in zip(rows, ps):
        y = [1, 0, 0] if r["yh"] > r["ya"] else ([0, 1, 0] if r["yh"] == r["ya"] else [0, 0, 1])
        q = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(q[y.index(1)], 1e-12)); rps += .5 * ((q[0]-y[0])**2 + (q[0]+q[1]-y[0]-y[1])**2)
        z = int(r["yh"] + r["ya"] > 2.5); ou -= math.log(max(p["over25"] if z else 1-p["over25"], 1e-12))
    return {"n": n, "ll_1x2": ll/n, "rps": rps/n, "oull_2_5": ou/n}

def clim(train, target):
    n = len(train); ph = sum(x["yh"] > x["ya"] for x in train)/n; pd = sum(x["yh"] == x["ya"] for x in train)/n
    po = sum(x["yh"] + x["ya"] > 2.5 for x in train)/n
    return scores(target, [{"ph": ph, "pd": pd, "pa": 1-ph-pd, "over25": po} for _ in target])

def fit_predict(train, target, arm):
    cut = min(x["date"] for x in target); prior = [x for x in train if x["date"] < cut]; m = DC().fit(prior, cut)
    movers = mover_ids(target[0]["season"], train + target); mult = x3_multipliers(prior, cut) if arm == "x3" else {}
    return m, movers, mult

def evaluate(rows, arms):
    result = []; pools = {a: [] for a in arms}; cpools = []
    for s in DEV:
        target = [x for x in rows if x["season"] == s]; train = [x for x in rows if x["date"] < min(y["date"] for y in target)]
        n = len(train); ph = sum(x["yh"] > x["ya"] for x in train)/n; pd = sum(x["yh"] == x["ya"] for x in train)/n
        po = sum(x["yh"] + x["ya"] > 2.5 for x in train)/n
        cp = {"ph": ph, "pd": pd, "pa": 1-ph-pd, "over25": po}
        cpools += [(target[i], cp) for i in range(len(target))]
        for a in arms:
            m, movers, mult = fit_predict(train, target, a); ps = []
            for r in target:
                lh, la = adjusted_lambdas(m, r["hi"], r["ai"], a, movers, mult); p = m.probs(lh, la); p.update(lh=lh, la=la); ps.append(p)
            z = scores(target, ps); z.update(arm=a, season=s, kind="model"); result.append(z); pools[a] += list(zip(target, ps))
        z = scores(target, [cp for _ in target]); z.update(arm="all", season=s, kind="climatology"); result.append(z)
    for a, pairs in pools.items():
        z = scores([x[0] for x in pairs], [x[1] for x in pairs]); z.update(arm=a, season="pooled", kind="model"); result.append(z)
    z = scores([x[0] for x in cpools], [x[1] for x in cpools]); z.update(arm="all", season="pooled", kind="climatology"); result.append(z)
    return result

def write_dev(result):
    (OUT/"results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with (OUT/"results_dev.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows({k: x.get(k, "") for k in fields} for x in result)

def dev():
    rows = load(set(("2021",) + DEV)); assert len(rows) == 1854 + 325 and not any(x["season"] == VIRGIN for x in rows)
    result = evaluate(rows, ("gate_zero", "x2", "x3")); write_dev(result)
    for x in result: print(x["arm"], x["season"], x["kind"], x["n"], x["ll_1x2"], x["rps"], x["oull_2_5"])
    return result

def virgin():
    result = json.loads((OUT/"results_dev.json").read_text()); passed = []
    base = next(x for x in result if x["season"] == "pooled" and x["kind"] == "climatology")
    for a in ("gate_zero", "x2", "x3"):
        p = next(x for x in result if x["arm"] == a and x["season"] == "pooled" and x["kind"] == "model")
        if p["ll_1x2"] < base["ll_1x2"] and p["rps"] < base["rps"] and p["oull_2_5"] < base["oull_2_5"]: passed.append(a)
    rows = load(set(ALL)); target = [x for x in rows if x["season"] == VIRGIN]; train = [x for x in rows if x["season"] != VIRGIN]
    read = passed or ["gate_zero"]; out = {}
    for a in read:
        m, movers, mult = fit_predict(train, target, a); ps = []
        for r in target:
            lh, la = adjusted_lambdas(m, r["hi"], r["ai"], a, movers, mult); p = m.probs(lh, la); p.update(lh=lh, la=la); ps.append(p)
        z = scores(target, ps); cp = clim(train, target)
        dh = sum(p["ph"] for p in ps)/len(ps) - sum(r["yh"] > r["ya"] for r in target)/len(target)
        do = sum(p["over25"] for p in ps)/len(ps) - sum(r["yh"] + r["ya"] > 2.5 for r in target)/len(target)
        z.update(arm=a, climatology=cp, calibration={"home_win_diff": dh, "over25_diff": do},
                 params={"a": dict(m.a), "d": dict(m.d), "h": m.h, "rho": m.rho, "mu": m.mu, "movers": sorted(movers), "x3_multipliers": mult})
        out[a] = z
    (OUT/"results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    (OUT/"fitted_params_virgin.json").write_text(json.dumps(out[read[0]]["params"], indent=2) + "\n")
    print(json.dumps({"read_arms": read, "virgin": {a: {k: x.get(k) for k in ("n", "ll_1x2", "rps", "oull_2_5", "calibration")} for a, x in out.items()}}, indent=2))
