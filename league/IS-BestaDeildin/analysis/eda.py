"""Phase A descriptive inventory and EDA for IS-BestaDeildin."""
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = list(csv.DictReader(open(HERE.parent / "data" / "is_matches.csv")))
STR = {"match_id","league","season","date","round","league_round_name","phase","league_name","home_team","away_team","cards_source","ht_source","referee"}
for r in M:
    for k in r:
        if k not in STR:
            try: r[k] = float(r[k]) if r[k] != "" else None
            except ValueError: pass
SEASONS = ["2021","2022","2023","2024","2025","2026"]
DEV = ["2022","2023","2024","2025"]
STATS = [r for r in M if r["has_stats_all"] == 1]

def avg(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.mean(xs), 4) if xs else None

def corr(pairs):
    pairs = [(x,y) for x,y in pairs if x is not None and y is not None]
    if len(pairs) < 2: return None
    mx, my = avg([x for x,_ in pairs]), avg([y for _,y in pairs])
    vx = sum((x-mx)**2 for x,y in pairs); vy = sum((y-my)**2 for x,y in pairs)
    return round(sum((x-mx)*(y-my) for x,y in pairs) / math.sqrt(vx*vy), 4) if vx and vy else None

def trait(hkey, akey, seasons, minimum=8):
    halves = defaultdict(lambda: [[], []]); count = defaultdict(int)
    rows = sorted([r for r in M if r["season"] in seasons and r[hkey] is not None], key=lambda r:(r["date"], r["match_id"]))
    for r in rows:
        for tid, val in ((r["home_team_id"], r[hkey]), (r["away_team_id"], r[akey])):
            halves[tid][count[tid] % 2].append(val); count[tid] += 1
    pairs = [(avg(x), avg(y)) for x,y in halves.values() if len(x) >= minimum and len(y) >= minimum]
    return {"n_teams": len(pairs), "r": corr(pairs)}

def split_share(key, seasons):
    rows = [r for r in M if r["season"] in seasons and r[f"fh_{key}_home"] is not None]
    rows = [r for r in rows if (r[f"{key}_home"] or 0) + (r[f"{key}_away"] or 0) > 0]
    n = sum(r[f"fh_{key}_home"] + r[f"fh_{key}_away"] for r in rows)
    d = sum(r[f"{key}_home"] + r[f"{key}_away"] for r in rows)
    return {"share": round(n/d, 4) if d else None, "n_matches": len(rows)}

levels = {}
for s in SEASONS:
    rows = [r for r in M if r["season"] == s]; st = [r for r in rows if r["has_stats_all"]]
    levels[s] = {"n":len(rows), "stats_n":len(st), "splits_n":sum(r["has_stats_half"] for r in rows),
                 "referee_named":sum(bool(r["referee"]) for r in rows),
                 "goals":avg([r["home_goals"]+r["away_goals"] for r in rows]),
                 "home_goals":avg([r["home_goals"] for r in rows]), "away_goals":avg([r["away_goals"] for r in rows]),
                 "sot":avg([r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"] for r in st]),
                 "corners":avg([r["corners_home"]+r["corners_away"] for r in st]),
                 "shots":avg([r["total_shots_home"]+r["total_shots_away"] for r in st]),
                 "yellows_stats":avg([r["stats_yellow_home"]+r["stats_yellow_away"] for r in st]),
                 "big_chance_coverage":sum(r["big_chance_home"] is not None and r["big_chance_away"] is not None for r in rows),
                 "touches_opp_box_coverage":sum(r["touches_opp_box_home"] is not None and r["touches_opp_box_away"] is not None for r in rows),
                 "shotmap_n":sum(r["has_shotmap"] for r in rows)}

traits = {}
for name, h, a in [("goals_for","home_goals","away_goals"),("goals_against","away_goals","home_goals"),
 ("sot_for","ShotsOnTarget_home","ShotsOnTarget_away"),("sot_against","ShotsOnTarget_away","ShotsOnTarget_home"),
 ("corners_for","corners_home","corners_away"),("corners_against","corners_away","corners_home"),
 ("shots_for","total_shots_home","total_shots_away"),("shots_against","total_shots_away","total_shots_home"),
 ("yellows_for","stats_yellow_home","stats_yellow_away"),("yellows_against","stats_yellow_away","stats_yellow_home"),
 ("possession","BallPossesion_home","BallPossesion_away"),("box_touches_for","touches_opp_box_home","touches_opp_box_away")]:
    traits[name] = trait(h, a, ["2023","2024","2025"] if name not in ("goals_for","goals_against") else SEASONS)

ref_half = defaultdict(lambda: [[], []]); ref_count = defaultdict(int)
for r in sorted([x for x in M if x["season"] in DEV and x["referee"] and x["stats_yellow_home"] is not None], key=lambda x:(x["date"],x["match_id"])):
    i = ref_count[r["referee"]] % 2; ref_half[r["referee"]][i].append(r["stats_yellow_home"]+r["stats_yellow_away"]); ref_count[r["referee"]] += 1
ref_pairs = [(avg(x),avg(y)) for x,y in ref_half.values() if len(x)>=5 and len(y)>=5]

def variance_test(key):
    rows = [r for r in M if r["season"] in ["2023","2024","2025"] and r[f"fh_{key}_home"] is not None]
    shares = []; total = 0; first = 0
    for r in rows:
        den = r[f"{key}_home"] + r[f"{key}_away"]
        if den > 0: shares.append((r[f"fh_{key}_home"]+r[f"fh_{key}_away"])/den); total += den; first += r[f"fh_{key}_home"]+r[f"fh_{key}_away"]
    p = first/total; return {"share":round(p,4),"n_matches":len(shares),"observed_var":round(statistics.variance(shares),4),"expected_binomial_var":round(p*(1-p)/(total/len(shares)),4)}

out = {"seasons": SEASONS, "n": len(M), "levels": levels, "traits": traits,
       "corr_box_touches_corners": {"n":len([r for r in STATS if r["touches_opp_box_home"] is not None]), "r":corr([(r["touches_opp_box_home"]+r["touches_opp_box_away"], r["corners_home"]+r["corners_away"]) for r in STATS if r["touches_opp_box_home"] is not None])},
       "referee_trait": {"n_referees":len(ref_pairs),"r":corr(ref_pairs),"referees_total":len(ref_half)},
       "referee_coverage": {s:{"named":levels[s]["referee_named"],"n":levels[s]["n"]} for s in SEASONS},
       "halves_variance": {k:variance_test(k) for k in ("ShotsOnTarget","corners","total_shots","yellow_cards")},
       "halves_constants": {"goals":0.4455,"ShotsOnTarget":0.4644,"corners":0.4707,"total_shots":0.4623,"yellow_cards":0.3499},
       "halves_splits": {k:split_share(k,["2023","2024","2025"]) for k in ("ShotsOnTarget","corners","total_shots","yellow_cards")},
       "cards_stats_vs_events": {}, "phase_levels": {}, "dev_over_rates": {},
       "team_ids_total": len(set([r["home_team_id"] for r in M]+[r["away_team_id"] for r in M]))}
for s in SEASONS:
    rows=[r for r in M if r["season"]==s and r["stats_yellow_home"] is not None and r["stats_yellow_away"] is not None]
    out["cards_stats_vs_events"][s]={"n":len(rows),"exact":round(avg([r["stats_yellow_home"]+r["stats_yellow_away"]==r["ev_yellow_home"]+r["ev_yellow_away"] for r in rows]),4) if rows else None,"mean_stats_minus_events":round(avg([(r["stats_yellow_home"]+r["stats_yellow_away"])-(r["ev_yellow_home"]+r["ev_yellow_away"]) for r in rows]),4) if rows else None}
    for p in ("regular","championship","relegation"):
        pr=[r for r in M if r["season"]==s and r["phase"]==p]
        if pr: out["phase_levels"][f"{s}_{p}"]={"n":len(pr),"goals":avg([r["home_goals"]+r["away_goals"] for r in pr])}
for key, fn, lines in [("goals",lambda r:r["home_goals"]+r["away_goals"],[2.5]),("sot",lambda r:r["ShotsOnTarget_home"]+r["ShotsOnTarget_away"],[9.5]),("corners",lambda r:r["corners_home"]+r["corners_away"],[11.5]),("cards",lambda r:r["stats_yellow_home"]+r["stats_yellow_away"],[4.5]),("shots",lambda r:r["total_shots_home"]+r["total_shots_away"],[27.5])]:
    rows=[r for r in M if r["season"] in DEV and (key=="goals" or r["has_stats_all"])]
    out["dev_over_rates"][key]={str(line):round(avg([fn(r)>line for r in rows]),4) for line in lines}
out["home_advantage"]={s:{"home_goals":levels[s]["home_goals"],"away_goals":levels[s]["away_goals"],"difference":round(levels[s]["home_goals"]-levels[s]["away_goals"],4)} for s in SEASONS}
inventory={"by_season":{s:{"n":levels[s]["n"],"stats_n":levels[s]["stats_n"],"splits_n":levels[s]["splits_n"],"referee_named":levels[s]["referee_named"],"big_chance_n":levels[s]["big_chance_coverage"],"touches_opp_box_n":levels[s]["touches_opp_box_coverage"],"shotmap_n":levels[s]["shotmap_n"]} for s in SEASONS},"team_ids_total":out["team_ids_total"]}
json.dump(out, open(HERE/"eda_summary.json","w"), indent=2)
json.dump(inventory, open(HERE/"inventory_summary.json","w"), indent=2)
print(json.dumps(out, indent=2))
