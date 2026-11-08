"""Create Phase A descriptive charts; no models are fitted."""
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader((ROOT / "data/dk2_matches.csv").open()))
OUT = Path(__file__).resolve().parent / "charts"; OUT.mkdir(exist_ok=True)
seasons = sorted({r["season"] for r in rows})
means = [sum(int(r["home_goals"]) + int(r["away_goals"]) for r in rows if r["season"] == s) / sum(r["season"] == s for r in rows) for s in seasons]
fig, ax = plt.subplots(figsize=(10, 5.5)); ax.plot(seasons, means, marker="o", label="Goals")
ax.set_title("DK-2Division levels by season"); ax.set_ylabel("match total (both teams)"); ax.tick_params(axis="x", rotation=35); ax.grid(alpha=.25); ax.legend(); fig.tight_layout(); fig.savefig(OUT / "levels_by_season.png", dpi=160); plt.close(fig)

def corr(pairs):
    mx = sum(x for x, _ in pairs) / len(pairs); my = sum(y for _, y in pairs) / len(pairs)
    den = (sum((x - mx) ** 2 for x, _ in pairs) * sum((y - my) ** 2 for _, y in pairs)) ** .5
    return sum((x - mx) * (y - my) for x, y in pairs) / den
traits = defaultdict(lambda: [[], []])
for s in seasons[:5]:
    rr = sorted((r for r in rows if r["season"] == s), key=lambda r: (r["date"], r["match_id"]))
    for i, r in enumerate(rr):
        for side, opp in (("home", "away"), ("away", "home")):
            traits[(s, r[f"{side}_team_id"])][i % 2].append((int(r[f"{side}_goals"]), int(r[f"{opp}_goals"])))
attack = [(sum(x for x, _ in a)/len(a), sum(x for x, _ in b)/len(b)) for a, b in traits.values()]
defence = [(sum(y for _, y in a)/len(a), sum(y for _, y in b)/len(b)) for a, b in traits.values()]
fig, ax = plt.subplots(figsize=(7, 4.5)); ax.bar(["Attack", "Defence"], [corr(attack), corr(defence)], color="#3578a8"); ax.axhline(0, color="black", lw=.7); ax.set_ylim(-.2, 1); ax.set_ylabel("chronological split-half r"); ax.set_title("Team-trait reliability (descriptive)"); fig.tight_layout(); fig.savefig(OUT / "trait_reliability.png", dpi=160); plt.close(fig)
fig, ax = plt.subplots(figsize=(5.5, 4.5)); ax.bar(["Goals"], [0.4611], color="#c26d3c"); ax.axhline(.5, color="black", lw=.7, ls="--"); ax.set_ylim(0, .6); ax.set_ylabel("1H share"); ax.set_title("Frozen first-half constant"); ax.text(0, .473, "0.461", ha="center"); fig.tight_layout(); fig.savefig(OUT / "halves_constants.png", dpi=160); plt.close(fig)
print("created 3 charts")
