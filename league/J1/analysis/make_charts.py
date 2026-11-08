"""Step 4 (visualization) backfill for the J.League exploration.

Generates the standard chart set for league/J1/analysis/charts/ from the
frozen EDA numbers (eda_summary.json + cards_halves_summary.json, computed
in Phase 3). No new statistics are computed here — this script only plots
what EDA.md reports, so the charts can never drift from the findings.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
OUT = HERE / "charts"
OUT.mkdir(exist_ok=True)
eda = json.loads((HERE / "eda_summary.json").read_text())
cards = json.loads((HERE / "cards_halves_summary.json").read_text())


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=130)
    plt.close(fig)
    print("wrote", name)


# 1 — League levels by season: goals per match, J1/J2/J3 (EDA F1)
fig, ax = plt.subplots(figsize=(8, 4.2))
for lg, marker in (("j1", "o"), ("j2", "s"), ("j3", "^")):
    ss = eda["seasons"][lg]
    xs = list(ss.keys())
    ax.plot(xs, [ss[s]["goals"] for s in xs], marker=marker, label=lg.upper())
ax.axhline(2.84, color="grey", ls="--", lw=1, label="Top-5 spine mean (2.84)")
ax.set_title("Goals per match by season — J1 / J2 / J3 (EDA F1)")
ax.set_ylabel("goals / match")
ax.legend()
save(fig, "levels_by_season.png")

# 2 — Trait reliability: split-half r of J1 team traits (EDA F2/F5/F6)
rel = eda["reliability"]["j1"]
ratio = eda["reliability"]["j1_ratio_traits"]
traits = [
    ("shots for", rel["shots_for"]["r"]), ("xG for", rel["xg_for"]["r"]),
    ("SOT for", rel["sot_for"]["r"]), ("goals for", rel["goals_for"]["r"]),
    ("yellows for", rel["yellow_for"]["r"]), ("corners for", rel["corners_for"]["r"]),
    ("set-play xG share", ratio["setplay_xg_share"]["r"]),
    ("xG / shot", ratio["xg_per_shot"]["r"]),
    ("finishing (G - xG)", ratio["finishing_goals_minus_xg"]["r"]),
    ("on-target rate", ratio["sot_rate"]["r"]),
]
labels = [t[0] for t in traits][::-1]
vals = [t[1] for t in traits][::-1]
colors = ["#2e7d32" if v >= 0.4 else ("#ef6c00" if v >= 0.3 else "#c62828") for v in vals]
fig, ax = plt.subplots(figsize=(8, 4.6))
ax.barh(labels, vals, color=colors)
ax.axvline(0.3, color="grey", ls="--", lw=1)
ax.set_xlim(0, 1)
ax.set_title("J1 team-trait reliability, split-half r (EDA F2/F5/F6)\nred < 0.3 = noise zone")
for i, v in enumerate(vals):
    ax.text(v + 0.02, i, f"{v:.2f}", va="center")
save(fig, "trait_reliability.png")

# 3 — Cross-tier gap: movers' GF / GA before vs after the step (EDA F4)
ct = eda["cross_tier"]
fig, axes = plt.subplots(1, 2, figsize=(9, 4.2), sharey=True)
for ax, key, title in ((axes[0], "j2->j1", "J2 -> J1"), (axes[1], "j3->j2", "J3 -> J2")):
    for i, (grp, c) in enumerate((("promoted", "#1565c0"), ("relegated", "#ad1457"))):
        g = ct[key][grp]
        x = [i * 3, i * 3 + 1]
        ax.bar([x[0]], [g["gf_before"]], color=c, alpha=0.45)
        ax.bar([x[0] + 0.0], [g["gf_after"]], color=c)
        ax.bar([x[1]], [g["ga_before"]], color=c, alpha=0.45)
        ax.bar([x[1]], [g["ga_after"]], color=c)
    ax.set_xticks([0, 1, 3, 4])
    ax.set_xticklabels(["GF\nbefore", "GA\nbefore", "GF", "GA"])
    ax.set_title(f"{title} movers (solid = after, faded = before)")
axes[0].set_ylabel("goals / match")
fig.suptitle("Cross-tier gap ≈ 0.5 goals/match, symmetric (EDA F4)")
save(fig, "tier_gap.png")

# 4 — Frozen halves constants for J1 (EDA F3 + F14)
h = eda["halves_j1"]
card_share = cards.get("frozen_constant_1h_share", 0.383)
names = ["goals", "SOT", "corners", "total shots", "yellow cards"]
shares = [h["goal_share_1h"]["mean"], h["sot_share_1h_mean"],
          h["corner_share_1h_mean"], h["shots_share_1h_mean"], card_share]
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.bar(names, shares, color="#37474f")
ax.axhline(0.5, color="grey", ls="--", lw=1)
ax.set_ylim(0, 0.6)
ax.set_title("J1 frozen first-half shares — the ONLY halves mechanism (EDA F3/F14)\nper-match true variance of the share measured at zero for all five stats")
for i, v in enumerate(shares):
    ax.text(i, v + 0.015, f"{v:.3f}", ha="center")
save(fig, "halves_constants.png")

# 5 — Referee strictness + territorial proxy (EDA F8/F9) as a small panel
fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
axes[0].bar(["referee card-rate\nsplit-half r"], [eda["referees"]["card_rate_split_half"]["r"]], color="#2e7d32")
axes[0].set_ylim(0, 1)
axes[0].set_title("Referee strictness is a trait (EDA F8)")
ct2 = eda["corners_territorial_j1"]
axes[1].bar(["opp-box touches", "possession"],
            [ct2["corr_corners_boxtouches"], ct2["corr_corners_possession"]],
            color=["#2e7d32", "#90a4ae"])
axes[1].set_ylim(0, 0.6)
axes[1].set_title("Per-match corr with team corners (EDA F9)")
save(fig, "referee_and_territory.png")
print("charts done ->", OUT)
