"""Compute inventory_summary.json + eda_summary.json for IR-AzadeganLeague
from the built CSV (league/IR-AzadeganLeague/data/ir_azadegan_matches.csv).
Second-path check: headline levels must match the payload-level EDA run
(/tmp/eda_azadegan.py) up to the two excluded never-played rows (0-0,
so goal totals are unchanged; played n per season differs by that row).
"""
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "ir_azadegan_matches.csv"
TEAM = HERE.parent / "data" / "team_matches.csv"

rows = list(csv.DictReader(open(DATA)))
for r in rows:
    r["home_goals"] = int(r["home_goals"])
    r["away_goals"] = int(r["away_goals"])
    r["ht_home_goals"] = float(r["ht_home_goals"]) if r["ht_home_goals"] not in ("", "nan") else None
    r["ht_away_goals"] = float(r["ht_away_goals"]) if r["ht_away_goals"] not in ("", "nan") else None
rows.sort(key=lambda x: (x["date"], int(x["match_id"])))
seasons = sorted(set(r["season"] for r in rows))

# ---------------- inventory ----------------
inv = {
    "league": "IR-AzadeganLeague",
    "fotmob_id": 9372,
    "index_rows": 1564,
    "played_matches": len(rows),
    "excluded_unplayed": ["3743953", "5098083"],
    "excluded_unplayed_reason": "status finished False, started False, placeholder 0-0; never played",
    "seasons": {},
    "coverage_played": {
        "stats_nonnull": sum(1 for r in rows if r["has_stats_all"] == "True"),
        "shotmap_shots_gt0": sum(1 for r in rows if r["has_shotmap"] == "True"),
        "lineup_nonnull": sum(1 for r in rows if r["has_lineup"] == "True"),
        "referee_text": sum(1 for r in rows if r["referee"]),
        "events_nonempty": sum(1 for r in rows if r["has_events"] == "True"),
        "period_splits": 0,
        "score_events_mismatch": [r["match_id"] for r in rows if r["score_events_mismatch"] == "True"],
    },
    "card_events": {"Yellow": 0, "Red": 122, "YellowRed": 11,
                    "matches_with_any_card_event": 117},
    "team_renames_same_id": {
        "1082763": ["Arman Gohar Sirjan", "Shahr Raz"],
        "1528916": ["Mes Sungun", "Kara Gostar"],
        "1602400": ["Shenavarsazi Qeshm", "Qeshm Island"],
    },
    "distinct_team_ids": len(set([r["home_team_id"] for r in rows] + [r["away_team_id"] for r in rows])),
    "format": "double round-robin, 34 rounds; 18 teams (17 in 2022/2023, 16 in 2026/2027 partial)",
}
for s in seasons:
    m = [r for r in rows if r["season"] == s]
    teams = set([r["home_team_id"] for r in m] + [r["away_team_id"] for r in m])
    inv["seasons"][s] = {"played": len(m), "teams": len(teams),
                         "rounds": sorted(set(r["round"] for r in m), key=int),
                         "date_range": [min(r["date"] for r in m), max(r["date"] for r in m)]}

# ---------------- levels ----------------
def levels(ms):
    n = len(ms)
    g = sum(r["home_goals"] + r["away_goals"] for r in ms)
    return {
        "n": n,
        "goals_per_match": round(g / n, 3),
        "home_goals_per_match": round(sum(r["home_goals"] for r in ms) / n, 3),
        "away_goals_per_match": round(sum(r["away_goals"] for r in ms) / n, 3),
        "home_win_pct": round(sum(1 for r in ms if r["home_goals"] > r["away_goals"]) / n, 3),
        "draw_pct": round(sum(1 for r in ms if r["home_goals"] == r["away_goals"]) / n, 3),
        "away_win_pct": round(sum(1 for r in ms if r["home_goals"] < r["away_goals"]) / n, 3),
        "btts_pct": round(sum(1 for r in ms if r["home_goals"] > 0 and r["away_goals"] > 0) / n, 3),
        "over1_5_pct": round(sum(1 for r in ms if r["home_goals"] + r["away_goals"] > 1.5) / n, 3),
        "over2_5_pct": round(sum(1 for r in ms if r["home_goals"] + r["away_goals"] > 2.5) / n, 3),
        "over3_5_pct": round(sum(1 for r in ms if r["home_goals"] + r["away_goals"] > 3.5) / n, 3),
    }

season_levels = {s: levels([r for r in rows if r["season"] == s]) for s in seasons}
dev = [r for r in rows if r["season"] in ("2021/2022", "2022/2023", "2023/2024", "2024/2025")]
virgin = [r for r in rows if r["season"] == "2025/2026"]

# ---------------- reliability ----------------
def corr(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den else float("nan")

team_games = defaultdict(list)
for r in rows:
    team_games[(r["home_team_id"], r["season"])].append((r["date"], r["home_goals"], r["away_goals"]))
    team_games[(r["away_team_id"], r["season"])].append((r["date"], r["away_goals"], r["home_goals"]))

def trait_split(games_by_team, value_fn, min_matches=8):
    """Chronological split-half r pooled across team-seasons."""
    xs, ys = [], []
    per_season = defaultdict(lambda: ([], []))
    for (team, season), games in games_by_team.items():
        games = sorted(games)
        if len(games) < min_matches:
            continue
        h = len(games) // 2
        v1 = statistics.mean([value_fn(g) for g in games[:h]])
        v2 = statistics.mean([value_fn(g) for g in games[h:]])
        xs.append(v1); ys.append(v2)
        per_season[season][0].append(v1); per_season[season][1].append(v2)
    out = {"n_team_seasons": len(xs), "r_chronological": round(corr(xs, ys), 3),
           "per_season": {s: {"n": len(a), "r": round(corr(a, b), 3)} for s, (a, b) in sorted(per_season.items())}}
    return out

gf = trait_split(team_games, lambda g: g[1])
ga = trait_split(team_games, lambda g: g[2])

rng = random.Random(20261110)
r_gf, r_ga = [], []
for _ in range(60):
    fx, fy, ax, ay = [], [], [], []
    for (team, season), games in team_games.items():
        if len(games) < 8:
            continue
        idx = list(range(len(games))); rng.shuffle(idx)
        h = len(idx) // 2
        g1 = [games[i] for i in idx[:h]]; g2 = [games[i] for i in idx[h:]]
        fx.append(statistics.mean([g[1] for g in g1])); fy.append(statistics.mean([g[1] for g in g2]))
        ax.append(statistics.mean([g[2] for g in g1])); ay.append(statistics.mean([g[2] for g in g2]))
    r_gf.append(corr(fx, fy)); r_ga.append(corr(ax, ay))
gf["r_random_mean_60"] = round(statistics.mean(r_gf), 3)
gf["r_random_range_60"] = [round(min(r_gf), 3), round(max(r_gf), 3)]
ga["r_random_mean_60"] = round(statistics.mean(r_ga), 3)
ga["r_random_range_60"] = [round(min(r_ga), 3), round(max(r_ga), 3)]

# reds trait (team-seasons, chronological split-half on reds per match)
team_reds = defaultdict(list)
for r in rows:
    team_reds[(r["home_team_id"], r["season"])].append((r["date"], int(r["red_home"])))
    team_reds[(r["away_team_id"], r["season"])].append((r["date"], int(r["red_away"])))
reds = trait_split(team_reds, lambda g: g[1])

# ---------------- halves ----------------
ht_rows = [r for r in rows if r["ht_home_goals"] is not None]
h1 = sum(int(r["ht_home_goals"]) + int(r["ht_away_goals"]) for r in ht_rows)
ft = sum(r["home_goals"] + r["away_goals"] for r in ht_rows)
p = h1 / ft
shares = []
for r in ht_rows:
    n = r["home_goals"] + r["away_goals"]
    if n > 0:
        shares.append(((r["ht_home_goals"] + r["ht_away_goals"]) / n, n))
obs_var = statistics.variance([s for s, _ in shares])
noise = statistics.mean([p * (1 - p) / n for _, n in shares])
# team 1H-share split-half (team goals for)
tg = defaultdict(list)
for r in ht_rows:
    tg[(r["home_team_id"], r["season"])].append((r["date"], r["ht_home_goals"], r["home_goals"]))
    tg[(r["away_team_id"], r["season"])].append((r["date"], r["ht_away_goals"], r["away_goals"]))
sx, sy = [], []
for (t, s), games in tg.items():
    games = sorted(games)
    tot = sum(g[2] for g in games)
    if tot < 10 or len(games) < 8:
        continue
    h = len(games) // 2
    g1, g2 = games[:h], games[h:]
    n1 = sum(g[2] for g in g1); n2 = sum(g[2] for g in g2)
    if n1 >= 5 and n2 >= 5:
        sx.append(sum(g[1] for g in g1) / n1); sy.append(sum(g[1] for g in g2) / n2)
halves = {
    "goals": {
        "matches_with_ht": len(ht_rows),
        "share_1h": round(p, 4),
        "goals_1h": h1, "goals_ft": ft,
        "per_season": {s: round(sum(int(r["ht_home_goals"]) + int(r["ht_away_goals"]) for r in ht_rows if r["season"] == s)
                                / sum(r["home_goals"] + r["away_goals"] for r in ht_rows if r["season"] == s), 4)
                       for s in seasons},
        "observed_variance": round(obs_var, 5),
        "noise_floor_per_match": round(noise, 5),
        "true_variance": round(obs_var - noise, 5),
        "team_split_half_r": round(corr(sx, sy), 3),
        "team_split_half_n": len(sx),
    }
}

# ---------------- entrants ----------------
teams_by_season = {s: set() for s in seasons}
for r in rows:
    teams_by_season[r["season"]].add(r["home_team_id"]); teams_by_season[r["season"]].add(r["away_team_id"])
name_of = {}
for r in rows:
    # Name the club as it played in THAT season (three ids renamed mid-corpus).
    name_of[(r["home_team_id"], r["season"])] = r["home_team"]
    name_of[(r["away_team_id"], r["season"])] = r["away_team"]
entrants = {}
dev_gf_d, dev_ga_d = [], []
dev_em = 0
for i, s in enumerate(seasons):
    if i == 0:
        continue
    prev = seasons[i - 1]
    entr = sorted(teams_by_season[s] - teams_by_season[prev])
    lg = [r for r in rows if r["season"] == s]
    mu = sum(r["home_goals"] + r["away_goals"] for r in lg) / (2 * len(lg))
    gf_d, ga_d, n_em = [], [], 0
    for t in entr:
        gm = [r for r in lg if r["home_team_id"] == t or r["away_team_id"] == t]
        n_em += len(gm)
        gf_d.append(sum(r["home_goals"] if r["home_team_id"] == t else r["away_goals"] for r in gm) / len(gm) - mu)
        ga_d.append(sum(r["away_goals"] if r["home_team_id"] == t else r["home_goals"] for r in gm) / len(gm) - mu)
    entrants[f"{prev} -> {s}"] = {
        "entrants": [name_of[(t, s)] for t in entr], "n_teams": len(entr), "team_matches": n_em,
        "gf_gap": round(statistics.mean(gf_d), 3) if gf_d else None,
        "ga_gap": round(statistics.mean(ga_d), 3) if ga_d else None,
    }
    if s in ("2022/2023", "2023/2024", "2024/2025"):
        dev_gf_d += gf_d; dev_ga_d += ga_d; dev_em += n_em
entrants["pooled_dev_transitions"] = {
    "transitions": ["2022/2023", "2023/2024", "2024/2025"],
    "n_teams": len(dev_gf_d), "team_matches": dev_em,
    "gf_gap": round(statistics.mean(dev_gf_d), 3), "ga_gap": round(statistics.mean(dev_ga_d), 3),
}

eda = {
    "season_levels": season_levels,
    "dev_levels": levels(dev),
    "virgin_levels": levels(virgin),
    "reliability": {"goals_for": gf, "goals_against": ga, "reds": reds},
    "halves": halves,
    "entrants": entrants,
}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=2, ensure_ascii=False) + "\n")
(HERE / "eda_summary.json").write_text(json.dumps(eda, indent=2, ensure_ascii=False) + "\n")
print(json.dumps({"season_levels": season_levels, "halves_share": p, "true_var": round(obs_var - noise, 5),
                  "gf_r": gf["r_chronological"], "ga_r": ga["r_chronological"],
                  "dev_entrants": entrants["pooled_dev_transitions"]}, indent=2))
