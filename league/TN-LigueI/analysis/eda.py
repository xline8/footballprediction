"""CSV-only inventory and exploratory summaries for Tunisia Ligue I."""
import csv, json, math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "data" / "tn_matches.csv"
INV = HERE / "inventory_summary.json"
EDA = HERE / "eda_summary.json"
rows = list(csv.DictReader(open(CSV)))
for r in rows:
    for k in ("home_goals", "away_goals", "home_team_id", "away_team_id", "goal_events", "half_events", "card_events", "yellow_events", "red_events", "yellowred_events"):
        r[k] = int(r[k])
    for k in ("has_stats", "has_shotmap", "referee_named", "has_events", "is_awarded"):
        r[k] = int(r[k])
    r["g"] = r["home_goals"] + r["away_goals"]

seasons = sorted({r["season"] for r in rows})
# Model rows: every played league match except the 9 awarded ones.
# All phases (group / championship / relegation / placement / regular)
# are league matches with 90-minute scores and enter the model data.
model = [r for r in rows if r["is_awarded"] == 0]

def level(rs):
    n = len(rs); g = sum(r["g"] for r in rs)
    return {"n": n, "goals_per_match": g/n, "home_goals": sum(r["home_goals"] for r in rs)/n,
            "away_goals": sum(r["away_goals"] for r in rs)/n,
            "home_win": sum(r["home_goals"] > r["away_goals"] for r in rs)/n,
            "draw": sum(r["home_goals"] == r["away_goals"] for r in rs)/n,
            "away_win": sum(r["home_goals"] < r["away_goals"] for r in rs)/n,
            "ou15": sum(r["g"] > 1 for r in rs)/n, "ou25": sum(r["g"] > 2 for r in rs)/n,
            "ou35": sum(r["g"] > 3 for r in rs)/n, "btts": sum(r["home_goals"] > 0 and r["away_goals"] > 0 for r in rs)/n}

def pearson(x, y):
    mx, my = sum(x)/len(x), sum(y)/len(y)
    a = sum((v-mx)**2 for v in x); b = sum((v-my)**2 for v in y)
    return sum((u-mx)*(v-my) for u,v in zip(x,y)) / math.sqrt(a*b)

def reliability(ss):
    gf1=[]; gf2=[]; ga1=[]; ga2=[]
    for s in ss:
        rs=sorted([r for r in model if r["season"]==s], key=lambda r:(r["date"], int(r["match_id"])))
        f=defaultdict(list); a=defaultdict(list)
        for r in rs:
            f[r["home_team_id"]].append(r["home_goals"]); a[r["home_team_id"]].append(r["away_goals"])
            f[r["away_team_id"]].append(r["away_goals"]); a[r["away_team_id"]].append(r["home_goals"])
        for t in f:
            h=len(f[t])//2
            if h >= 5:
                gf1.append(sum(f[t][:h])/h); gf2.append(sum(f[t][h:])/(len(f[t])-h))
                ga1.append(sum(a[t][:h])/h); ga2.append(sum(a[t][h:])/(len(a[t])-h))
    return {"n_team_seasons":len(gf1), "gf_r":pearson(gf1,gf2), "ga_r":pearson(ga1,ga2)}

def halves(rs):
    used=[r for r in rs if r["goals_1h"] != "" and r["goal_events"] == r["home_goals"]+r["away_goals"]]
    g1=sum(int(r["goals_1h"]) for r in used); g=sum(r["g"] for r in used)
    shares=[int(r["goals_1h"])/r["g"] for r in used if r["g"]]
    p=g1/g
    obs=sum((x-p)**2 for x in shares)/len(shares)
    exp=sum(p*(1-p)/r["g"] for r in used if r["g"])/len(shares)
    true_var=max(0.0, obs-exp)
    return {"first_half_goals":g1,"goals":g,"matches_used":len(used),"share":p,
            "observed_variance":obs,"binomial_noise_expectation":exp,"variance_ratio":obs/exp,
            "implied_true_sd":math.sqrt(true_var)}

# Entrants by team ID (names have accent variants: id 8153 is both
# "Esperance" and "Espérance", so name-based entrant lists are wrong).
id_to_names = defaultdict(set)
for r in rows:
    id_to_names[r["home_team_id"]].add(r["home_team"])
    id_to_names[r["away_team_id"]].add(r["away_team"])
entrants = {}
prev_ids = set()
for s in seasons:
    ids = {r["home_team_id"] for r in rows if r["season"] == s} | {r["away_team_id"] for r in rows if r["season"] == s}
    entrants[s] = sorted((i, sorted(id_to_names[i])[0]) for i in ids - prev_ids)
    prev_ids |= ids

inv = {"league": "TN-LigueI", "fotmob_id": 544, "index_rows": len(rows), "payloads_present": len(rows),
       "parentLeagueId_distribution": {"544": len(rows)},
       "leagueName_distribution": dict(Counter(r["league_name"] for r in rows)),
       "phase_distribution": dict(Counter(r["phase"] for r in rows)),
       "coverage": {"stats": sum(r["has_stats"] for r in rows),
                    "shotmap": sum(r["has_shotmap"] for r in rows),
                    "referee_named": sum(r["referee_named"] for r in rows),
                    "scores": len(rows),
                    "goal_events_match_nonempty": sum(r["has_events"] for r in rows)},
       "events": dict(Counter({"Goal": sum(r["goal_events"] for r in rows),
                               "Half": sum(r["half_events"] for r in rows),
                               "Card": sum(r["card_events"] for r in rows),
                               "Card_Red": sum(r["red_events"] for r in rows),
                               "Card_YellowRed": sum(r["yellowred_events"] for r in rows),
                               "Card_Yellow": sum(r["yellow_events"] for r in rows)})),
       "seasons": {}, "awarded_match_ids": sorted(r["match_id"] for r in rows if r["is_awarded"]),
       "entrants_by_team_id": {s: [[i, n] for i, n in v] for s, v in entrants.items()},
       "team_name_variants": {str(k): sorted(v) for k, v in id_to_names.items() if len(v) > 1}}
for s in seasons:
    sr = [r for r in rows if r["season"] == s]
    mr = [r for r in sr if r["is_awarded"] == 0]
    teams = sorted({r["home_team_id"] for r in sr} | {r["away_team_id"] for r in sr})
    inv["seasons"][s] = {"n": len(sr), "model_rows": len(mr),
                         "awarded": len(sr) - len(mr), "teams": len(teams),
                         "phases": dict(Counter(r["phase"] for r in sr))}

levels = {s: level([r for r in model if r["season"] == s]) for s in seasons}
dev = [r for r in model if r["season"] in {"2022/2023", "2023/2024", "2024/2025"}]
out = {"league": "TN-LigueI",
       "levels_by_season": levels,
       "levels_by_phase": {p: level([r for r in model if r["phase"] == p]) for p in sorted({r["phase"] for r in model})},
       "dev_pooled": level(dev),
       "virgin_pooled": level([r for r in model if r["season"] == "2025/2026"]),
       "windows": {"warmup": "2021/2022", "dev_scored": ["2022/2023", "2023/2024", "2024/2025"],
                   "dev_scored_n": len(dev), "virgin": "2025/2026 (inventory only)",
                   "confirmatory_reserve": "2026/2027 partial (inventory only)"},
       "trait_reliability": {"dev_era_2021_2025": reliability(seasons[:4]),
                             "scored_window_2022_2025": reliability(seasons[1:4])},
       "goals_1h_share": {"per_season": {s: halves([r for r in model if r["season"] == s]) for s in seasons},
                          "dev_pooled": halves(dev)}}
INV.write_text(json.dumps(inv, indent=2, sort_keys=True) + "\n")
EDA.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print("wrote", INV, EDA)
print(json.dumps(out, indent=2))
print(json.dumps({k: inv[k] for k in ("awarded_match_ids", "entrants_by_team_id", "team_name_variants")}, indent=2))
