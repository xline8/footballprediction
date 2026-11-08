"""Charts for MX-ExpansionMX EDA: levels by block, trait reliabilities,
halves constants. Mirrors the J1/CL chart set. Run: python3 make_charts.py
(writes PNGs into analysis/charts/)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
eda = json.loads((HERE / "eda_summary.json").read_text())
out = HERE / "charts"
out.mkdir(exist_ok=True)
blocks = list(eda["levels_by_block"])
short = [b.replace("20", "").replace(" - ", " ") for b in blocks]

fig, ax = plt.subplots(1, 3, figsize=(13, 3.6))
ax[0].plot(short, [eda["levels_by_block"][b]["goals_per_match"] for b in blocks], marker="o")
ax[0].set_title("Goals per match"); ax[0].tick_params(labelrotation=45, labelsize=7)
ax[1].plot(short, [eda["levels_by_block"][b]["home_win_rate"] for b in blocks], marker="o")
ax[1].set_title("Home win rate"); ax[1].tick_params(labelrotation=45, labelsize=7)
yv = [eda["levels_by_block"][b].get("yellows_per_match") for b in blocks]
ax[2].plot(short, [y if y else float("nan") for y in yv], marker="o")
ax[2].set_title("Yellows per match (clean era from 2023/2024 A)"); ax[2].tick_params(labelrotation=45, labelsize=7)
fig.tight_layout(); fig.savefig(out / "levels_by_season.png", dpi=110); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 3.4))
labels = ["Goals for", "Goals against", "Yellows for", "Yellows against"]
vals = [eda["reliability_goals"]["for"]["r"], eda["reliability_goals"]["against"]["r"],
        eda["reliability_yellows_cards_era"]["for"]["r"], eda["reliability_yellows_cards_era"]["against"]["r"]]
ax.bar(labels, vals); ax.set_ylim(0, 1); ax.set_title("Split-half trait reliability (r)")
fig.tight_layout(); fig.savefig(out / "trait_reliability.png", dpi=110); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.5, 3.4))
ax.bar(["Goals 1H share", "Yellows 1H share"],
       [eda["halves"]["goals_1h_share"], eda["halves"]["yellow_1h_share"]])
ax.set_ylim(0, 0.6); ax.set_title("Frozen halves constants (true variance: goals 0.0)")
fig.tight_layout(); fig.savefig(out / "halves_constants.png", dpi=110); plt.close(fig)
print("charts written to", out)
