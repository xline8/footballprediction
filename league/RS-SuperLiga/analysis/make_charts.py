"""Charts for RS-SuperLiga EDA (levels by season, trait reliability,
halves constants). Mechanics copied from the FI-Veikkausliiga reference
make_charts.py; adapted to this league's era break: SOT/corners/shots
exist only in the virgin season, so they appear as virgin-only markers,
never as a dev trend. Reads eda_summary.json (dev+virgin only; the
2026/2027 reserve season is excluded from every computation)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
S = json.load(open(HERE / "eda_summary.json"))
CH = HERE / "charts"
CH.mkdir(exist_ok=True)
seasons = S["seasons"]
labels = ["21/22", "22/23", "23/24", "24/25", "25/26\n(virgin)"]

# 1. levels by season: goals + event yellows for all seasons; virgin-only
# stats levels as single markers (they do not exist in dev).
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(labels, [S["levels"][s]["goals"] for s in seasons], marker="o", label="goals")
ax.plot(labels, [S["levels"][s]["yellows_event"] for s in seasons], marker="o", label="yellows (events)")
ax.plot([labels[-1]], [S["levels"][seasons[-1]]["sot"]], marker="s", label="SOT (virgin only)")
ax.plot([labels[-1]], [S["levels"][seasons[-1]]["corners"]], marker="s", label="corners (virgin only)")
ax.plot([labels[-1]], [S["levels"][seasons[-1]]["shots"]], marker="s", label="total shots (virgin only)")
ax.legend(fontsize=8)
ax.set_title("RS-SuperLiga levels per match by season (stats feed: virgin only)")
fig.tight_layout()
fig.savefig(CH / "levels_by_season.png", dpi=110)
plt.close(fig)

# 2. trait reliability: only goals (dev) and event yellows (dev, broken
# feed) are measurable on dev; every stats trait is null (no dev data).
fig, ax = plt.subplots(figsize=(8, 4))
tr = S["traits_dev"]
keys = ["goals_for", "yellows_event_for"]
vals = [tr[k]["r"] for k in keys]
ax.bar(["goals for\n(dev, n=23 teams)", "event yellows for\n(dev, YellowRed-only)"],
       vals)
ax.axhline(0, color="k", lw=0.8)
ax.set_ylim(0, 1.0)
for i, v in enumerate(vals):
    ax.text(i, v + 0.03, f"r = {v}", ha="center")
ax.set_title("Split-half trait reliability (r) — dev era only;\nSOT/corners/shots/possession/touches/fouls/saves: no dev data (null)")
fig.tight_layout()
fig.savefig(CH / "trait_reliability.png", dpi=110)
plt.close(fig)

# 3. halves constants: only the goals constant is measurable on dev.
# Yellows 1H is computed on the near-empty dev event feed (13 1H cards)
# and is NOT a usable constant; SOT/corners/shots splits are null in dev.
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(["goals 1H\n(events, dev, n=1087)",
        "yellows 1H\n(events, dev, n=101 — NOT usable)"],
       [S["halves_goals_dev_league_only"]["share"],
        S["halves_yellows_dev"]["share"]])
ax.set_ylim(0, 0.6)
ax.set_title("Halves shares (dev era) — SOT/corners/shots 1H: null (no dev splits)")
fig.tight_layout()
fig.savefig(CH / "halves_constants.png", dpi=110)
plt.close(fig)
print("charts done")
