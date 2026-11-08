"""Charts for MA-BotolaPro EDA (from eda_summary.json / inventory)."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = Path(__file__).resolve().parent
eda = json.loads((HERE / "eda_summary.json").read_text())
inv = json.loads((HERE / "inventory_summary.json").read_text())
out = HERE / "charts"; out.mkdir(exist_ok=True)
seasons = list(eda["goals_levels"])
plt.figure(figsize=(7, 4)); plt.bar(seasons, [eda["goals_levels"][s]["goals_per_match"] for s in seasons])
plt.ylabel("goals per match"); plt.title("MA-BotolaPro goals level by season (dev)"); plt.tight_layout(); plt.savefig(out / "goals_levels_by_season.png"); plt.close()
rel = eda["split_half_reliability"]
labels = [k for k, v in rel.items() if v]; vals = [rel[k]["r"] for k in labels]
plt.figure(figsize=(8, 4)); plt.barh(labels, vals); plt.xlabel("split-half r"); plt.title("Trait reliability (dev era)"); plt.tight_layout(); plt.savefig(out / "trait_reliabilities.png"); plt.close()
labels2 = list(inv); stats = [inv[s]["stats_all"] / inv[s]["n"] for s in labels2]
plt.figure(figsize=(7, 4)); plt.bar(labels2, stats); plt.ylabel("stats coverage share"); plt.title("Stats-feed coverage by season (era map)"); plt.tight_layout(); plt.savefig(out / "stats_coverage_by_season.png"); plt.close()
print("charts written", sorted(p.name for p in out.iterdir()))
