"""EDA computations for AE-ProLeague — all numbers in EDA.md come from here."""
import csv, json, math, statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = [r for r in csv.DictReader((HERE.parent / "data" / "ae_matches.csv").open())]
def f(v):
    return float(v) if v not in (None, "") else None
def total(r, key):
    a, b = f(r[f"{key}_home"]), f(r[f"{key}_away"])
    return None if a is None or b is None else a + b

SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
out = {}
levels = {}
for s in SEASONS:
    rs = [r for r in ROWS if r["season"] == s]
    lv = {"n": len(rs), "teams": len({r["home_team_id"] for r in rs} | {r["away_team_id"] for r in rs}),
          "goals": statistics.mean(int(r["home_goals"]) + int(r["away_goals"]) for r in rs),
          "home_goals": statistics.mean(int(r["home_goals"]) for r in rs),
          "away_goals": statistics.mean(int(r["away_goals"]) for r in rs),
          "home_win": statistics.mean(int(r["home_goals"]) > int(r["away_goals"]) for r in rs),
          "draw": statistics.mean(int(r["home_goals"]) == int(r["away_goals"]) for r in rs),
          "ou25": statistics.mean(int(r["home_goals"]) + int(r["away_goals"]) > 2.5 for r in rs)}
    for key, name in (("ShotsOnTarget", "sot"), ("corners", "corners"), ("total_shots", "shots"), ("yellow_cards", "cards_stats"), ("ev_yellow", "cards_ev")):
        vals = [total(r, key) for r in rs]
        vals = [v for v in vals if v is not None]
        lv[name] = statistics.mean(vals) if vals else None
        lv[name + "_n"] = len(vals)
    levels[s] = lv
out["levels"] = levels

DEV = ["2022/2023", "2023/2024", "2024/2025"]  # scored dev folds (seed 2021/2022)
dev_rows = [r for r in ROWS if r["season"] in DEV and r["awarded"] == "0"]
def over_rate(rows, key, line):
    vals = [total(r, key) for r in rows]
    vals = [v for v in vals if v is not None]
    return {"n": len(vals), "rate": statistics.mean(v > line for v in vals)}
out["dev_over_rates"] = {
    "sot": {str(l): over_rate(dev_rows, "ShotsOnTarget", l) for l in (7.5, 8.5, 9.5)},
    "corners": {str(l): over_rate(dev_rows, "corners", l) for l in (8.5, 9.5, 10.5)},
    "cards": {str(l): over_rate(dev_rows, "yellow_cards", l) for l in (3.5, 4.5, 5.5)},
    "shots": {str(l): over_rate(dev_rows, "total_shots", l) for l in (24.5, 25.5, 26.5)},
    "goals_ou25": {"n": len(dev_rows), "rate": statistics.mean(int(r["home_goals"]) + int(r["away_goals"]) > 2.5 for r in dev_rows)},
}

# split-half reliability: per team, split its matches (chronological) into odd/even halves,
# trait = ratio of sums (for) or mean per match; correlate across teams. Career-pooled, all complete seasons.
COMP = SEASONS[:5]
comp_rows = [r for r in ROWS if r["season"] in COMP and r["awarded"] == "0"]
def team_series(rows):
    series = defaultdict(list)
    for r in sorted(rows, key=lambda r: (r["date"], int(r["match_id"]))):
        series[r["home_team_id"]].append(("home", r))
        series[r["away_team_id"]].append(("away", r))
    return series
def pearson(xs, ys):
    n = len(xs)
    mx, my = statistics.mean(xs), statistics.mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den if den > 0 else None
def reliability(getter, min_matches=20):
    xs, ys, teams = [], [], 0
    for tid, lst in team_series(comp_rows).items():
        if len(lst) < min_matches:
            continue
        h1 = [getter(side, r) for i, (side, r) in enumerate(lst) if i % 2 == 0]
        h2 = [getter(side, r) for i, (side, r) in enumerate(lst) if i % 2 == 1]
        h1 = [v for v in h1 if v is not None]; h2 = [v for v in h2 if v is not None]
        if len(h1) < 8 or len(h2) < 8:
            continue
        xs.append(statistics.mean(h1)); ys.append(statistics.mean(h2)); teams += 1
    return {"r": pearson(xs, ys), "teams": teams}
def per_match(key, suffix):
    def g(side, r):
        return f(r[f"{key}_{side}"])
    return g
rel = {
    "goals_for": reliability(lambda s, r: int(r[f"{s}_goals"])),
    "goals_against": reliability(lambda s, r: int(r[f"{'away' if s=='home' else 'home'}_goals"])),
    "sot_for": reliability(per_match("ShotsOnTarget", "for")),
    "sot_against": reliability(lambda s, r: f(r[f"ShotsOnTarget_{'away' if s=='home' else 'home'}"])),
    "corners_for": reliability(per_match("corners", "for")),
    "corners_against": reliability(lambda s, r: f(r[f"corners_{'away' if s=='home' else 'home'}"])),
    "shots_for": reliability(per_match("total_shots", "for")),
    "cards_for_stats": reliability(per_match("yellow_cards", "for")),
    "boxtouches_for": reliability(per_match("touches_opp_box", "for")),
    "boxtouches_against": reliability(lambda s, r: f(r[f"touches_opp_box_{'away' if s=='home' else 'home'}"])),
    "bigchance_for": reliability(per_match("big_chance", "for")),
    "possession": reliability(per_match("BallPossesion", "for")),
    "on_target_rate": reliability(lambda s, r: (f(r[f"ShotsOnTarget_{s}"]) / f(r[f"total_shots_{s}"])) if f(r[f"total_shots_{s}"]) else None),
}
# per-match correlation box touches vs corners
bt, co = [], []
for r in comp_rows:
    b, c = total(r, "touches_opp_box"), total(r, "corners")
    if b is not None and c is not None:
        bt.append(b); co.append(c)
rel["corr_boxtouch_corners"] = {"r": pearson(bt, co), "n": len(bt)}
bp, co2 = [], []
for r in comp_rows:
    b, c = f(r["BallPossesion_home"]), total(r, "corners")
    if b is not None and c is not None:
        bp.append(b); co2.append(c)
out["reliability"] = rel

# halves shares: period splits era (FirstHalf present) for count stats; events for goals & cards-ev (era-limited)
def share(rows, key):
    num = den = 0.0; n = 0; shares = []
    for r in rows:
        a1, b1 = f(r[f"{key}_1h_home"]), f(r[f"{key}_1h_away"])
        a, b = f(r[f"{key}_home"]), f(r[f"{key}_away"])
        if a1 is None or b1 is None or a is None or b is None or (a + b) == 0:
            continue
        num += a1 + b1; den += a + b; n += 1; shares.append((a1 + b1) / (a + b))
    # variance decomposition: observed var of per-match share vs binomial noise expectation
    if shares:
        m = statistics.mean(shares)
        obs = statistics.variance(shares)
        noise = statistics.mean([m * (1 - m) / max(d, 1) for d in [den / n]]) if n else None
        true_var = obs - (m * (1 - m) / (den / n))
    else:
        m = obs = true_var = None
    return {"share": num / den if den else None, "n": n, "per_match_mean_share": m if shares else None,
            "obs_var": obs if shares else None, "true_var_est": true_var if shares else None}
split_rows = [r for r in ROWS if r["season"] in ("2023/2024", "2024/2025", "2025/2026") and r["awarded"] == "0"]
halves = {}
for key in ("ShotsOnTarget", "corners", "total_shots", "yellow_cards"):
    halves[key] = share(split_rows, key)
# goals 1H share from events (ht_source reliable, all complete seasons)
gn = gd = 0; gshares = []
for r in comp_rows:
    if r["ht_source"] != "events":
        continue
    ft = int(r["home_goals"]) + int(r["away_goals"]); ht = int(r["ht_home_goals"]) + int(r["ht_away_goals"])
    gn += ht; gd += ft
    if ft > 0:
        gshares.append(ht / ft)
halves["goals_events"] = {"share": gn / gd if gd else None, "n": len(gshares),
                          "per_match_mean_share": statistics.mean(gshares) if gshares else None,
                          "obs_var": statistics.variance(gshares) if gshares else None}
out["halves"] = halves

# referee: coverage + strictness split-half (refs with >=16 matches, stats yellows)
ref_matches = defaultdict(list)
for r in comp_rows:
    if r["referee"]:
        ref_matches[r["referee"]].append(total(r, "yellow_cards"))
out["referee_coverage"] = {s: {"named": sum(1 for r in ROWS if r["season"] == s and r["referee"]),
                               "n": len([r for r in ROWS if r["season"] == s])} for s in SEASONS}
xs, ys, nref = [], [], 0
for ref, vals in ref_matches.items():
    vals = [v for v in vals if v is not None]
    if len(vals) < 16:
        continue
    xs.append(statistics.mean(vals[::2])); ys.append(statistics.mean(vals[1::2])); nref += 1
out["referee_reliability"] = {"r": pearson(xs, ys) if nref >= 5 else None, "refs_ge16": nref,
                              "refs_total": len(ref_matches),
                              "max_ref_matches": max((len(v) for v in ref_matches.values()), default=0)}

# cards artefact: stats vs events per season
art = {}
for s in SEASONS:
    rs = [r for r in ROWS if r["season"] == s]
    sv = [total(r, "yellow_cards") for r in rs]; evv = [total(r, "ev_yellow") for r in rs]
    agree = statistics.mean(a == b for a, b in zip(sv, evv))
    art[s] = {"stats_mean": statistics.mean(sv), "events_mean": statistics.mean(evv), "exact_agree": agree}
out["cards_artefact"] = art

# team id stability: ids per season, name variants per id
ids = defaultdict(set); names = defaultdict(set)
for r in ROWS:
    for side in ("home", "away"):
        ids[r["season"]].add(r[f"{side}_team_id"]); names[r[f"{side}_team_id"]].add(r[f"{side}_team"])
out["teams_per_season"] = {s: len(v) for s, v in ids.items()}
out["team_ids_total"] = len(names)
out["ids_with_multiple_names"] = {k: sorted(v) for k, v in names.items() if len(v) > 1}
out["awarded"] = [r["match_id"] for r in ROWS if r["awarded"] == "1"]
out["ht_unreliable"] = [r["match_id"] for r in ROWS if r["ht_source"] != "events"]
(HERE / "eda_numbers.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
