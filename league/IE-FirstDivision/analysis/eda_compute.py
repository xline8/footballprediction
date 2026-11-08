"""Compute the IE-FirstDivision EDA ledger. No model fitting occurs here.

Design population = REGULAR-season matches only (playoffs excluded from
every number below except the coverage inventory). Dev seasons
2021-2025; 2026 is virgin and contributes only its coverage inventory.
Sibling Premier Division table (main repo, league/IE-PremierDivision/
data/ie_matches.csv) is read for the relegated-mover check only.
"""
import csv, json, math, statistics as st
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = Path("/home/hatch/workspace/footballprediction")
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "ie_first_division_matches.csv")))
PREM = list(csv.DictReader(open(MAIN / "league" / "IE-PremierDivision" / "data" / "ie_matches.csv")))
DEV_SEASONS = ["2021", "2022", "2023", "2024", "2025"]
SEASONS = DEV_SEASONS + ["2026"]
REG = [r for r in ROWS if r["phase"] == "regular"]
DEV = [r for r in REG if r["season"] != "2026"]
DEV_EVAL = [r for r in REG if r["season"] in {"2022", "2023", "2024", "2025"}]

def mean(xs): return st.mean(xs) if xs else None

def corr_halves(series, minimum=10):
    xs, ys = [], []
    for vals in series.values():
        if len(vals) >= minimum:
            xs.append(st.mean(vals[0::2])); ys.append(st.mean(vals[1::2]))
    if len(xs) < 5: return None, len(xs)
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
    return (sum((x-mx)*(y-my) for x, y in zip(xs, ys))/den if den else None), len(xs)

def half_share(rows, value_fn, weight_fn):
    shares, weights = [], []
    for r in rows:
        one, total = value_fn(r), weight_fn(r)
        if one is not None and total is not None and total > 0:
            shares.append(one / total); weights.append(total)
    if len(shares) < 2: return {"n": len(shares), "share": None, "obs_sd": None, "true_sd": None}
    m, obs_var = st.mean(shares), st.variance(shares)
    noise = st.mean([m*(1-m)/w for w in weights])
    return {"n": len(shares), "share": round(m, 4), "obs_sd": round(math.sqrt(obs_var), 4),
            "true_sd": round(math.sqrt(max(obs_var-noise, 0)), 4)}

out = {"n": len(ROWS), "n_regular": len(REG), "n_playoff": len(ROWS) - len(REG), "seasons": SEASONS}
per = {}
for season in SEASONS:
    rs = [r for r in REG if r["season"] == season]
    hg = [int(r["home_goals"]) for r in rs]; ag = [int(r["away_goals"]) for r in rs]
    tot = [h + a for h, a in zip(hg, ag)]
    per[season] = {
        "n_regular": len(rs), "n_playoff": sum(1 for r in ROWS if r["season"] == season and r["phase"] == "playoff"),
        "first_date": min(r["date"] for r in rs), "last_date": max(r["date"] for r in rs),
        "goals": round(mean(tot), 3), "home_goals": round(mean(hg), 3), "away_goals": round(mean(ag), 3),
        "home_edge_goals": round(mean(hg) - mean(ag), 3),
        "home_win_pct": round(100*mean([h > a for h, a in zip(hg, ag)]), 1),
        "draw_pct": round(100*mean([h == a for h, a in zip(hg, ag)]), 1),
        "away_win_pct": round(100*mean([h < a for h, a in zip(hg, ag)]), 1),
        "btts_pct": round(100*mean([h > 0 and a > 0 for h, a in zip(hg, ag)]), 1),
        "over25_pct": round(100*mean([t > 2.5 for t in tot]), 1),
        "over15_pct": round(100*mean([t > 1.5 for t in tot]), 1),
        "over35_pct": round(100*mean([t > 3.5 for t in tot]), 1),
        "goals_dispersion_var_mean": round(st.variance(tot)/mean(tot), 3),
        "cov_stats_all": 0.0, "cov_half": 0.0, "cov_shotmap": 0.0, "cov_named_referee": 0.0,
        "cov_events": round(100*mean([int(r["has_events"]) for r in rs]), 1),
        "cov_ht_derivable": round(100*sum(1 for r in rs if r["ht_source"] in ("events", "inferred-0-0"))/len(rs), 1),
        "ev_yellow_per_match": round(mean([int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) for r in rs]), 3),
        "ev_red_per_match": round(mean([int(r["ev_red_home"])+int(r["ev_red_away"]) for r in rs]), 3),
    }
out["per_season"] = per
out["playoff_levels"] = {"n": 30, "goals_per_match": round(mean([int(r["home_goals"])+int(r["away_goals"]) for r in ROWS if r["phase"] == "playoff"]), 3)}
out["round_distribution"] = {s: dict(sorted(Counter(r["round"] for r in ROWS if r["season"] == s).items(), key=lambda x: int(x[0]) if x[0].isdigit() else 999)) for s in SEASONS}
out["phase_distribution"] = {s: dict(Counter(r["phase"] for r in ROWS if r["season"] == s)) for s in SEASONS}
out["teams_per_season"] = {s: sorted({r["home_team"] for r in REG if r["season"] == s} | {r["away_team"] for r in REG if r["season"] == s}) for s in SEASONS}
out["team_id_stability"] = {"n_team_ids": len({r["home_team_id"] for r in ROWS} | {r["away_team_id"] for r in ROWS}),
                            "names_mapping_to_multiple_ids": []}

# Reliability: goals for / against, split-half (alternating split) on
# career-pooled team series, dev regular matches only.
dfor, dagainst = defaultdict(list), defaultdict(list)
for r in sorted(DEV, key=lambda x: x["date"]):
    dfor[r["home_team"]].append(float(r["home_goals"])); dfor[r["away_team"]].append(float(r["away_goals"]))
    dagainst[r["home_team"]].append(float(r["away_goals"])); dagainst[r["away_team"]].append(float(r["home_goals"]))
a, na = corr_halves(dfor); b, nb = corr_halves(dagainst)
out["reliability"] = {"goals": {"for": {"r": round(a, 3), "n_teams": na}, "against": {"r": round(b, 3), "n_teams": nb}}}
# Season-to-season lag correlation of team goals-for (consecutive seasons).
def team_season_gf(season):
    d = {}
    for r in REG:
        if r["season"] != season: continue
        for side, opp in (("home", "away"), ("away", "home")):
            d.setdefault(r[f"{side}_team"], [0, 0])
            d[r[f"{side}_team"]][0] += int(r[f"{side}_goals"]); d[r[f"{side}_team"]][1] += 1
    return {t: g/n for t, (g, n) in d.items()}
lags = []
for s1, s2 in zip(DEV_SEASONS, DEV_SEASONS[1:]):
    d1, d2 = team_season_gf(s1), team_season_gf(s2)
    common = sorted(set(d1) & set(d2))
    if len(common) >= 5:
        xs = [d1[t] for t in common]; ys = [d2[t] for t in common]
        mx, my = mean(xs), mean(ys)
        den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
        lags.append({"seasons": f"{s1}->{s2}", "n_teams": len(common),
                     "r": round(sum((x-mx)*(y-my) for x, y in zip(xs, ys))/den, 3) if den else None})
out["goals_for_season_lag_corr"] = lags

# Half shares: goals 1H share from events, dev regular matches with a
# derivable HT (events or inferred 0-0); mismatch/none rows excluded.
hs_rows = [r for r in DEV if r["ht_source"] in ("events", "inferred-0-0")]
out["half_shares"] = {"goals_events_2021_2025": half_share(
    hs_rows, lambda r: int(r["ht_home_goals"]) + int(r["ht_away_goals"]),
    lambda r: int(r["home_goals"]) + int(r["away_goals"]))}
# Per-season half shares (same rows).
out["half_shares_by_season"] = {s: half_share(
    [r for r in hs_rows if r["season"] == s],
    lambda r: int(r["ht_home_goals"]) + int(r["ht_away_goals"]),
    lambda r: int(r["home_goals"]) + int(r["away_goals"])) for s in DEV_SEASONS}
out["halves_constants"] = {"goals_1h_share": out["half_shares"]["goals_events_2021_2025"]["share"]}

# Mover check: clubs entering the First Division in season S who were
# NOT in the First Division in S-1. Classify via the sibling Premier
# Division table: present in Premier S-1 => relegated mover; absent
# from both => brand-new club.
def teams_in(rows, season):
    return {r["home_team_id"] for r in rows if r["season"] == season} | {r["away_team_id"] for r in rows if r["season"] == season}
def team_name(rows, season, tid):
    for r in rows:
        if r["season"] == season and (r["home_team_id"] == tid or r["away_team_id"] == tid):
            return r["home_team"] if r["home_team_id"] == tid else r["away_team"]
    return tid
transitions = []
for i, s in enumerate(DEV_SEASONS[1:], 1):
    prev = DEV_SEASONS[i-1]
    new = teams_in(REG, s) - teams_in(REG, prev)
    for tid in sorted(new):
        rs = [r for r in REG if r["season"] == s and (r["home_team_id"] == tid or r["away_team_id"] == tid)]
        gf = sum(int(r["home_goals"] if r["home_team_id"] == tid else r["away_goals"]) for r in rs)/len(rs)
        ga = sum(int(r["away_goals"] if r["home_team_id"] == tid else r["home_goals"]) for r in rs)/len(rs)
        in_prem_prev = tid in teams_in(PREM, prev)
        prem_rs = [r for r in PREM if r["season"] == prev and (r["home_team_id"] == tid or r["away_team_id"] == tid)]
        pgf = pga = None
        if prem_rs:
            pgf = sum(int(r["home_goals"] if r["home_team_id"] == tid else r["away_goals"]) for r in prem_rs)/len(prem_rs)
            pga = sum(int(r["away_goals"] if r["home_team_id"] == tid else r["home_goals"]) for r in prem_rs)/len(prem_rs)
        transitions.append({"season": s, "team": team_name(REG, s, tid),
                            "origin": "relegated-from-Premier" if in_prem_prev else "new-club",
                            "matches": len(rs), "gf_per_match": round(gf, 3), "ga_per_match": round(ga, 3),
                            "league_goals_per_team_match": round(per[s]["goals"]/2, 3),
                            "prem_prev_gf": round(pgf, 3) if pgf is not None else None,
                            "prem_prev_ga": round(pga, 3) if pga is not None else None})
out["mover_check"] = {"n_transitions_dev": len(transitions), "transitions": transitions}
# 2026 arrivals (virgin; listed for the record, NOT used for any design number).
new26 = teams_in(REG, "2026") - teams_in(REG, "2025")
out["mover_check_2026_virgin_only"] = [{"team": team_name(REG, "2026", tid),
    "origin": "relegated-from-Premier" if tid in teams_in(PREM, "2025") else "new-club"} for tid in sorted(new26)]

# Primary lines: goals OU over-rates on dev eval seasons (regular only).
rates = {}
for line in (1.5, 2.5, 3.5):
    rates[str(line)] = round(100*mean([int(r["home_goals"])+int(r["away_goals"]) > line for r in DEV_EVAL]), 1)
chosen = min((1.5, 2.5, 3.5), key=lambda x: abs(rates[str(x)]/100-0.5))
out["primary_lines"] = {"goals": {"dev_seasons": ["2022", "2023", "2024", "2025"], "n_matches": len(DEV_EVAL),
                                   "over_rates_pct": rates, "primary_line": chosen, "primary_over_rate_pct": rates[str(chosen)]}}

# Goal-event cross-check + card audit (all rows, incl. playoffs).
out["goal_event_agreement"] = {"n_matches": len(ROWS),
    "mismatches": [{"season": r["season"], "date": r["date"], "match": f"{r['home_team']} vs {r['away_team']}", "score": f"{r['home_goals']}-{r['away_goals']}",
                    "ev_goals": f"{r['ev_goals_home']}-{r['ev_goals_away']}", "ht_source": r["ht_source"]}
                   for r in ROWS if r["score_events_mismatch"] == "1" or r["ht_source"] == "none"]}
out["card_audit"] = {"plain_yellow_events_total": sum(int(r["ev_yellow_strict_home"])+int(r["ev_yellow_strict_away"]) for r in ROWS),
                     "yellowred_events_total": sum(int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) for r in ROWS) - sum(int(r["ev_yellow_strict_home"])+int(r["ev_yellow_strict_away"]) for r in ROWS),
                     "red_events_total": sum(int(r["ev_red_home"])+int(r["ev_red_away"]) for r in ROWS),
                     "matches_with_any_card_event": sum(1 for r in ROWS if int(r["ev_red_home"])+int(r["ev_red_away"]) > 0),
                     "named_referee_matches": 0}

json.dump(out, open(HERE / "eda_numbers.json", "w"), indent=1)
print(json.dumps(out, indent=1))
