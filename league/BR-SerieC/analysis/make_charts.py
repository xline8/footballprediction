"""Render BR-SerieC EDA charts from the committed analysis CSVs."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "brc_matches.csv"
OUT = HERE / "charts"; OUT.mkdir(exist_ok=True)
seasons = ["2021", "2022", "2023", "2024", "2025", "2026"]
with DATA.open() as f: rows = list(csv.DictReader(f))
def ns(s): return [r for r in rows if r["season"] == s]
levels = [sum(int(r["home_goals"])+int(r["away_goals"]) for r in ns(s))/len(ns(s)) for s in seasons]
fig, ax = plt.subplots(figsize=(8,4.5)); ax.bar(seasons, levels, color="#37474f"); ax.set_title("BR-SerieC goals per match"); ax.set_ylabel("goals"); fig.tight_layout(); fig.savefig(OUT/"levels_by_season.png", dpi=130); plt.close(fig)
traits = {"goals-for": .411, "goals-against": .143}
fig, ax = plt.subplots(figsize=(7,3.5)); ax.barh(list(traits), list(traits.values()), color="#2e7d32"); ax.axvline(.3,color="grey",ls="--"); ax.set_xlim(-.05,.5); ax.set_title("BR-SerieC trait split-half reliability (60 splits)"); fig.tight_layout(); fig.savefig(OUT/"trait_reliability.png",dpi=130); plt.close(fig)
fig, ax = plt.subplots(figsize=(5,3.5)); ax.bar(["goals"],[.4426],color="#37474f"); ax.axhline(.5,color="grey",ls="--"); ax.set_ylim(0,.6); ax.text(0,.457,".443",ha="center"); ax.set_title("Frozen first-half goal share"); fig.tight_layout(); fig.savefig(OUT/"halves_constants.png",dpi=130); plt.close(fig)
print("charts written", sorted(p.name for p in OUT.glob("*.png")))
