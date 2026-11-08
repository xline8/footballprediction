"""LU-NationalDivision charts: same set as league/J1/analysis/charts/.

Reads league/LU-NationalDivision/data/lu_matches.csv, writes PNGs to
analysis/charts/. Run: python3 make_charts.py
"""
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "data" / "lu_matches.csv"
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)

rows = list(csv.DictReader(open(CSV)))
for r in rows:
    r["hg"] = int(r["home_goals"])
    r["ag"] = int(r["away_goals"])
    r["g1"] = int(r["goals_1h_home"]) + int(r["goals_1h_away"]) if r["goals_1h_home"] else None
    r["g2"] = int(r["goals_2h_home"]) + int(r["goals_2h_away"]) if r["goals_2h_home"] else None

seasons = sorted({r["season"] for r in rows})
short = {s: s.replace("20", "", 1).replace("/", "-") for s in seasons}


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sx = sum((x - mx) ** 2 for x in xs)
    sy = sum((y - my) ** 2 for y in ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sx * sy)


# 1. levels by season
fig, ax = plt.subplots(figsize=(8, 4.5))
tot, hw, ou25 = [], [], []
for s in seasons:
    rs = [r for r in rows if r["season"] == s]
    n = len(rs)
    tot.append(sum(r["hg"] + r["ag"] for r in rs) / n)
    hw.append(sum(1 for r in rs if r["hg"] > r["ag"]) / n)
    ou25.append(sum(1 for r in rs if r["hg"] + r["ag"] > 2.5) / n)
x = range(len(seasons))
ax.plot(x, tot, "o-", label="goals/match")
ax.plot(x, ou25, "s-", label="OU2.5 over-rate")
ax.plot(x, hw, "^-", label="home-win rate")
ax.set_xticks(list(x))
ax.set_xticklabels([short[s] for s in seasons])
ax.set_ylim(0, 4)
ax.set_title("LU-NationalDivision: levels by season (2026/27 partial)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "levels_by_season.png", dpi=120)
plt.close(fig)

# 2. coverage by season (what exists in the feed)
fig, ax = plt.subplots(figsize=(8, 4.5))
cov = {"score": [], "goal events": [], "stats feed": [], "shotmap": [], "referee named": []}
for s in seasons:
    rs = [r for r in rows if r["season"] == s]
    n = len(rs)
    cov["score"].append(100.0)
    cov["goal events"].append(100 * sum(1 for r in rs if r["has_events"] == "True") / n)
    cov["stats feed"].append(0.0)
    cov["shotmap"].append(0.0)
    cov["referee named"].append(0.0)
x = range(len(seasons))
for k, v in cov.items():
    ax.plot(x, v, "o-", label=k)
ax.set_xticks(list(x))
ax.set_xticklabels([short[s] for s in seasons])
ax.set_ylim(-5, 105)
ax.set_ylabel("% of matches")
ax.set_title("LU-NationalDivision: field coverage by season (scores-only league)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "coverage_by_season.png", dpi=120)
plt.close(fig)

# 3. trait reliability (split-half by team-season)
def split_half(season_list):
    gf1, gf2, ga1, ga2 = [], [], [], []
    for s in season_list:
        rs = sorted([r for r in rows if r["season"] == s], key=lambda r: (r["date"], r["match_id"]))
        tf, ta = defaultdict(list), defaultdict(list)
        for r in rs:
            tf[r["home_id"]].append(r["hg"])
            ta[r["home_id"]].append(r["ag"])
            tf[r["away_id"]].append(r["ag"])
            ta[r["away_id"]].append(r["hg"])
        for t in tf:
            f, a = tf[t], ta[t]
            h = len(f) // 2
            if h >= 5:
                gf1.append(sum(f[:h]) / h)
                gf2.append(sum(f[h:]) / (len(f) - h))
                ga1.append(sum(a[:h]) / h)
                ga2.append(sum(a[h:]) / (len(a) - h))
    return pearson(gf1, gf2), pearson(ga1, ga2), len(gf1)

r_dev = split_half(["2021/2022", "2022/2023", "2023/2024", "2024/2025"])
r_sc = split_half(["2022/2023", "2023/2024", "2024/2025"])
fig, ax = plt.subplots(figsize=(8, 4.5))
labels = ["GF dev-era\n(n=64)", "GA dev-era\n(n=64)", "GF scored\n(n=48)", "GA scored\n(n=48)"]
vals = [r_dev[0], r_dev[1], r_sc[0], r_sc[1]]
ax.bar(labels, vals, color=["#2c7bb6", "#d7191c", "#2c7bb6", "#d7191c"])
ax.set_ylim(0, 1)
ax.set_ylabel("split-half r")
ax.set_title("LU-NationalDivision: team trait reliability (goals)")
for i, v in enumerate(vals):
    ax.text(i, v + 0.03, f"{v:.3f}", ha="center")
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "trait_reliability.png", dpi=120)
plt.close(fig)

# 4. halves constants (1H share of goals by season)
fig, ax = plt.subplots(figsize=(8, 4.5))
shares, ses, ns = [], [], []
for s in seasons:
    rs = [r for r in rows if r["season"] == s and r["g1"] is not None]
    g1 = sum(r["g1"] for r in rs)
    g2 = sum(r["g2"] for r in rs)
    n = g1 + g2
    p = g1 / n
    shares.append(p)
    ses.append(math.sqrt(p * (1 - p) / n))
    ns.append(n)
x = range(len(seasons))
ax.errorbar(x, shares, yerr=ses, fmt="o-", capsize=4, label="1H share ± 1 SE")
ax.axhline(0.4294, color="red", linestyle="--", label="frozen constant 0.4294 (dev scored)")
ax.set_xticks(list(x))
ax.set_xticklabels([f"{short[s]}\n(n={n})" for s, n in zip(seasons, ns)])
ax.set_ylim(0.30, 0.55)
ax.set_ylabel("1H share of goals")
ax.set_title("LU-NationalDivision: goals 1H share by season")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUT / "halves_constants.png", dpi=120)
plt.close(fig)

print("charts written:", sorted(p.name for p in OUT.glob("*.png")))
print("split-half dev-era GF/GA:", round(r_dev[0], 3), round(r_dev[1], 3))
print("split-half scored GF/GA:", round(r_sc[0], 3), round(r_sc[1], 3))
