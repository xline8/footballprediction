import csv, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader((HERE.parent / "data" / "ua_matches.csv").open()))
eda = json.loads((HERE / "eda_numbers.json").read_text())
seasons = sorted(eda["seasons"])
fig, ax = plt.subplots(figsize=(8, 4))
for key, lab in (("goals_pg", "goals"), ("sot_pg", "SOT"), ("corners_pg", "corners")):
    ax.plot(seasons, [eda["seasons"][s].get(key) for s in seasons], marker="o", label=lab)
ax.legend(); ax.set_title("UA Premier League — levels by season"); fig.tight_layout(); fig.savefig(HERE / "charts" / "levels_by_season.png", dpi=110)
rel = eda["reliability"]["dev_block_2022_2025"]
fig, ax = plt.subplots(figsize=(8, 4))
traits = ["goals", "sot", "corners", "shots", "yellow_events"]
ax.bar([t + " for" for t in traits], [rel[t]["for_r"] for t in traits]); ax.bar([t + " ag" for t in traits], [rel[t]["against_r"] for t in traits])
ax.set_title("Split-half trait reliability (dev block 2022/23–2024/25)"); fig.tight_layout(); fig.savefig(HERE / "charts" / "trait_reliability.png", dpi=110)
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(["goals 1H share", "cards 1H share"], [0.4441, 0.3290]); ax.set_title("Frozen halves constants (event times, dev era)"); fig.tight_layout(); fig.savefig(HERE / "charts" / "halves_constants.png", dpi=110)
print("charts done")
