"""CSV-only inventory and exploratory summaries for NI-Premiership."""
import csv, json, math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "data" / "ni_matches.csv"
INV = HERE / "inventory_summary.json"
EDA = HERE / "eda_summary.json"
rows = list(csv.DictReader(open(CSV)))
for r in rows:
    for k in ("home_goals", "away_goals", "home_team_id", "away_team_id", "goal_events", "half_events", "card_events", "yellow_events", "red_events", "yellowred_events"):
        r[k] = int(r[k])
    for k in ("has_stats", "has_shotmap", "referee_named", "has_events", "is_playoff"):
        r[k] = int(r[k])
    r["g"] = r["home_goals"] + r["away_goals"]

seasons = sorted({r["season"] for r in rows})
regular = [r for r in rows if r["phase"] == "regular"]
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
        rs=sorted([r for r in regular if r["season"]==s], key=lambda r:(r["date"], int(r["match_id"])))
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
    # Per-match share variance uses scored matches; zero-goal matches have no share.
    obs=sum((x-p)**2 for x in shares)/len(shares)
    exp=sum(p*(1-p)/r["g"] for r in used if r["g"])/len(shares)
    true_var=max(0.0, obs-exp)
    return {"first_half_goals":g1,"goals":g,"matches_used":len(used),"share":p,
            "observed_variance":obs,"binomial_noise_expectation":exp,"variance_ratio":obs/exp,
            "implied_true_sd":math.sqrt(true_var)}

inv={"league":"NI-Premiership", "fotmob_id":129, "index_rows":len(rows), "payloads_present":len(rows),
     "parentLeagueId_distribution":{"129":len(rows)}, "leagueName_distribution":dict(Counter(r["league_name"] for r in rows)), "coverage":{"stats":sum(r["has_stats"] for r in rows),
     "shotmap":sum(r["has_shotmap"] for r in rows), "referee_named":sum(r["referee_named"] for r in rows),
     "scores":len(rows), "goal_events_match_nonempty":sum(r["has_events"] for r in rows)},
     "events":dict(Counter({"Goal":sum(r["goal_events"] for r in rows), "Half":sum(r["half_events"] for r in rows),
                             "Card":sum(r["card_events"] for r in rows), "Card_Red":sum(r["red_events"] for r in rows),
                             "Card_YellowRed":sum(r["yellowred_events"] for r in rows),
                             "Card_Yellow":sum(r["yellow_events"] for r in rows)})),
     "seasons":{}, "playoff_counts":{}, "exception_3907917":"header 3-0 vs event trail 1-3; halves missing"}
for s in seasons:
    sr=[r for r in rows if r["season"]==s]; rr=[r for r in sr if r["phase"]=="regular"]
    teams=sorted(set([r["home_team"] for r in sr]+[r["away_team"] for r in sr]))
    inv["seasons"][s]={"n":len(sr),"regular":len(rr),"playoff":len(sr)-len(rr),"teams":len(teams),"team_list":teams}
    inv["playoff_counts"][s]=len(sr)-len(rr)
inv["entrant_lists"]={s:sorted(set(inv["seasons"][s]["team_list"])-set(inv["seasons"][seasons[i-1]]["team_list"])) for i,s in enumerate(seasons) if i}

levels={s:level([r for r in regular if r["season"]==s]) for s in seasons}
dev=[r for r in regular if r["season"] in {"2022/2023","2023/2024","2024/2025"}]
out={"league":"NI-Premiership", "levels_by_season":levels, "dev_pooled":level(dev),
     "virgin_pooled":level([r for r in regular if r["season"]=="2025/2026"]),
     "windows":{"warmup":"2021/2022","dev_scored":["2022/2023","2023/2024","2024/2025"],"dev_scored_n":len(dev),"virgin":"2025/2026 (inventory only)","confirmatory_reserve":"2026/2027 partial (inventory only)"},
     "trait_reliability":{"dev_era_2021_2025":reliability(seasons[:4]),"scored_window_2022_2025":reliability(seasons[1:4])},
     "goals_1h_share":{"per_season":{s:halves([r for r in regular if r["season"]==s]) for s in seasons},"dev_pooled":halves(dev)}}
INV.write_text(json.dumps(inv,indent=2,sort_keys=True)+"\n"); EDA.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
print("wrote",INV,EDA); print(json.dumps(out,indent=2))
