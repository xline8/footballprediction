"""EDA numbers for UA-PremierLeague from ua_matches.csv (frozen inputs only)."""
import csv, json, math, random
from collections import defaultdict, Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = list(csv.DictReader((HERE.parent / "data" / "ua_matches.csv").open()))
SEASONS = sorted({r["season"] for r in ROWS})

def f(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def mean(xs): return sum(xs) / len(xs) if xs else None

out = {"seasons": {}}
for s in SEASONS:
    sub = [r for r in ROWS if r["season"] == s]
    d = {"n": len(sub), "dates": [min(r["date"] for r in sub), max(r["date"] for r in sub)],
         "teams_by_id": len({r["home_team_id"] for r in sub} | {r["away_team_id"] for r in sub}),
         "teams_by_name": len({r["home_team"] for r in sub} | {r["away_team"] for r in sub}),
         "rounds": sorted({r["round"] for r in sub}, key=lambda x: (len(x), x)),
         "has_stats": sum(int(r["has_stats_all"]) for r in sub),
         "has_events": sum(int(r["has_events"]) for r in sub),
         "has_splits": sum(int(r["has_period_splits_content"]) for r in sub),
         "referee_nonempty": sum(1 for r in sub if r["referee"].strip()),
         "cancelled": sum(int(r["cancelled"]) for r in sub),
         "not_finished": sum(1 for r in sub if int(r["finished"]) == 0),
         "xg_rows": sum(1 for r in sub if f(r["expected_goals_home"]) is not None),
         "touches_rows": sum(1 for r in sub if f(r["touches_opp_box_home"]) is not None),
         "stats_cards_rows": sum(1 for r in sub if f(r["yellow_cards_home"]) is not None),
         "zero_stub_rows": sum(1 for r in sub if int(r["has_stats_all"]) and f(r["total_shots_home"]) == 0 and f(r["total_shots_away"]) == 0 and f(r["corners_home"]) == 0 and f(r["corners_away"]) == 0),
         }
    st = [r for r in sub if int(r["has_stats_all"])]
    d["goals_pg"] = mean([f(r["home_goals"]) + f(r["away_goals"]) for r in sub])
    d["home_win_rate"] = mean([1.0 if f(r["home_goals"]) > f(r["away_goals"]) else 0.0 for r in sub])
    d["ou25_rate"] = mean([1.0 if f(r["home_goals"]) + f(r["away_goals"]) > 2.5 else 0.0 for r in sub])
    if st:
        d["sot_pg"] = mean([f(r["ShotsOnTarget_home"]) + f(r["ShotsOnTarget_away"]) for r in st])
        d["corners_pg"] = mean([f(r["corners_home"]) + f(r["corners_away"]) for r in st])
        d["shots_pg"] = mean([f(r["total_shots_home"]) + f(r["total_shots_away"]) for r in st])
    ev = [r for r in sub if int(r["has_events"])]
    d["ev_yellow_pg"] = mean([f(r["ev_yellow_home"]) + f(r["ev_yellow_away"]) for r in ev]) if ev else None
    both = [r for r in sub if f(r["yellow_cards_home"]) is not None and int(r["has_events"])]
    if both:
        diffs = [(f(r["yellow_cards_home"]) + f(r["yellow_cards_away"])) - (f(r["ev_yellow_home"]) + f(r["ev_yellow_away"])) for r in both]
        d["cards_both_n"] = len(both)
        d["cards_exact_agree"] = mean([1.0 if x == 0 else 0.0 for x in diffs])
        d["cards_stats_minus_events"] = mean(diffs)
        d["stats_yellow_pg"] = mean([f(r["yellow_cards_home"]) + f(r["yellow_cards_away"]) for r in both])
    # halves from event times (builder ht_ columns for goals; cards need raw events -> use ht goals only here)
    g1 = sum(f(r["ht_home_goals"]) + f(r["ht_away_goals"]) for r in sub)
    gT = sum(f(r["home_goals"]) + f(r["away_goals"]) for r in sub)
    d["goals_1h_share_events"] = (g1 / gT) if gT else None
    out["seasons"][s] = d

# team id/name stability
id2names = defaultdict(set); name2ids = defaultdict(set)
for r in ROWS:
    for side in ("home", "away"):
        id2names[r[f"{side}_team_id"]].add(r[f"{side}_team"]); name2ids[r[f"{side}_team"]].add(r[f"{side}_team_id"])
out["ids_with_multiple_names"] = {k: sorted(v) for k, v in id2names.items() if len(v) > 1}
out["names_with_multiple_ids"] = {k: sorted(v) for k, v in name2ids.items() if len(v) > 1}
out["n_team_ids"] = len(id2names)

# split-half reliability on team-match rows, per era blocks
TM = list(csv.DictReader((HERE.parent / "data" / "ua_team_matches.csv").open()))
def split_half(rows, key_for, key_against=None, min_n=20):
    by = defaultdict(list)
    for r in rows:
        v = f(r.get(key_for))
        if v is not None: by[r["team_id"]].append(v)
    xs, ys = [], []
    rng = random.Random(42)
    for t, vs in by.items():
        if len(vs) >= min_n:
            idx = list(range(len(vs))); rng.shuffle(idx)
            h = len(vs) // 2
            xs.append(mean([vs[i] for i in idx[:h]])); ys.append(mean([vs[i] for i in idx[h:]]))
    if len(xs) < 5: return None, len(xs)
    mx, my = mean(xs), mean(ys)
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    vx = sum((a - mx) ** 2 for a in xs); vy = sum((b - my) ** 2 for b in ys)
    return (cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else None), len(xs)

def block(seasons):
    return [r for r in TM if r["season"] in seasons]
ALL = [r["season"] for r in TM]
FITERA = ["2022/2023", "2023/2024", "2024/2025", "2025/2026"]
out["reliability"] = {}
for label, seasons in (("all", sorted(set(ALL))), ("fit_era_2022plus", FITERA), ("dev_block_2022_2025", FITERA[:3])):
    rel = {}
    for trait, kf, ka in (("goals", "goals_for", "goals_against"), ("sot", "ShotsOnTarget_for", "ShotsOnTarget_against"),
                          ("corners", "corners_for", "corners_against"), ("shots", "total_shots_for", "total_shots_against"),
                          ("yellow_stats", "yellow_cards_for", "yellow_cards_against"), ("yellow_events", "yellow_events_for", "yellow_events_against"),
                          ("touches", "touches_opp_box_for", "touches_opp_box_against"), ("big_chance", "big_chance_for", "big_chance_against"),
                          ("possession", "BallPossesion_for", None), ("xg", "expected_goals_for", "expected_goals_against")):
        rf, nf = split_half(block(seasons), kf); ra, na = split_half(block(seasons), ka) if ka else (None, 0)
        rel[trait] = {"for_r": rf, "for_n_teams": nf, "against_r": ra, "against_n_teams": na}
    out["reliability"][label] = rel

# referee reliability (events yellows per match by referee) -- coverage first
refs = Counter(r["referee"] for r in ROWS if r["referee"].strip())
out["referee_distinct"] = len(refs); out["referee_top"] = refs.most_common(5)

# over-rates for line choice on scored dev (2023/2024+2024/2025, stats rows, fit era)
dev = [r for r in ROWS if r["season"] in ("2023/2024", "2024/2025") and int(r["has_stats_all"])]
def over_rate(rows, tot, line): return mean([1.0 if t > line else 0.0 for t in tot])
out["dev_lines"] = {"n_stats": len(dev),
  "sot": {str(l): over_rate(dev, [f(r["ShotsOnTarget_home"]) + f(r["ShotsOnTarget_away"]) for r in dev], l) for l in (7.5, 8.5, 9.5)},
  "corners": {str(l): over_rate(dev, [f(r["corners_home"]) + f(r["corners_away"]) for r in dev], l) for l in (8.5, 9.5, 10.5)},
  "shots": {str(l): over_rate(dev, [f(r["total_shots_home"]) + f(r["total_shots_away"]) for r in dev], l) for l in (23.5, 24.5, 25.5, 26.5)},
  "cards_ev": {str(l): over_rate(dev, [f(r["ev_yellow_home"]) + f(r["ev_yellow_away"]) for r in dev], l) for l in (3.5, 4.5, 5.5)},
  "cards_stats_n": len([r for r in dev if f(r["yellow_cards_home"]) is not None]),
  }
vir = [r for r in ROWS if r["season"] == "2025/2026"]
out["virgin_n"] = len(vir); out["virgin_stats_n"] = sum(int(r["has_stats_all"]) for r in vir)
print(json.dumps(out, indent=1, default=str))
(HERE / "eda_numbers.json").write_text(json.dumps(out, indent=1, default=str))
