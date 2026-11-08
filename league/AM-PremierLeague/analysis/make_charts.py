"""Charts for AM-PremierLeague EDA (same set as J1, adapted to a
scores-only league): levels by season, trait reliability, halves
constant. Reads league/AM-PremierLeague/data/am_matches.csv.
Usage: python3 league/AM-PremierLeague/analysis/make_charts.py
"""
import csv
import json
import math
import os
import random
import statistics

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
LEAGUE = os.path.dirname(BASE)
CSV = os.path.join(LEAGUE, "data", "am_matches.csv")
CHARTS = os.path.join(BASE, "charts")
os.makedirs(CHARTS, exist_ok=True)

rows = list(csv.DictReader(open(CSV)))
rows = [r for r in rows if r["awarded"] != "True"]  # regular season only
for r in rows:
    r["hg"] = int(r["home_goals"])
    r["ag"] = int(r["away_goals"])
    r["awarded"] = r["awarded"] == "True"
    r["ht_hg"] = int(r["ht_home_goals"]) if r["ht_home_goals"] != "" else None
    r["ht_ag"] = int(r["ht_away_goals"]) if r["ht_away_goals"] != "" else None

seasons = sorted(set(r["season"] for r in rows))
SEASONS = seasons  # noqa: F841


def corr(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    vx = sum((a - mx) ** 2 for a in xs)
    vy = sum((b - my) ** 2 for b in ys)
    return cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else float("nan")


# --- 1. levels by season -------------------------------------------------
means, homes, aways, hw, ou = [], [], [], [], []
for s in seasons:
    sub = [r for r in rows if r["season"] == s]
    n = len(sub)
    means.append(sum(r["hg"] + r["ag"] for r in sub) / n)
    homes.append(sum(r["hg"] for r in sub) / n)
    aways.append(sum(r["ag"] for r in sub) / n)
    hw.append(sum(1 for r in sub if r["hg"] > r["ag"]) / n)
    ou.append(sum(1 for r in sub if r["hg"] + r["ag"] >= 3) / n)
fig, ax = plt.subplots(figsize=(8, 4.5))
x = range(len(seasons))
ax.plot(x, means, marker="o", label="Mean goals")
ax.plot(x, homes, marker="o", label="Home goals")
ax.plot(x, aways, marker="o", label="Away goals")
ax.set_xticks(list(x))
ax.set_xticklabels([s.replace("/", "/\n") for s in seasons])
ax.set_ylabel("Goals per match")
ax.set_title("AM-PremierLeague: levels by season")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "levels_by_season.png"), dpi=120)
plt.close(fig)

# --- 2. trait reliability (split-half GF/GA per season) -------------------
# Trait-major loop order (GF all seasons, then GA) — matches EDA.md.
random.seed(7)
gf_r, ga_r = [], []
for trait, acc in (("GF", gf_r), ("GA", ga_r)):
    for s in seasons:
        sub = [r for r in rows if r["season"] == s]
        teams = {}
        for r in sub:
            teams.setdefault(r["home_team_id"], []).append(
                r["hg"] if trait == "GF" else r["ag"])
            teams.setdefault(r["away_team_id"], []).append(
                r["ag"] if trait == "GF" else r["hg"])
        A, B = [], []
        for vals in teams.values():
            if len(vals) < 10:
                continue
            v = vals[:]
            random.shuffle(v)
            h = len(v) // 2
            A.append(sum(v[:h]) / h)
            B.append(sum(v[h:]) / (len(v) - h))
        acc.append(corr(A, B))
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(x, gf_r, marker="o", label="Goals-for split-half r")
ax.plot(x, ga_r, marker="s", label="Goals-against split-half r")
ax.axhline(0, color="grey", lw=0.8)
ax.set_xticks(list(x))
ax.set_xticklabels([s.replace("/", "/\n") for s in seasons])
ax.set_ylabel("Split-half correlation")
ax.set_title("AM-PremierLeague: team-trait reliability by season")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "trait_reliability.png"), dpi=120)
plt.close(fig)

# --- 3. halves constant ----------------------------------------------------
shares = []
for s in seasons:
    sub = [r for r in rows if r["season"] == s and r["ht_hg"] is not None]
    h1 = sum(r["ht_hg"] + r["ht_ag"] for r in sub)
    ft = sum(r["hg"] + r["ag"] for r in sub)
    shares.append(h1 / ft if ft else float("nan"))
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(x, shares, marker="o", label="1H share of goals")
ax.axhline(0.4335, color="red", ls="--", label="Frozen constant 0.4335")
ax.set_xticks(list(x))
ax.set_xticklabels([s.replace("/", "/\n") for s in seasons])
ax.set_ylabel("1H share")
ax.set_ylim(0.30, 0.55)
ax.set_title("AM-PremierLeague: goals 1H share by season (frozen constant)")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "halves_constants.png"), dpi=120)
plt.close(fig)

# --- 4. tier gap -----------------------------------------------------------
teams = {}
for r in rows:
    if r["season"] == "2026/2027":
        continue
    for tid, gf, ga in ((r["home_team_id"], r["hg"], r["ag"]),
                        (r["away_team_id"], r["ag"], r["hg"])):
        t = teams.setdefault(tid, [0, 0, 0, r["home_team"] if tid == r["home_team_id"] else r["away_team"]])
        t[0] += 1
        t[1] += gf
        t[2] += ga
order = sorted(teams.items(), key=lambda kv: -(kv[1][1] - kv[1][2]) / kv[1][0])
names = [v[3] for _, v in order]
diffs = [(v[1] - v[2]) / v[0] for _, v in order]
fig, ax = plt.subplots(figsize=(8, 5.5))
ax.barh(names[::-1], diffs[::-1])
ax.axvline(0, color="black", lw=0.8)
ax.set_xlabel("GF minus GA per match (complete seasons)")
ax.set_title("AM-PremierLeague: team tiers")
fig.tight_layout()
fig.savefig(os.path.join(CHARTS, "tier_gap.png"), dpi=120)
plt.close(fig)

print("charts written to", CHARTS)
print("levels:", [round(m, 3) for m in means])
print("GF split-half r:", [round(v, 3) for v in gf_r])
print("GA split-half r:", [round(v, 3) for v in ga_r])
print("1H shares:", [round(v, 4) for v in shares])
