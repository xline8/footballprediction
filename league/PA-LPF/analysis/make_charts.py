"""Make the PA-LPF scores-only EDA charts from the generated CSV."""
import csv
import math
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
LEAGUE = os.path.dirname(BASE)
CSV = os.path.join(LEAGUE, "data", "pa_lpf_matches.csv")
CHARTS = os.path.join(BASE, "charts")
os.makedirs(CHARTS, exist_ok=True)
rows = [r for r in csv.DictReader(open(CSV)) if r["excluded_awarded"] != "True"]
for r in rows:
    for k in ("home_goals", "away_goals", "ht_home_goals", "ht_away_goals"):
        r[k] = int(r[k])
seasons = sorted({r["season"] for r in rows})

def corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((y - mb) ** 2 for y in b)
    return num / math.sqrt(va * vb) if va and vb else float("nan")

# Levels.
means, home, away = [], [], []
for s in seasons:
    q = [r for r in rows if r["season"] == s]
    means.append(sum(r["home_goals"] + r["away_goals"] for r in q) / len(q))
    home.append(sum(r["home_goals"] for r in q) / len(q))
    away.append(sum(r["away_goals"] for r in q) / len(q))
fig, ax = plt.subplots(figsize=(8, 4.5)); x = range(len(seasons))
ax.plot(x, means, "o-", label="Mean goals"); ax.plot(x, home, "o-", label="Home goals")
ax.plot(x, away, "o-", label="Away goals"); ax.set_xticks(list(x)); ax.set_xticklabels(seasons)
ax.set_ylabel("Goals per match"); ax.set_title("PA-LPF: levels by season"); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "levels_by_season.png"), dpi=120); plt.close(fig)

# GF/GA split-half reliability, deterministic and matching the EDA convention.
random.seed(7); reliabilities = {"GF": [], "GA": []}
for trait in ("GF", "GA"):
    for s in seasons:
        q = [r for r in rows if r["season"] == s]; teams = {}
        for r in q:
            if trait == "GF":
                teams.setdefault(r["home_team_id"], []).append(r["home_goals"])
                teams.setdefault(r["away_team_id"], []).append(r["away_goals"])
            else:
                teams.setdefault(r["home_team_id"], []).append(r["away_goals"])
                teams.setdefault(r["away_team_id"], []).append(r["home_goals"])
        a, b = [], []
        for vals in teams.values():
            if len(vals) < 10: continue
            random.shuffle(vals); h = len(vals) // 2
            a.append(sum(vals[:h]) / h); b.append(sum(vals[h:]) / (len(vals) - h))
        reliabilities[trait].append(corr(a, b))
fig, ax = plt.subplots(figsize=(8, 4.5)); ax.plot(x, reliabilities["GF"], "o-", label="GF")
ax.plot(x, reliabilities["GA"], "s-", label="GA"); ax.axhline(0, color="grey", lw=.8)
ax.set_xticks(list(x)); ax.set_xticklabels(seasons); ax.set_ylabel("Split-half r")
ax.set_title("PA-LPF: team-trait reliability"); ax.grid(alpha=.3); ax.legend()
fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "trait_reliability.png"), dpi=120); plt.close(fig)

# Frozen first-half constant.
shares = []
for s in seasons:
    q = [r for r in rows if r["season"] == s]
    shares.append(sum(r["ht_home_goals"] + r["ht_away_goals"] for r in q) /
                 sum(r["home_goals"] + r["away_goals"] for r in q))
frozen = sum(r["ht_home_goals"] + r["ht_away_goals"] for r in rows) / sum(r["home_goals"] + r["away_goals"] for r in rows)
fig, ax = plt.subplots(figsize=(8, 4.5)); ax.plot(x, shares, "o-", label="1H share")
ax.axhline(frozen, color="red", ls="--", label=f"Frozen {frozen:.4f}"); ax.set_xticks(list(x)); ax.set_xticklabels(seasons)
ax.set_ylabel("1H share of goals"); ax.set_ylim(.30, .60); ax.set_title("PA-LPF: frozen goals halves constant")
ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(os.path.join(CHARTS, "halves_constants.png"), dpi=120); plt.close(fig)

print("charts written to", CHARTS)
