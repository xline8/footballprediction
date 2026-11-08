"""Charts for LV-Virsliga EDA (from eda_summary.json / inventory_summary.json)."""
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
plt.ylabel("goals per match"); plt.title("LV-Virsliga goals level by season (dev)"); plt.tight_layout(); plt.savefig(out / "goals_levels_by_season.png"); plt.close()
rel = eda["split_half_reliability"]
labels = [k for k, v in rel.items() if v and v.get("r") is not None]; vals = [rel[k]["r"] for k in labels]
plt.figure(figsize=(9, 5)); plt.barh(labels, vals); plt.xlabel("split-half r"); plt.title("Trait reliability (dev era; count traits on 2025)"); plt.tight_layout(); plt.savefig(out / "trait_reliabilities.png"); plt.close()
inv_seasons = sorted(inv["seasons"])
stats = [inv["seasons"][s]["has_stats_all"] / inv["seasons"][s]["n"] for s in inv_seasons]
plt.figure(figsize=(7, 4)); plt.bar(inv_seasons, stats); plt.ylabel("stats coverage share"); plt.title("Stats-feed coverage by season (era map)"); plt.tight_layout(); plt.savefig(out / "stats_coverage_by_season.png"); plt.close()
hc = eda["halves_constants_2025"]
labels = list(hc); vals = [hc[k]["share_1h"] for k in labels]
plt.figure(figsize=(7, 4)); plt.bar(labels, vals); plt.ylabel("1H share of FT total"); plt.title("Halves constants (2025, frozen)"); plt.tight_layout(); plt.savefig(out / "halves_constants.png"); plt.close()
print("charts written", sorted(p.name for p in out.iterdir()))
