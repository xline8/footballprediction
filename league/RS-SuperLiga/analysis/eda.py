"""EDA for RS-SuperLiga (Serbia Super Liga, FotMob 182): era structure,
trait reliability, halves shares, target-definition checks, format facts.
Writes eda_summary.json + inventory_summary.json next to this file.

SPLIT DISCIPLINE (frozen by the brief, BRIEF.md):
- DEV = 2021/2022 .. 2024/2025. VIRGIN = 2025/2026 (n=296).
- RESERVE = 2026/2027 is EXCLUDED from every computation in this script:
  its directory is never read, its CSV rows are filtered out first.
- VIRGIN rows are used ONLY for inventory purposes (feed coverage, levels)
  and for the two target-definition checks the task explicitly authorises
  for the rich era (stats-vs-events cards; splits consistency). Virgin
  rows are NEVER used to choose features, thresholds, arms, or halves
  constants. Where dev data does not exist, the value is null with a
  reason -- never a virgin number borrowed as a frozen constant.

Method follows the FI-Veikkausliiga reference eda.py (split-half traits,
event-time halves shares with a binomial-noise comparison).
"""
import csv, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # ~/workspace/league-work/RS-SuperLiga
WORK = ROOT / "work" / "Serbia" / "Super Liga"

DEV = ["2021/2022", "2022/2023", "2023/2024", "2024/2025"]
VIRGIN = "2025/2026"
RESERVE = "2026/2027"
SEASONS = DEV + [VIRGIN]  # reserve excluded everywhere
SEASON_DIRS = {"2021/2022": "2021-2022", "2022/2023": "2022-2023",
               "2023/2024": "2023-2024", "2024/2025": "2024-2025",
               "2025/2026": "2025-2026"}

M = list(csv.DictReader(open(HERE.parent / "data" / "rs_matches.csv")))
M = [r for r in M if r["season"] != RESERVE]  # reserve excluded, first thing
assert all(r["season"] in SEASONS for r in M), "unexpected season in CSV"
assert len(M) == 1488, f"expected 1488 rows (dev+virgin), got {len(M)}"


def f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


for r in M:
    for k in list(r):
        if k not in ("match_id", "league", "season", "date", "round", "phase",
                     "home_team", "away_team", "cards_source", "ht_source",
                     "referee", "coverage_level"):
            r[k] = f(r[k]) if r[k] not in ("", None) else None

out = {"seasons": SEASONS, "dev_seasons": DEV, "virgin_season": VIRGIN,
       "reserve_season_excluded": RESERVE,
       "reserve_exclusion_note": "2026/2027 (104 rows in rs_matches.csv) "
       "excluded from every computation in this script; its raw-JSON "
       "directory was never read.",
       "n": len(M), "n_dev": sum(1 for r in M if r["season"] in DEV),
       "n_virgin": sum(1 for r in M if r["season"] == VIRGIN)}

# ---------------------------------------------------------------- levels
lev = {}
for s in SEASONS:
    sub = [r for r in M if r["season"] == s]
    st = [r for r in sub if r["has_stats_all"] == 1]

    def mean(key, rows):
        v = [r[key] for r in rows if r[key] is not None]
        return round(statistics.mean(v), 3) if v else None

    lev[s] = {
        "n": len(sub), "stats_n": len(st),
        "goals": round(statistics.mean([r["home_goals"] + r["away_goals"] for r in sub]), 3),
        "home_goals": round(statistics.mean([r["home_goals"] for r in sub]), 3),
        "away_goals": round(statistics.mean([r["away_goals"] for r in sub]), 3),
        "sot": mean("ShotsOnTarget_home", st) is not None and round(
            statistics.mean([r["ShotsOnTarget_home"] + r["ShotsOnTarget_away"] for r in st]), 3) or None,
        "corners": round(statistics.mean([r["corners_home"] + r["corners_away"] for r in st]), 3) if st else None,
        "shots": round(statistics.mean([r["total_shots_home"] + r["total_shots_away"] for r in st]), 3) if st else None,
        "yellows_event": round(statistics.mean([r["yellow_home"] + r["yellow_away"] for r in sub]), 3),
        "yellows_stats": round(statistics.mean([r["stats_yellow_home"] + r["stats_yellow_away"] for r in st]), 3) if st else None,
        "over25_rate": round(statistics.mean([1 if r["home_goals"] + r["away_goals"] > 2.5 else 0 for r in sub]), 3),
    }
out["levels"] = lev

# ------------------------------------------------- trait reliability (dev)
def trait(col_h, col_a, seasons):
    """Split-half by team: odd/even appearances pooled over `seasons`.
    Returns null r when the column has no usable rows in those seasons."""
    per = defaultdict(lambda: [[], []])
    rows = [r for r in M if r["season"] in seasons and r[col_h] is not None]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    cnt = defaultdict(int)
    for r in rows:
        for tid, val in ((r["home_team_id"], r[col_h]), (r["away_team_id"], r[col_a])):
            h = cnt[tid] % 2
            per[tid][h].append(val)
            cnt[tid] += 1
    xs, ys = [], []
    for tid, (a, b) in per.items():
        if len(a) >= 8 and len(b) >= 8:
            xs.append(statistics.mean(a))
            ys.append(statistics.mean(b))
    if len(xs) < 8:
        return {"n_teams": len(xs), "r": None,
                "note": "too few teams with >=8 matches per half"}
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return {"n_teams": len(xs),
            "r": round(cov / math.sqrt(vx * vy), 3) if vx > 0 and vy > 0 else None}


def no_dev_data(col):
    return {"n_teams": 0, "r": None,
            "note": f"no dev data: {col} exists only in the virgin season "
                    "(stats feed absent 2021/2022-2024/2025); reliability "
                    "cannot be measured on dev and virgin rows must not "
                    "choose features"}


out["traits_dev"] = {
    "goals_for": trait("home_goals", "away_goals", DEV),
    # Event yellows in dev are YellowRed-only (no plain Yellow Card events
    # at all 2021-2025): the trait is computed on that broken feed and is
    # reported only to document the break, never to adopt a cards feature.
    "yellows_event_for": trait("yellow_home", "yellow_away", DEV),
    "sot_for": no_dev_data("ShotsOnTarget"),
    "corners_for": no_dev_data("corners"),
    "shots_for": no_dev_data("total_shots"),
    "possession": no_dev_data("BallPossesion"),
    "touches_for": no_dev_data("touches_opp_box"),
    "big_chance_for": no_dev_data("big_chance"),
    "fouls_for": no_dev_data("fouls"),
    "keeper_saves_for": no_dev_data("keeper_saves"),
}

# Season-to-season correlation of team goals-for per match (dev only):
# team-season mean goals-for, consecutive dev-season pairs.
def season_team_means(col_h, col_a, season):
    per = defaultdict(list)
    for r in M:
        if r["season"] != season:
            continue
        per[r["home_team_id"]].append(r[col_h])
        per[r["away_team_id"]].append(r[col_a])
    return {t: statistics.mean(v) for t, v in per.items() if len(v) >= 10}


def pearson(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return round(cov / math.sqrt(vx * vy), 3) if vx > 0 and vy > 0 else None


s2s = {}
for a, b in zip(DEV[:-1], DEV[1:]):
    ma, mb = season_team_means("home_goals", "away_goals", a), season_team_means("home_goals", "away_goals", b)
    common = sorted(set(ma) & set(mb))
    s2s[f"{a}_vs_{b}"] = {"n_teams": len(common),
                         "r": pearson([ma[t] for t in common], [mb[t] for t in common]) if len(common) >= 8 else None}
out["traits_season_to_season_goals_for_dev"] = s2s

# ------------------------------------------------------------ halves (dev)
AWARDED_MATCH = 4271663  # 2023/2024: awarded 0-3, events show 7 goals


def halves(num_key, den_fn, seasons, label, exclude_ids=()):
    shares, tot, num = [], 0, 0
    for r in M:
        if r["season"] not in seasons or int(r["match_id"]) in exclude_ids:
            continue
        d = den_fn(r)
        if d and d > 0 and r[num_key] is not None:
            shares.append(r[num_key] / d)
            num += r[num_key]
            tot += d
    p = num / tot if tot else None
    ds = [den_fn(r) for r in M if r["season"] in seasons
          and int(r["match_id"]) not in exclude_ids and den_fn(r)]
    exp_var = p * (1 - p) / (tot / len(ds)) if p is not None and ds else None
    obs_var = statistics.variance(shares) if len(shares) > 2 else None
    return {"share": round(p, 4) if p is not None else None,
            "n_matches": len(shares), "total_denominator": tot,
            "total_numerator": num,
            "obs_var": round(obs_var, 5) if obs_var is not None else None,
            "binom_var": round(exp_var, 5) if exp_var is not None else None,
            "excess_var": round(obs_var - exp_var, 5) if obs_var is not None and exp_var is not None else None}


out["halves_goals_dev"] = halves(
    "goals_1h_total", lambda r: r["home_goals"] + r["away_goals"], DEV, "goals",
    exclude_ids=(AWARDED_MATCH,))
out["halves_goals_dev_incl_awarded"] = halves(
    "goals_1h_total", lambda r: r["home_goals"] + r["away_goals"], DEV, "goals")
# League-member halves (frozen candidate): same as above but excluding the
# 8 cross-tier qualification ties (see qualification inventory below).
out["halves_goals_dev_league_only"] = halves(
    "goals_1h_total",
    lambda r: r["home_goals"] + r["away_goals"] if r["phase"] != "qualification" else 0,
    DEV, "goals", exclude_ids=(AWARDED_MATCH,))
out["halves_yellows_dev"] = halves(
    "ev_yellow_1h", lambda r: r["yellow_home"] + r["yellow_away"], DEV, "yellows")
out["halves_note_awarded_match"] = (
    f"Match {AWARDED_MATCH} (2023/2024, FK Radnicki 1923 vs FK Crvena "
    "Zvezda) was an awarded 0-3 win: FT goals 3 but 7 Goal events (5 in "
    "1H). Its event 1H count exceeds its FT total, so it is excluded from "
    "the frozen halves_goals_dev share; the inclusive value is reported "
    "separately as halves_goals_dev_incl_awarded.")
# Split halves: NO dev season has period splits -> null, do not borrow virgin.
out["halves_splits_dev"] = {
    k: {"share": None, "n_matches": 0,
        "note": "no dev data: period splits (FirstHalf/SecondHalf) exist "
                "only in the virgin season; the virgin share is NOT used "
                "as a frozen constant"}
    for k in ("total_shots", "ShotsOnTarget", "corners", "yellow_cards")}
out["halves_yellows_dev_note"] = (
    "Dev event yellows total 13 first-half cards on 108 cards overall "
    "(see inventory); the 1H share is computed on that near-empty feed "
    "and is NOT a usable frozen constant for a cards product.")

# ------------------------------------------------------- dev medians/lines
dev_goals = [r for r in M if r["season"] in DEV]
out["dev_medians"] = {
    "sot": None, "corners": None, "shots": None, "yellows": None,
    "note": "no dev medians for SOT/corners/shots/yellows: no stats feed "
            "in dev and the event cards feed is broken (YellowRed-only); "
            "no primary line can be set from dev for S/C/K/T",
    "goals_over25_rate_dev": round(statistics.mean(
        [1 if r["home_goals"] + r["away_goals"] > 2.5 else 0 for r in dev_goals]), 3),
    "goals_median_dev": statistics.median(
        [r["home_goals"] + r["away_goals"] for r in dev_goals]),
}

# ------------------------------------------------------------- X2 entrants
# Entrant = club absent the previous season among REGULAR-phase teams AND
# playing regular-phase matches this season. The plain "absent previous
# season" rule is contaminated here: the qualification (relegation
# play-off) ties bring in tier-2 clubs for 2 matches only (FK Graficar
# and Indjija in 2022/2023; FK IMT Beograd and Zeleznicar Pancevo in
# 2021/2022, who were tier-2 opponents then and promoted members from
# 2023/2024). Those are cross-tier opponents, not promoted entrants.
sup_teams, name_of = defaultdict(set), {}
regular_teams = defaultdict(set)
for r in M:
    sup_teams[r["season"]].add(int(r["home_team_id"]))
    sup_teams[r["season"]].add(int(r["away_team_id"]))
    if r["phase"] == "regular":
        regular_teams[r["season"]].add(int(r["home_team_id"]))
        regular_teams[r["season"]].add(int(r["away_team_id"]))
    name_of[int(r["home_team_id"])] = r["home_team"]
    name_of[int(r["away_team_id"])] = r["away_team"]
entrants = []
for s in SEASONS[1:]:
    prev = {"2022/2023": "2021/2022", "2023/2024": "2022/2023",
            "2024/2025": "2023/2024", "2025/2026": "2024/2025"}[s]
    for tid in sorted(regular_teams[s]):
        if tid not in regular_teams.get(prev, ()):
            entrants.append((s, tid))
# Cross-tier qualification-only clubs (inventory, not entrants): clubs with
# NO regular-phase appearance in any season in the corpus -- they exist
# only as tier-2 play-off opponents. (FK IMT Beograd and Zeleznicar
# Pancevo were tier-2 opponents in 2021/2022 but became promoted regular
# members from 2023/2024, so they are NOT in this list.)
all_regular = set().union(*regular_teams.values()) if regular_teams else set()
qual_only = sorted({tid for s in SEASONS for tid in sup_teams[s]
                    if tid not in all_regular})
out["qualification_cross_tier_clubs"] = [
    {"team_id": t, "team": name_of.get(t),
     "seasons": sorted({r["season"] for r in M
                        if t in (r["home_team_id"], r["away_team_id"])})}
    for t in qual_only]
out["qualification_matches"] = {
    "n": sum(1 for r in M if r["phase"] == "qualification"),
    "seasons": sorted({r["season"] for r in M if r["phase"] == "qualification"}),
    "note": "2-legged relegation/promotion play-off ties: a Super Liga "
            "club vs a Prva Liga (tier 2) club. Cross-tier rows; the "
            "design doc excludes them from fitting (see MODEL_DESIGN). "
            "They stay in rs_matches.csv with phase=qualification and in "
            "the levels table, but out of halves_goals_dev_league_only "
            "and out of the X2 entrant measurement."}
out["x2_entrants"] = [{"season": s, "team_id": t, "team": name_of.get(t)}
                      for s, t in entrants]
diffs = []
for s, tid in entrants:
    if s not in DEV:
        continue  # virgin entrant performance is never measured (would choose features from virgin)
    sub = [r for r in M if r["season"] == s and tid in (r["home_team_id"], r["away_team_id"])]
    gf = statistics.mean([(r["home_goals"] if r["home_team_id"] == tid else r["away_goals"]) for r in sub])
    ga = statistics.mean([(r["away_goals"] if r["home_team_id"] == tid else r["home_goals"]) for r in sub])
    lg = statistics.mean([r["home_goals"] + r["away_goals"] for r in M if r["season"] == s]) / 2
    diffs.append((round(gf - lg, 3), round(ga - lg, 3)))
out["x2_entrant_gf_ga_diff_vs_league_team_mean_dev"] = {
    "n": len(diffs),
    "gf_diff": round(statistics.mean([d[0] for d in diffs]), 3) if diffs else None,
    "ga_diff": round(statistics.mean([d[1] for d in diffs]), 3) if diffs else None,
    "note": "dev transitions only (2022/2023-2024/2025); the 2025/2026 "
            "entrant is listed in x2_entrants for inventory but its "
            "performance is not measured"}

# ------------------------------------------- cards: stats vs events (virgin only)
art = {}
sub = [r for r in M if r["season"] == VIRGIN and r["stats_yellow_home"] is not None]
ev = [r["ev_yellow_home"] + r["ev_yellow_away"] for r in sub]
st = [r["stats_yellow_home"] + r["stats_yellow_away"] for r in sub]
art[VIRGIN] = {
    "n": len(sub),
    "exact": round(statistics.mean([1 if a == b else 0 for a, b in zip(ev, st)]), 3),
    "mean_ev": round(statistics.mean(ev), 3),
    "mean_stats": round(statistics.mean(st), 3),
    "mean_stats_minus_ev": round(statistics.mean([b - a for a, b in zip(ev, st)]), 3),
    "ev_gt_stats": sum(1 for a, b in zip(ev, st) if a > b),
    "stats_gt_ev": sum(1 for a, b in zip(ev, st) if b > a),
    "note": "rich-era-only check (stats yellows exist only in the virgin "
            "season); the stats feed NEVER exceeds events here -- it "
            "systematically undercounts yellows vs the event feed"}
out["cards_stats_vs_events"] = art

# Splits consistency (virgin inventory only, not a feature/threshold input)
bad = tot = 0
for r in M:
    if r["season"] == VIRGIN and r["fh_corners_home"] is not None:
        tot += 1
        if abs((r["fh_corners_home"] + r["sh_corners_home"]) - r["corners_home"]) > 0.01:
            bad += 1
out["splits_consistency_corners_home_virgin_inventory"] = {"n": tot, "mismatch": bad}

# ------------------------------------------------------- phases / teams
out["phase_counts"] = {s: {p: sum(1 for r in M if r["season"] == s and r["phase"] == p)
                           for p in ("regular", "championship", "relegation", "qualification")}
                       for s in SEASONS}
out["teams_per_season"] = {s: len(sup_teams[s]) for s in SEASONS}
idnames = defaultdict(set)
for r in M:
    idnames[int(r["home_team_id"])].add(r["home_team"])
    idnames[int(r["away_team_id"])].add(r["away_team"])
out["team_ids_multi_name"] = {str(k): sorted(v) for k, v in idnames.items() if len(v) > 1}
out["team_ids_total"] = len(idnames)
out["team_ids_note"] = ("25 distinct team ids in dev+virgin rows. The "
    "pre-findings figure of 27 counts the full CSV including the reserve "
    "season 2026/2027, which this script excludes; 2 ids appear only in "
    "the reserve season and are not enumerated here.")
out["calendar"] = {s: {"first": min(r["date"] for r in M if r["season"] == s),
                       "last": max(r["date"] for r in M if r["season"] == s)}
                   for s in SEASONS}
out["no_events_matches_dev"] = {s: sum(1 for r in M if r["season"] == s and r["has_events"] == 0)
                                for s in DEV}
out["coverage_level_by_season"] = {s: Counter(r["coverage_level"] for r in M if r["season"] == s)
                                   for s in SEASONS}
out["coverage_level_by_season"] = {s: dict(c) for s, c in out["coverage_level_by_season"].items()}

# ============================================ raw-JSON inventory (dev+virgin only)
inv = {"by_season": {}, "reserve_excluded": RESERVE,
       "note": "Raw JSONs read only for dev seasons + virgin (inventory). "
               "The 2026/2027 directory was never listed or opened."}
for s in SEASONS:
    d = SEASON_DIRS[s]
    files = sorted((WORK / d).glob("*.json"))
    n = len(files)
    evtypes, card_detail = Counter(), Counter()
    n_ev = n_lineup = n_lineup_fullxi = n_stats = n_ref = n_shotmap = 0
    keys = Counter()
    periods_seen = Counter()
    goal_ev = ft_goals = goal_mismatch = 0
    refs = Counter()
    for p in files:
        dd = json.load(open(p))
        c = dd.get("content") or {}
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        if evs:
            n_ev += 1
        for e in evs:
            evtypes[e.get("type")] += 1
            if e.get("type") == "Card":
                card_detail[e.get("card")] += 1
            if e.get("type") == "Goal":
                goal_ev += 1
        lu = c.get("lineup") or {}
        if lu and (lu.get("homeTeam") or lu.get("awayTeam")):
            n_lineup += 1
            hs = len(((lu.get("homeTeam") or {}).get("starters")) or [])
            as_ = len(((lu.get("awayTeam") or {}).get("starters")) or [])
            if hs == 11 and as_ == 11:
                n_lineup_fullxi += 1
        per = (c.get("stats") or {}).get("Periods") or {}
        if per:
            n_stats += 1
        periods_seen[tuple(sorted(per.keys()))] += 1
        for period, block in per.items():
            for g in (block or {}).get("stats", []) or []:
                for stt in g.get("stats", []) or []:
                    keys[(period, stt.get("key"))] += 1
        ref = (((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text")
        if ref:
            n_ref += 1
            refs[ref] += 1
        if (c.get("shotmap") or {}).get("shots"):
            n_shotmap += 1
        ss = ((dd.get("header") or {}).get("status") or {}).get("scoreStr") or "0 - 0"
        a, b = ss.split("-")
        ft = int(a) + int(b)
        ft_goals += ft
        ge = sum(1 for e in evs if e.get("type") == "Goal")
        if ge != ft:
            goal_mismatch += 1
    allkeys = sorted({k for (pp, k) in keys if pp == "All"})
    fhkeys = sorted({k for (pp, k) in keys if pp == "FirstHalf"})
    inv["by_season"][s] = {
        "n_json": n,
        "events_matches": n_ev,
        "no_events_matches": n - n_ev,
        "event_types": dict(evtypes),
        "card_detail": dict(card_detail),
        "goal_events_total": goal_ev,
        "ft_goals_total": ft_goals,
        "goal_event_vs_ft_mismatch_matches": goal_mismatch,
        "lineup_block": n_lineup,
        "lineup_full_xi_both_sides": n_lineup_fullxi,
        "stats_matches": n_stats,
        "stats_keys_all_n": len(allkeys),
        "stats_keys_all": allkeys,
        "stats_keys_firsthalf_n": len(fhkeys),
        "periods_seen": {str(k): v for k, v in periods_seen.items()},
        "referee_named": n_ref,
        "referee_distinct": len(refs),
        "shotmap_matches": n_shotmap,
        "has_expected_goals_key": any("expected_goals" in k.lower() or "expectedgoals" in k.lower()
                                      for k in allkeys),
    }
inv["team_ids_total"] = len(idnames)
json.dump(out, open(HERE / "eda_summary.json", "w"), indent=1)
json.dump(inv, open(HERE / "inventory_summary.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print(json.dumps(inv, indent=1))
