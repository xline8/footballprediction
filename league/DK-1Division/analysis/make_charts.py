"""Create Phase A descriptive charts. This script does not fit models."""
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "dk1_matches.csv"
OUT = Path(__file__).resolve().parent / "charts"
OUT.mkdir(exist_ok=True)


def val(row, key):
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return None


rows = list(csv.DictReader(DATA.open()))
seasons = sorted({r["season"] for r in rows})
metrics = {"Goals": ("home_goals", "away_goals"), "SOT": ("ShotsOnTarget_home", "ShotsOnTarget_away"), "Corners": ("corners_home", "corners_away"), "Yellows": ("yellow_cards_home", "yellow_cards_away"), "Total shots": ("total_shots_home", "total_shots_away")}

fig, ax = plt.subplots(figsize=(10, 5.5))
for label, cols in metrics.items():
    ys = []
    for season in seasons:
        rr = [r for r in rows if r["season"] == season]
        vals = [val(r, c) for r in rr for c in cols]
        vals = [x for x in vals if x is not None]
        ys.append(sum(vals) / len(rr) if len(vals) == 2 * len(rr) else math.nan)
    ax.plot(seasons, ys, marker="o", label=label)
ax.set_title("DK-1Division levels by season")
ax.set_ylabel("match total (both teams)")
ax.tick_params(axis="x", rotation=35)
ax.grid(alpha=.25)
ax.legend(ncol=3)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=160); plt.close(fig)


# Chronological team split-half Pearson reliabilities, descriptive only.
team_rows = []
for r in rows:
    for side in ("home", "away"):
        team_rows.append((r["team_id"] if "team_id" in r else r[f"{side}_team_id"], r["date"], {k: val(r, f"{v}_{side}") for k, v in {"SOT": "ShotsOnTarget", "Corners": "corners", "Shots": "total_shots", "Box touches": "touches_opp_box", "Yellows": "yellow_cards"}.items()}))


def corr(pairs):
    if len(pairs) < 3: return 0.0
    mx = sum(x for x, _ in pairs) / len(pairs); my = sum(y for _, y in pairs) / len(pairs)
    den = math.sqrt(sum((x - mx) ** 2 for x, _ in pairs) * sum((y - my) ** 2 for _, y in pairs))
    return sum((x - mx) * (y - my) for x, y in pairs) / den if den else 0.0


labels, values = [], []
for label in ["SOT", "Corners", "Shots", "Box touches", "Yellows"]:
    pairs = []
    for tid in sorted({x[0] for x in team_rows}):
        rr = sorted([x for x in team_rows if x[0] == tid and x[2][label] is not None], key=lambda x: x[1])
        if len(rr) < 20: continue
        cut = len(rr) // 2
        pairs.append((sum(x[2][label] for x in rr[:cut]) / cut, sum(x[2][label] for x in rr[cut:]) / (len(rr) - cut)))
    labels.append(label); values.append(corr(pairs))
fig, ax = plt.subplots(figsize=(7, 4.5)); ax.bar(labels, values, color="#3578a8")
ax.axhline(0, color="black", lw=.7); ax.set_ylim(-.2, 1); ax.set_ylabel("chronological split-half r")
ax.set_title("Team-trait reliability (descriptive)"); ax.tick_params(axis="x", rotation=25); fig.tight_layout()
fig.savefig(OUT / "trait_reliability.png", dpi=160); plt.close(fig)


fig, ax = plt.subplots(figsize=(7, 4.5))
labels = ["Goals", "SOT", "Corners", "Shots", "Yellows"]
shares = [0.436, 0.455, 0.469, 0.461, 0.314]
ax.bar(labels, shares, color="#c26d3c"); ax.axhline(.5, color="black", lw=.7, ls="--")
ax.set_ylim(0, .6); ax.set_ylabel("1H share"); ax.set_title("Frozen first-half constants (complete-splits era)")
for i, y in enumerate(shares): ax.text(i, y + .012, f"{y:.3f}", ha="center")
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=160); plt.close(fig)
