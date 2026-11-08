"""Recompute and assert the frozen DK-2Division Phase A facts."""
import csv
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data/dk2_matches.csv").open()))
assert len(rows) == 1050 and len({r["match_id"] for r in rows}) == 1050
seasons = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
expected_goals = [523, 566, 572, 487, 533, 262]
expected_ht = [182, 159, 187, 185, 180, 86]

def corr(pairs):
    mx = sum(x for x, _ in pairs) / len(pairs); my = sum(y for _, y in pairs) / len(pairs)
    den = math.sqrt(sum((x - mx) ** 2 for x, _ in pairs) * sum((y - my) ** 2 for _, y in pairs))
    return sum((x - mx) * (y - my) for x, y in pairs) / den

for season, goal_total, ht_n in zip(seasons, expected_goals, expected_ht):
    rr = [r for r in rows if r["season"] == season]
    assert len(rr) == (90 if season == "2026/2027" else 192)
    assert sum(int(r["home_goals"]) + int(r["away_goals"]) for r in rr) == goal_total
    assert sum(r["ht_present"] == "1" for r in rr) == ht_n
    print(season, len(rr), goal_total, f"mean={goal_total / len(rr):.3f}")

pooled_hg = sum(int(r["home_goals"]) for r in rows)
pooled_ag = sum(int(r["away_goals"]) for r in rows)
assert round(pooled_hg / len(rows), 3) == 1.486
assert round(pooled_ag / len(rows), 3) == 1.317
assert round(sum(int(r["home_goals"]) + int(r["away_goals"]) > 2 for r in rows) / len(rows), 3) == 0.548
paired = [r for r in rows if r["ht_present"] == "1"]
assert sum(int(r["ht_home_goals"]) + int(r["ht_away_goals"]) for r in paired) == 1317
assert sum(int(r["home_goals"]) + int(r["away_goals"]) for r in paired) == 2856
assert round(1317 / 2856, 4) == 0.4611

# Split the chronologically ordered match list within each season into odd/even
# match slots. This is the pre-specified descriptive split, not a model fit.
attack, defence, shares = [], [], []
for season in seasons[:5]:
    rr = sorted((r for r in rows if r["season"] == season), key=lambda r: (r["date"], r["match_id"]))
    traits = defaultdict(lambda: [[], []])
    for i, r in enumerate(rr):
        for side, opponent in (("home", "away"), ("away", "home")):
            tid = r[f"{side}_team_id"]
            traits[tid][i % 2].append((int(r[f"{side}_goals"]), int(r[f"{opponent}_goals"]), r))
    for tid, vals in traits.items():
        a, b = vals
        attack.append((sum(x[0] for x in a) / len(a), sum(x[0] for x in b) / len(b)))
        defence.append((sum(x[1] for x in a) / len(a), sum(x[1] for x in b) / len(b)))
        h = [[], []]
        for slot, part in enumerate(vals):
            for x in part:
                if x[2]["ht_present"] != "1":
                    continue
                h[slot].append((x[2]["ht_home_goals"] if x[2]["home_team_id"] == tid else x[2]["ht_away_goals"], x[0]))
            h[slot] = [(int(ht), int(ft)) for ht, ft in h[slot]]
        if all(h) and sum(x[1] for x in h[0]) >= 8 and sum(x[1] for x in h[1]) >= 8:
            shares.append((sum(x[0] for x in h[0]) / sum(x[1] for x in h[0]), sum(x[0] for x in h[1]) / sum(x[1] for x in h[1])))
assert len(attack) == len(defence) == 60
assert round(corr(attack), 3) == 0.635
assert round(corr(defence), 3) == 0.481
assert len(shares) == 59
assert round(corr(shares), 3) == -0.120
print("home_goals=1.486 away_goals=1.317 OU2.5=0.548")
print("ht_paired=979 goals_1h_share=0.4611")
print("reliability attack=0.635 defence=0.481 team_1h_share=-0.120 (n=59)")
