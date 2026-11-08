"""Render SA-FirstDivision EDA charts (PNG) from eda_numbers.json + CSV.

Run: python3 league/SA-FirstDivision/analysis/make_charts.py
Output: league/SA-FirstDivision/analysis/charts/*.png
  reliability.png  — split-half r per trait (dev seasons)
  halves.png       — 1H shares with observed vs noise SD (2025/2026)
  distributions.png — per-match total histograms (dev seasons)

NOTE (2026-11-10): this script could not be executed in the builder's
exec sandbox (child processes cannot write file content there — see
the Phase B handoff). The SVG equivalents in charts/ were rendered by
hand from the same eda_numbers.json values and are the visual record
until this script is run in an unrestricted environment.
"""
import csv, json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
NUM = json.load(open(HERE / "eda_numbers.json"))
ROWS = list(csv.DictReader(open(HERE.parent / "data" / "safd_matches.csv")))
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)

# --- reliability ---
rel = [("Goals for (24/25)", NUM["reliability_goals_2024_25"]["goals_for"]),
       ("Goals against (24/25)", NUM["reliability_goals_2024_25"]["goals_against"])]
for k, v in NUM["reliability_count_2025_26"].items():
    rel.append((k.replace("_", " ") + " (25/26)", v))
names = [n for n, _ in rel]
vals = [v for _, v in rel]
colors = ["#b3402e" if v < 0.3 else "#2a7f62" for v in vals]
fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(names, vals, color=colors)
ax.set_xlim(0, 1)
ax.axvline(0.3, color="grey", linestyle="--", linewidth=1)
ax.set_xlabel("split-half r (odd/even per team, min 10 matches)")
ax.set_title("SA-FirstDivision team-trait reliabilities (dev seasons)")
for i, v in enumerate(vals):
    ax.text(v + 0.02, i, f"{v:.3f}", va="center", fontsize=9)
fig.tight_layout()
fig.savefig(OUT / "reliability.png", dpi=150)
plt.close(fig)

# --- halves: observed SD vs noise SD ---
hs = NUM["half_shares_2025_26"]
markets = ["sot", "corners", "shots", "yellows_events"]
labels = ["SOT (0.4540)", "Corners (0.4678)", "Total shots (0.4557)", "Event yellows (0.4010)"]
obs = [hs[m]["obs_sd"] for m in markets]
noise = [hs[m]["noise_sd"] for m in markets]
x = range(len(markets))
fig, ax = plt.subplots(figsize=(8, 4.5))
w = 0.35
ax.bar([i - w / 2 for i in x], obs, w, label="observed SD", color="#2a7f62")
ax.bar([i + w / 2 for i in x], noise, w, label="binomial noise SD", color="#9aa5a1")
ax.set_xticks(list(x))
ax.set_xticklabels(labels)
ax.set_ylabel("SD of per-match 1H share")
ax.set_title("Halves constants 2025/2026: observed SD ≈ noise SD (true SD ≈ 0)")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "halves.png", dpi=150)
plt.close(fig)

# --- distributions (dev seasons) ---
g24 = [int(r["home_goals"]) + int(r["away_goals"]) for r in ROWS
       if r["season"] == "2024/2025" and r["phase"] == "regular" and r["awarded"] == "0"]
d25 = [r for r in ROWS if r["season"] == "2025/2026" and r["phase"] == "regular" and r["awarded"] == "0"]
def tot(r, k):
    return float(r[k + "_home"]) + float(r[k + "_away"])
panels = [("Goals 2024/25", g24, range(0, 10)),
          ("SOT 2025/26", [tot(r, "ShotsOnTarget") for r in d25], range(1, 19)),
          ("Corners 2025/26", [tot(r, "corners") for r in d25], range(2, 20)),
          ("Total shots 2025/26", [tot(r, "total_shots") for r in d25], range(9, 42)),
          ("Event yellows 2025/26", [float(r["yellow_home"]) + float(r["yellow_away"]) for r in d25], range(0, 11))]
fig, axes = plt.subplots(2, 3, figsize=(12, 7))
axes = axes.ravel()
for ax, (title, vals, bins) in zip(axes, panels):
    ax.hist(vals, bins=[b - 0.5 for b in bins] + [max(bins) + 0.5], color="#2a7f62")
    ax.set_title(title)
    ax.set_xlabel("total per match")
    ax.set_ylabel("matches")
axes[-1].axis("off")
fig.tight_layout()
fig.savefig(OUT / "distributions.png", dpi=150)
plt.close(fig)
print("wrote", sorted(p.name for p in OUT.glob("*.png")))
