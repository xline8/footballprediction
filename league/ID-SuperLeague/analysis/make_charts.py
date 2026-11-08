"""Create Phase A descriptive charts. This script does not fit models."""
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "id_matches.csv"
TDATA = ROOT / "data" / "id_team_matches.csv"
OUT = Path(__file__).resolve().parent / "charts"
OUT.mkdir(exist_ok=True)


def val(row, key):
    try:
        return float(row[key])
    except (KeyError, TypeError, ValueError):
        return None


rows = [r for r in csv.DictReader(DATA.open()) if r["phase"] == "regular"]
seasons = sorted({r["season"] for r in rows})
metrics = {"Goals": ("home_goals", "away_goals"), "SOT": ("ShotsOnTarget_home", "ShotsOnTarget_away"),
           "Corners": ("corners_home", "corners_away"), "Yellows (events)": ("yellow_home", "yellow_away"),
           "Total shots": ("total_shots_home", "total_shots_away")}

fig, ax = plt.subplots(figsize=(10, 5.5))
for label, cols in metrics.items():
    ys = []
    for season in seasons:
        rr = [r for r in rows if r["season"] == season]
        vals = [val(r, c) for r in rr for c in cols]
        vals = [x for x in vals if x is not None]
        # per-match total: sum of available values over matches that have both sides
        both = [r for r in rr if all(val(r, c) is not None for c in cols)]
        ys.append(sum(val(r, cols[0]) + val(r, cols[1]) for r in both) / len(both) if both else math.nan)
    ax.plot(seasons, ys, marker="o", label=label)
ax.set_title("ID-SuperLeague levels by season (regular; stats-era markets end Oct 2023)")
ax.set_ylabel("match total (both teams)")
ax.tick_params(axis="x", rotation=35)
ax.grid(alpha=.25)
ax.legend(ncol=3)
fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=160); plt.close(fig)


# Within-season chronological split-half reliabilities (descriptive).
trows = [r for r in csv.DictReader(TDATA.open()) if r["phase"] == "regular"]
traits = {"Goals for": "goals_for", "Goals against": "goals_against",
          "Yellows for": "yellow_for", "Yellows against": "yellow_against",
          "SOT for": "ShotsOnTarget_for", "Corners for": "corners_for",
          "Possession for": "BallPossesion_for"}


def corr(pairs):
    if len(pairs) < 3:
        return 0.0
    ma = sum(p[0] for p in pairs) / len(pairs); mb = sum(p[1] for p in pairs) / len(pairs)
    num = sum((a - ma) * (b - mb) for a, b in pairs)
    den = (sum((a - ma) ** 2 for a, _ in pairs) * sum((b - mb) ** 2 for _, b in pairs)) ** 0.5
    return num / den if den else 0.0


labels, rs = [], []
for label, col in traits.items():
    groups = {}
    for r in trows:
        v = val(r, col)
        if v is None:
            continue
        groups.setdefault((r["season"], r["team_id"]), []).append((r["date"], v))
    pairs = []
    for g in groups.values():
        if len(g) < 16:
            continue
        g.sort(); h = len(g) // 2
        pairs.append((sum(x[1] for x in g[:h]) / h, sum(x[1] for x in g[h:]) / (len(g) - h)))
    labels.append(label); rs.append(corr(pairs))

fig, ax = plt.subplots(figsize=(9, 4.5))
ax.barh(labels, rs)
ax.set_title("ID-SuperLeague trait reliability (within-season split-half r)")
ax.set_xlabel("Pearson r")
ax.grid(alpha=.25, axis="x")
fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=160); plt.close(fig)


# Halves constants: per-season pooled 1H shares from event order.
fig, axs = plt.subplots(1, 2, figsize=(10, 4.2))
for ax, (hcols, tcols, title, const) in zip(axs, [
        (("ht_home_goals", "ht_away_goals"), ("home_goals", "away_goals"), "Goals 1H share", 0.434),
        (("ev_yellow_1h_home", "ev_yellow_1h_away"), ("yellow_home", "yellow_away"), "Yellows 1H share", 0.385)]):
    ys = []
    for season in seasons:
        rr = [r for r in rows if r["season"] == season and r["goals_events_match_score"] == "1"
              and (title.startswith("Goals") or r["events_complete"] == "1")]
        num = sum((val(r, hcols[0]) or 0) + (val(r, hcols[1]) or 0) for r in rr)
        den = sum((val(r, tcols[0]) or 0) + (val(r, tcols[1]) or 0) for r in rr)
        ys.append(num / den if den else math.nan)
    ax.plot(seasons, ys, marker="o")
    ax.axhline(const, color="grey", linestyle="--", label=f"frozen constant {const}")
    ax.set_title(title); ax.tick_params(axis="x", rotation=35); ax.grid(alpha=.25); ax.legend()
fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=160); plt.close(fig)
print("charts written to", OUT)
