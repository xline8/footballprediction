"""Reproducible Thai League 2 inventory and EDA; performs no fitting."""
import csv
import json
import math
import random
import statistics as st
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data" / "th2_matches.csv").open()))
PARENT = list(csv.DictReader(
    (Path.home() / "workspace" / "footballprediction" / "league" /
     "TH-ThaiLeague" / "data" / "th_matches.csv").open()))
random.seed(42)
DEV = "2024/2025"          # only pre-virgin complete season
VIRGIN = "2025/2026"
REG = [r for r in ROWS if r["phase"] == "regular"]


def avg(v):
    return round(st.mean(v), 3) if v else None


def corr(xs, ys):
    if len(xs) < 5:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return round(sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den, 3) if den else None


def levels(rows):
    g = [int(r["home_goals"]) + int(r["away_goals"]) for r in rows]
    y = [int(r["yellow_home"]) + int(r["yellow_away"]) for r in rows]
    return {
        "matches": len(rows),
        "teams": len({r[k] for r in rows for k in ("home_team_id", "away_team_id")}),
        "date_range": [min(r["date"] for r in rows), max(r["date"] for r in rows)] if rows else None,
        "goals_per_match": avg(g),
        "home_win_rate": round(sum(int(r["home_goals"]) > int(r["away_goals"]) for r in rows) / len(rows), 3) if rows else None,
        "draw_rate": round(sum(int(r["home_goals"]) == int(r["away_goals"]) for r in rows) / len(rows), 3) if rows else None,
        "ou2_5_over_rate": round(sum(v > 2.5 for v in g) / len(g), 3) if g else None,
        "home_goal_advantage": avg([int(r["home_goals"]) - int(r["away_goals"]) for r in rows]),
        "event_yellows_per_match": avg(y),
        "cards_over_rates": {str(l): round(sum(v > l for v in y) / len(y), 3) for l in (3.5, 4.5, 5.5)} if y else None,
        "coverage": {
            "stats_all_pct": round(100 * sum(r["has_stats_all"] == "1" for r in rows) / len(rows), 1) if rows else None,
            "period_splits_pct": round(100 * sum(r["has_period_splits_content"] == "1" for r in rows) / len(rows), 1) if rows else None,
            "shotmap_pct": round(100 * sum(r["has_shotmap"] == "1" for r in rows) / len(rows), 1) if rows else None,
            "events_pct": round(100 * sum(r["cards_source"] == "events" for r in rows) / len(rows), 1) if rows else None,
            "referee_pct": round(100 * sum(bool(r["referee"]) for r in rows) / len(rows), 1) if rows else None,
        },
    }


per_season = {}
for s in sorted({r["season"] for r in ROWS}):
    all_s = [r for r in ROWS if r["season"] == s]
    reg_s = [r for r in all_s if r["phase"] == "regular"]
    per_season[s] = {"all": levels(all_s), "regular": levels(reg_s),
                     "playoff_matches": len(all_s) - len(reg_s)}

# --- cards artefact check: stats feed vs event feed, per season (all rows)
artefact = {}
for s in sorted({r["season"] for r in ROWS}):
    rs = [r for r in ROWS if r["season"] == s]
    stats_vals = [r for r in rs if r["yellow_cards_home"] not in (None, "")]
    ev_mean = avg([int(r["ev_yellow_home"]) + int(r["ev_yellow_away"]) for r in rs])
    artefact[s] = {"stats_rows": len(stats_vals), "event_yellow_mean": ev_mean,
                   "plain_yellow_events": sum(int(r["ev_yellow_direct_home"]) + int(r["ev_yellow_direct_away"]) for r in rs),
                   "yellowred_events": sum(int(r["ev_yellowred_home"]) + int(r["ev_yellowred_away"]) for r in rs)}

# --- reliabilities: random split-half within the DEV season (regular only),
# per team; traits: goals for/against, event yellows for/against.
dev_rows = [r for r in REG if r["season"] == DEV]


def split_half(get_values):
    per_team = defaultdict(list)
    for r in dev_rows:
        for side, other in (("home", "away"), ("away", "home")):
            v = get_values(r, side, other)
            if v is not None:
                per_team[r[f"{side}_team_id"]].append(v)
    xs, ys = [], []
    for team, vals in per_team.items():
        if len(vals) < 10:
            continue
        vals = vals[:]
        random.shuffle(vals)
        h = len(vals) // 2
        xs.append(st.mean(vals[:h])); ys.append(st.mean(vals[h:2 * h]))
    return {"r": corr(xs, ys), "teams": len(xs)}


reliability = {
    "goals_for": split_half(lambda r, s, o: int(r[f"{s}_goals"])),
    "goals_against": split_half(lambda r, s, o: int(r[f"{o}_goals"])),
    "yellows_for": split_half(lambda r, s, o: int(r[f"ev_yellow_{s}"])),
    "yellows_against": split_half(lambda r, s, o: int(r[f"ev_yellow_{o}"])),
}

# --- halves: frozen-constant test on DEV regular rows.
def halves(rows, total_fn, first_fn):
    shares, tots = [], []
    for r in rows:
        t = total_fn(r)
        if t and t > 0:
            shares.append(first_fn(r) / t); tots.append(t)
    if not shares:
        return None
    share = sum(first_fn(r) for r in rows if total_fn(r)) / sum(total_fn(r) for r in rows if total_fn(r))
    obs_var = st.variance(shares) if len(shares) > 1 else 0.0
    noise = st.mean([share * (1 - share) / t for t in tots])
    return {"n_matches_with_total": len(shares), "share_1h": round(share, 4),
            "obs_var": round(obs_var, 4), "noise_var": round(noise, 4),
            "true_var": round(obs_var - noise, 4)}

halves_out = {
    "goals": halves(dev_rows, lambda r: int(r["home_goals"]) + int(r["away_goals"]),
                    lambda r: int(r["ht_home_goals"]) + int(r["ht_away_goals"])),
    "yellow_cards": halves(dev_rows, lambda r: int(r["ev_yellow_home"]) + int(r["ev_yellow_away"]),
                           lambda r: int(r["ev_yellow_1h_home"]) + int(r["ev_yellow_1h_away"])),
}

# --- X2 movers vs parent Thai League 1 corpus.
def season_teams(rows, season):
    return {r[k] for r in rows if r["season"] == season for k in ("home_team_id", "away_team_id")}

def team_gf_ga(rows, season, team):
    gf = ga = n = 0
    for r in rows:
        if r["season"] != season:
            continue
        if r["home_team_id"] == team:
            gf += int(r["home_goals"]); ga += int(r["away_goals"]); n += 1
        elif r["away_team_id"] == team:
            gf += int(r["away_goals"]); ga += int(r["home_goals"]); n += 1
    return (gf / n, ga / n, n) if n else (None, None, 0)

def league_means(rows, season):
    rs = [r for r in rows if r["season"] == season]
    tot = sum(int(r["home_goals"]) + int(r["away_goals"]) for r in rs)
    return tot / (2 * len(rs))

movers = []
# entrants to T2 in DEV whose previous season was in T1 (relegated)
for team in sorted(season_teams(REG, DEV) - season_teams(PARENT, DEV)):
    pass
t1_prev = season_teams(PARENT, "2023/2024")
t2_dev = season_teams(REG, DEV)
for team in sorted(t2_dev & t1_prev, key=int):
    gf, ga, n = team_gf_ga(REG, DEV, team)
    lm = league_means(REG, DEV)
    name = next(r["home_team"] for r in REG if r["home_team_id"] == team) if any(r["home_team_id"] == team for r in REG) else team
    movers.append({"team_id": team, "team": name, "kind": "relegated_from_T1",
                   "season": DEV, "n": n, "gf_gap": round(gf - lm, 3), "ga_gap": round(ga - lm, 3)})
# entrants to T2 in VIRGIN: relegated from T1 2024/2025, or unseen in either
# 2024/2025 corpus (promoted from T3, unobserved tier).
t1_virgin_prev = season_teams(PARENT, DEV)
t2_virgin = season_teams(REG, VIRGIN)
lm_v = league_means(REG, VIRGIN)
for team in sorted(t2_virgin - t2_dev, key=int):
    gf, ga, n = team_gf_ga(REG, VIRGIN, team)
    kind = "relegated_from_T1" if team in t1_virgin_prev else "promoted_from_T3_unobserved"
    name = next((r["home_team"] for r in REG if r["home_team_id"] == team), team)
    movers.append({"team_id": team, "team": name, "kind": kind, "season": VIRGIN,
                   "n": n, "gf_gap": round(gf - lm_v, 3), "ga_gap": round(ga - lm_v, 3)})

team_id_names = {}
for r in ROWS:
    for side in ("home", "away"):
        team_id_names.setdefault(r[f"{side}_team_id"], set()).add(r[f"{side}_team"])

out = {
    "league": "TH-ThaiLeague2", "league_id": "9498", "n": len(ROWS),
    "regular_n": len(REG), "per_season": per_season,
    "cards_artefact": artefact, "reliability_dev_season_split_half": reliability,
    "halves_dev": halves_out, "x2_movers": movers,
    "team_ids": len(team_id_names),
    "team_id_multi_name": {k: sorted(v) for k, v in team_id_names.items() if len(v) > 1},
    "dev_scored_plan": {"warmup_matches": 90,
                        "dev_regular_n": len(dev_rows),
                        "dev_scored_n": len(dev_rows) - 90,
                        "virgin_regular_n": len([r for r in REG if r["season"] == VIRGIN])},
}
(HERE / "eda_numbers.json").write_text(json.dumps(out, indent=2) + "\n")
(HERE / "inventory_summary.json").write_text(json.dumps(
    {"per_season": per_season, "cards_artefact": artefact,
     "team_ids": out["team_ids"], "team_id_multi_name": out["team_id_multi_name"]},
    indent=2) + "\n")
print(json.dumps({k: out[k] for k in ("n", "regular_n", "reliability_dev_season_split_half",
                                       "halves_dev", "dev_scored_plan")}, indent=2))
print("movers:", json.dumps(movers, indent=1))
print("artefact:", json.dumps(artefact, indent=1))
