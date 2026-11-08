"""Phase-A EDA for PBM. All descriptive statistics exclude 2026."""
from __future__ import annotations
import csv, json, math, os
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
M = list(csv.DictReader((HERE.parent / "data" / "pbm_matches.csv").open(encoding="utf-8")))
EDA_SEASONS = ["2021", "2022", "2023", "2024", "2025"]
DEV = [r for r in M if r["season"] in EDA_SEASONS]

def f(r, k):
    try: return float(r.get(k, ""))
    except (TypeError, ValueError): return np.nan
def finite(x): return np.asarray(x, float)[np.isfinite(x)]
def mean(x):
    x = finite(x); return float(np.mean(x)) if len(x) else None
def pct(x): return float(100 * np.mean(np.asarray(x, float)))
def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float); z = np.isfinite(a) & np.isfinite(b)
    return float(np.corrcoef(a[z], b[z])[0, 1]) if z.sum() > 2 and np.std(a[z]) and np.std(b[z]) else None
def dispersion(x):
    x = finite(x); return float(np.var(x, ddof=1) / np.mean(x)) if len(x) > 1 and np.mean(x) else None

def levels(rs):
    g = np.array([f(r, "home_goals") + f(r, "away_goals") for r in rs]); h = np.array([f(r, "home_goals") for r in rs]); a = np.array([f(r, "away_goals") for r in rs])
    return {"n_matches": len(rs), "goals_per_match": mean(g), "home_goals": mean(h), "away_goals": mean(a),
            "home_draw_away_pct": [pct(h > a), pct(h == a), pct(h < a)], "home_advantage_goals": mean(h - a),
            "btts_pct": pct((h > 0) & (a > 0)), "over_1_5_pct": pct(g > 1.5), "over_2_5_pct": pct(g > 2.5),
            "over_3_5_pct": pct(g > 3.5), "dispersion_var_mean": dispersion(g)}

def split_r(groups, fn, min_matches=24, seed=9213):
    rng = np.random.default_rng(seed); vals = []
    for _ in range(60):
        x, y = [], []
        for rs in groups.values():
            a = finite([fn(r) for r in rs])
            if len(a) < min_matches: continue
            ix = rng.permutation(len(a)); n = len(a) // 2; x.append(np.mean(a[ix[:n]])); y.append(np.mean(a[ix[n:]]))
        q = corr(x, y)
        if q is not None: vals.append(q)
    odd, even = [], []
    for rs in groups.values():
        a = finite([fn(r) for r in rs])
        if len(a) >= min_matches: odd.append(np.mean(a[::2])); even.append(np.mean(a[1::2]))
    return {"r": mean(vals), "n_splits": len(vals), "career_pooled_teams": len(odd), "odd_even_r": corr(odd, even)}

def halves(rs):
    pairs = []
    for r in rs:
        total = f(r, "home_goals") + f(r, "away_goals"); first = f(r, "ht_home_goals") + f(r, "ht_away_goals")
        if total > 0 and np.isfinite(first): pairs.append((first, total))
    share = sum(a for a, _ in pairs) / sum(b for _, b in pairs); observed = np.var([a / b for a, b in pairs], ddof=1); noise = float(np.mean([share * (1 - share) / b for _, b in pairs]))
    by_team = defaultdict(list)
    for r in rs:
        total = f(r, "home_goals") + f(r, "away_goals"); first = f(r, "ht_home_goals") + f(r, "ht_away_goals")
        if total > 0 and np.isfinite(first): by_team[r["home_team_id"]].append(first / total); by_team[r["away_team_id"]].append(first / total)
    groups = {k: [{"v": x} for x in v] for k, v in by_team.items()}
    return {"n_matches": len(pairs), "share_1h": float(share), "observed_variance": float(observed), "noise_floor_per_match": noise, "true_variance": float(observed - noise), "team_share_split_half": split_r(groups, lambda q: q["v"])}

def warehouse_root():
    candidates = ([Path(os.environ["FOTMOB_WAREHOUSE"])] if os.environ.get("FOTMOB_WAREHOUSE") else []) + [Path("/home/hatch/workspace/footballprediction/data_enrichment"), HERE.parents[3] / "data_enrichment"]
    for p in candidates:
        if (p / "fotmob_world_index.csv").is_file(): return p
    raise FileNotFoundError("warehouse index not found")
def load_payload(root, rel):
    for p in (root / rel, root.parent / rel, Path("/home/hatch/workspace/footballprediction") / rel):
        if p.is_file(): return json.loads(p.read_text())
    raise FileNotFoundError(rel)
def national_membership():
    root = warehouse_root(); out = defaultdict(set)
    with (root / "fotmob_world_index.csv").open(newline="", encoding="utf-8") as fh:
        for ir in csv.DictReader(fh):
            if ir.get("league_id") != "8965" or ir.get("season") not in EDA_SEASONS: continue
            x = load_payload(root, ir["path"])
            out[ir["season"]].update(str(t["id"]) for t in ((x.get("header") or {}).get("teams") or []) if t.get("id") is not None)
    return out
def movers():
    by = {s: set() for s in EDA_SEASONS}
    for r in M:
        if r["season"] in by: by[r["season"]].update((r["home_team_id"], r["away_team_id"]))
    nac = national_membership(); records = []; output = {}
    for i in range(1, len(EDA_SEASONS)):
        prev, season = EDA_SEASONS[i-1], EDA_SEASONS[i]; newcomers = sorted(by[season] - by[prev]); season_rows = [r for r in M if r["season"] == season]
        league_mean = np.mean([f(r, "home_goals") for r in season_rows] + [f(r, "away_goals") for r in season_rows]); current = []
        for tid in newcomers:
            tr = []
            for r in season_rows:
                if r["home_team_id"] == tid: tr.append((f(r, "home_goals"), f(r, "away_goals"), r["home_team"]))
                elif r["away_team_id"] == tid: tr.append((f(r, "away_goals"), f(r, "home_goals"), r["away_team"]))
            direction = "from_nacional" if tid in nac.get(prev, set()) else "from_below_or_cross_competition"
            current.append({"team_id": tid, "team_name": tr[0][2], "direction": direction, "n_matches": len(tr), "gf_gap": float(np.mean([x[0] for x in tr]) - league_mean), "ga_gap": float(np.mean([x[1] for x in tr]) - league_mean)})
        records.extend(current); output[season] = {"newcomers": current, "n_newcomers": len(current)}
    pooled = {"n_team_blocks": len(records), "gf_gap": mean([x["gf_gap"] for x in records]), "ga_gap": mean([x["ga_gap"] for x in records]), "by_direction": {}}
    for direction in ("from_nacional", "from_below_or_cross_competition"):
        q = [x for x in records if x["direction"] == direction]; pooled["by_direction"][direction] = {"n": len(q), "gf_gap": mean([x["gf_gap"] for x in q]), "ga_gap": mean([x["ga_gap"] for x in q])}
    output["pooled_2022_2025"] = pooled; return output
def clean(x):
    if isinstance(x, float) and not math.isfinite(x): return None
    if isinstance(x, dict): return {k: clean(v) for k, v in x.items()}
    if isinstance(x, list): return [clean(v) for v in x]
    return x

def main():
    formats = {"2021": "Apertura + Clausura, 17 teams, 136 matches each", "2022": "Apertura + Clausura, 17 teams, 136 matches each", "2023": "Apertura + Clausura, 17 teams, 136 matches each", "2024": "Apertura + Clausura, 22 teams, 231 matches each", "2025": "Apertura + Clausura, 21 teams, 210 matches each", "2026": "virgin definition only: single table, 22 teams, rounds 1–42, 462 group matches"}
    seasons, inventory = {}, {}
    for s in EDA_SEASONS:
        rs = [r for r in M if r["season"] == s]; seasons[s] = levels(rs)
        inventory[s] = {"n_matches": len(rs), "distinct_teams": len({r["home_team_id"] for r in rs} | {r["away_team_id"] for r in rs}), "date_range": [min(r["date"] for r in rs), max(r["date"] for r in rs)], "format": formats[s], "coverage": {"events_pct": pct([r["has_events"] == "True" for r in rs]), "referee_pct": 0.0, "stats_nonempty_pct": 0.0, "shotmap_nonempty_pct": 0.0}}
    inventory["2026"] = {"n_matches": 462, "virgin": True, "format": formats["2026"], "completeness_basis": "inventory count; no outcomes/statistics used"}
    groups = defaultdict(list)
    for r in DEV:
        groups[r["home_team_id"]].append({"goals_for": f(r, "home_goals"), "goals_against": f(r, "away_goals")}); groups[r["away_team_id"]].append({"goals_for": f(r, "away_goals"), "goals_against": f(r, "home_goals")})
    reliability = {name: split_r(groups, lambda x, k=key: x[k]) for name, key in (("goals_for", "goals_for"), ("goals_against", "goals_against"))}
    summary = {"scope": {"eda_seasons": EDA_SEASONS, "virgin_excluded": "2026; no descriptive statistics computed"}, "seasons": seasons, "pooled": levels(DEV), "home_advantage_goals": levels(DEV)["home_advantage_goals"], "reliability": reliability, "halves": {"goals": halves(DEV)}, "referees": {"coverage_by_season": {s: 0.0 for s in EDA_SEASONS}, "coverage_pct": 0.0}, "movers": movers(), "primary_lines": {"goals": {"OU1.5": pct([f(r, "home_goals") + f(r, "away_goals") > 1.5 for r in DEV]), "OU2.5": pct([f(r, "home_goals") + f(r, "away_goals") > 2.5 for r in DEV]), "OU3.5": pct([f(r, "home_goals") + f(r, "away_goals") > 3.5 for r in DEV])}}, "absent": {"stats_payloads_nonempty": 0, "shotmap_shots": 0, "sot": 0, "corners": 0, "yellow_card_events": 0, "total_shots": 0, "xg": 0}}
    (HERE / "inventory_summary.json").write_text(json.dumps(clean(inventory), indent=2, ensure_ascii=False) + "\n")
    (HERE / "eda_summary.json").write_text(json.dumps(clean(summary), indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    print(json.dumps({"eda_matches": len(DEV), "pooled": summary["pooled"], "primary_lines": summary["primary_lines"], "movers": summary["movers"]["pooled_2022_2025"], "halves": summary["halves"]["goals"]}, indent=2))
if __name__ == "__main__": main()
