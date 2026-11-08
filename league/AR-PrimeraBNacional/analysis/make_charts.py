"""Generate Phase-A charts from the frozen EDA JSON."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
E = json.loads((HERE / "eda_summary.json").read_text())

def save(fig, name):
    fig.tight_layout(); fig.savefig(OUT / name, dpi=130); plt.close(fig)

ss = E["seasons"]
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(list(ss), [ss[s]["goals_per_match"] for s in ss], marker="o", label="goals")
card_seasons = [s for s in ss if ss[s]["yellows_per_match"] is not None]
ax.plot(card_seasons, [ss[s]["yellows_per_match"] for s in card_seasons], marker="s", label="yellow cards")
ax.axhline(2.55, color="grey", ls="--", lw=1, label="J1 goals 2.55")
ax.set_title("BNAC levels by season (EDA 2021–2025)"); ax.set_ylabel("per match"); ax.legend()
save(fig, "levels_by_season.png")

r = E["reliability"]
labels = ["goals for", "goals against", "yellows for", "yellows against"]
vals = [r["goals_for"]["r"], r["goals_against"]["r"], r["yellows_for_2023_2025"]["r"], r["yellows_against_2023_2025"]["r"]]
fig, ax = plt.subplots(figsize=(8, 4)); ax.barh(labels, vals, color=["#2e7d32" if v >= .4 else "#ef6c00" for v in vals])
ax.set_xlim(0, 1); ax.set_title("BNAC team-trait reliability, split-half r")
for i, v in enumerate(vals): ax.text(v + .02, i, f"{v:.2f}", va="center")
save(fig, "trait_reliability.png")

h = E["halves"]
labels = ["goals", "yellow cards"]
vals = [h["goals_2023_2025_complete_feed"]["share_1h"], h["yellows_2023_2025"]["share_1h"]]
fig, ax = plt.subplots(figsize=(7, 3.8)); ax.bar(labels, vals, color="#37474f"); ax.axhline(.5, color="grey", ls="--", lw=1)
ax.set_ylim(0, .6); ax.set_title("Frozen BNAC first-half shares (presentation only)")
for i, v in enumerate(vals): ax.text(i, v + .015, f"{v:.3f}", ha="center")
save(fig, "halves_constants.png")

ref = E["referees"]
fig, ax = plt.subplots(figsize=(5, 3.8)); v = ref["split_half_r"]["r"]
ax.bar(["referee\nsplit-half r"], [v], color="#2e7d32"); ax.set_ylim(0, 1); ax.set_title("Referee strictness (2023+ yellow era)"); ax.text(0, v + .03, f"{v:.2f}", ha="center")
save(fig, "referee_strictness.png")
print("charts written to", OUT)
