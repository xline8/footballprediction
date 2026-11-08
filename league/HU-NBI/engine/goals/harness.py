"""HU-NBI goals development harness; copied DC/arms mechanics, HU adapter."""
import csv, json, math
from collections import Counter, defaultdict, deque
from datetime import date
from pathlib import Path
from dc import DC
from arms import adjusted_lambdas

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "hu_nbi.csv"
SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
SCORED = SEASONS[1:]
LINE = 2.5

def load(path, allowed):
    allowed = set(allowed)
    assert allowed <= set(SEASONS), "HU loader allow-list blocks virgin seasons"
    out = []
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["season"] not in allowed: continue
            out.append({"match_id": r["match_id"], "season": r["season"], "date": date.fromisoformat(r["date"]),
                        "hi": int(r["home_id"]), "ai": int(r["away_id"]), "home": r["home_team"], "away": r["away_team"],
                        "yh": int(float(r["home_goals"])), "ya": int(float(r["away_goals"])), "xgh": None, "xga": None})
    return sorted(out, key=lambda x: (x["date"], x["match_id"]))

def _score(xs):
    n = len(xs)
    return {"n": n, "ou2.5_ll": sum(-math.log(max(p["over25"] if r["yh"] + r["ya"] > LINE else 1-p["over25"], 1e-12)) for r,p in xs)/n,
            "1x2_ll": sum(-math.log(max(p["ph"] if r["yh"] > r["ya"] else p["pd"] if r["yh"] == r["ya"] else p["pa"], 1e-12)) for r,p in xs)/n}

def prob_metrics(recs):
    return {"pooled": _score(recs), "per_season": {s: _score([x for x in recs if x[0]["season"] == s]) for s in SCORED}}

def dist(model, lh, la):
    p = model.probs(lh, la)
    return {"over25": p["over25"], "ph": p["ph"], "pd": p["pd"], "pa": p["pa"], "lam_home": lh, "lam_away": la}

def baseline_predictions(rows):
    hist = defaultdict(lambda: deque(maxlen=10)); out = []
    for r in rows:
        prior = [x for x in rows if x["date"] < r["date"]]
        train = [x for x in prior if int(x["season"][:4]) < int(r["season"][:4])]
        base = sum(x["yh"]+x["ya"] for x in train) / (2*len(train)) if train else 1.2
        h, a = list(hist[r["hi"]]), list(hist[r["ai"]])
        lh = sum(x[0] for x in h)/len(h) if h else base; la = sum(x[1] for x in a)/len(a) if a else base
        fake = DC(); out.append((r, dist(fake, max(lh, 1e-6), max(la, 1e-6))))
        hist[r["hi"]].append((r["yh"], r["ya"])); hist[r["ai"]].append((r["ya"], r["yh"]))
    return out

def run_dev():
    rows = load(DATA, SEASONS)
    result = {"protocol": {"league": "HU-NBI", "dev_seasons_loaded": list(SEASONS), "virgin_seasons_forbidden": ["2025/2026", "2026/2027"]}, "primary_line": LINE, "arms": {}, "baselines": {}, "gate": {}}
    all_preds = {}
    naive = dict((r["match_id"], p) for r,p in baseline_predictions(rows))
    for arm, arm_name in (("GZ", "gz"), ("SHR", "shr")):
        recs = []
        for season in SCORED:
            target = [r for r in rows if r["season"] == season]; cutoff = min(r["date"] for r in target)
            train = [r for r in rows if r["date"] < cutoff]; model = DC().fit(train, cutoff)
            counts = Counter(t for r in train for t in (r["hi"], r["ai"]))
            for r in target:
                lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm_name, counts, (0,0,0,set()))
                recs.append((r, dist(model, lh, la)))
        all_preds[arm] = recs; result["arms"][arm] = prob_metrics(recs)
    for name, source in (("base_rate", None), ("naive_trailing_10", naive)):
        recs = []
        for r in rows:
            if r["season"] not in SCORED: continue
            if source is None:
                train = [x for x in rows if int(x["season"][:4]) < int(r["season"][:4])]
                rate = sum(x["yh"]+x["ya"] > LINE for x in train) / len(train)
                p = {"over25": rate, "ph": 0.45, "pd": 0.25, "pa": 0.30}
            else: p = source[r["match_id"]]
            recs.append((r,p))
        result["baselines"][name] = prob_metrics(recs)
    for arm in all_preds:
        result["gate"][arm] = {"pooled_beats_base_rate": result["arms"][arm]["pooled"]["ou2.5_ll"] < result["baselines"]["base_rate"]["pooled"]["ou2.5_ll"], "pooled_beats_naive_trailing_10": result["arms"][arm]["pooled"]["ou2.5_ll"] < result["baselines"]["naive_trailing_10"]["pooled"]["ou2.5_ll"]}
    write_outputs(result, all_preds)
    return result

def write_outputs(result, all_preds):
    (HERE / "results_dev.json").write_text(json.dumps(result, indent=2) + "\n")
    for arm, recs in all_preds.items():
        with (HERE / f"dev_predictions_{arm}.csv").open("w", newline="", encoding="utf-8") as fh:
            fields = ["match_id","season","date","home_id","away_id","expected","p_over","p_home","p_draw","p_away","actual","actual_home","actual_away"]
            w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
            for r,p in recs:
                w.writerow({"match_id":r["match_id"],"season":r["season"],"date":r["date"].isoformat(),"home_id":r["hi"],"away_id":r["ai"],"expected":p["lam_home"]+p["lam_away"],"p_over":p["over25"],"p_home":p["ph"],"p_draw":p["pd"],"p_away":p["pa"],"actual":r["yh"]+r["ya"],"actual_home":r["yh"],"actual_away":r["ya"]})
