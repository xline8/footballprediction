"""Regenerate the RO-LigaII Step 4 charts from rl2_matches.csv."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
(HERE / "charts").mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader((HERE.parent / "data" / "rl2_matches.csv").open()))
inc = [r for r in rows if r["phase"] != "relegation_playoff"]
seasons = sorted({r["season"] for r in inc})

def n(r, key):
    return float(r[key])

def corr(xs, ys):
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return num / den

levels = {
    "Goals / match": lambda r: n(r, "home_goals") + n(r, "away_goals"),
    "Home win": lambda r: n(r, "home_goals") > n(r, "away_goals"),
    "OU2.5 over": lambda r: n(r, "home_goals") + n(r, "away_goals") > 2.5,
}
fig, axes = plt.subplots(1, 3, figsize=(12, 4))
for ax, (label, fn) in zip(axes, levels.items()):
    vals = [sum(fn(r) for r in inc if r["season"] == s) / sum(1 for r in inc if r["season"] == s) for s in seasons]
    ax.plot(seasons, vals, marker="o")
    ax.set_title(label)
    ax.tick_params(axis="x", rotation=45, labelsize=8)
fig.suptitle("RO-LigaII inclusion-set levels by season")
fig.tight_layout()
fig.savefig(HERE / "charts" / "levels_by_season.png", dpi=120)
plt.close(fig)

by_unit = defaultdict(list)
for r in inc:
    for side in ("home", "away"):
        by_unit[(r["season"], r[f"{side}_team_id"])].append((r["date"], r["match_id"], n(r, f"{side}_goals"), n(r, "away_goals" if side == "home" else "home_goals")))
xs = {"goals for": [], "goals against": []}
for vals in by_unit.values():
    vals.sort()
    for label, pos in (("goals for", 2), ("goals against", 3)):
        a = [v[pos] for v in vals[0::2]]
        b = [v[pos] for v in vals[1::2]]
        if a and b:
            xs[label].append((sum(a) / len(a), sum(b) / len(b)))
fig, ax = plt.subplots(figsize=(7, 4))
labels = list(xs)
ax.bar(labels, [corr([a for a, _ in xs[k]], [b for _, b in xs[k]]) for k in labels])
ax.set_ylim(0, 1)
ax.set_ylabel("split-half r (team-season odd/even)")
ax.set_title("RO-LigaII goals-only trait reliability")
fig.tight_layout()
fig.savefig(HERE / "charts" / "trait_reliability.png", dpi=120)
plt.close(fig)

# Goal-event half shares are descriptive constants only; event/score gaps are
# documented in DATA_UNDERSTANDING and EDA. Read the source events so the
# denominator is goal events, not the score-derived total.
index = {r["match_id"]: r for r in csv.DictReader((HERE.parents[2] / "data_enrichment" / "fotmob_world_index.csv").open()) if r["league_id"] == "9113"}
first, total = [], []
for s in seasons:
    first_s = total_s = 0
    for r in inc:
        if r["season"] != s:
            continue
        payload = json.loads((HERE.parents[2] / index[r["match_id"]]["path"]).read_text())
        events = (((payload.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events", []) or []
        goals = [e for e in events if e.get("type") == "Goal"]
        first_s += sum(isinstance(e.get("time"), (int, float)) and e["time"] <= 45 for e in goals)
        total_s += len(goals)
    first.append(first_s / total_s if total_s else 0)
    total.append(total_s)
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(seasons, first, marker="o", label="goals 1H share")
ax.axhline(0.457419, color="grey", linestyle="--", label="pooled constant")
ax.set_ylim(0, 0.7)
ax.set_ylabel("1H share")
ax.set_title("RO-LigaII goals half-share presentation constant")
ax.tick_params(axis="x", rotation=45)
ax.legend()
fig.tight_layout()
fig.savefig(HERE / "charts" / "halves_constants.png", dpi=120)
plt.close(fig)
print("charts written")
