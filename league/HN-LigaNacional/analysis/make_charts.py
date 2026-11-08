#!/usr/bin/env python3
"""Render the descriptive chart set from eda_summary.json."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent; CHARTS = HERE / "charts"
def main():
    d = json.load(open(HERE / "eda_summary.json")); seasons = list(d["seasons"]); x = list(range(len(seasons))); CHARTS.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5)); ax.plot(x, [d["seasons"][s]["mean_total_goals"] for s in seasons], "o-", label="Total goals"); ax.plot(x, [d["seasons"][s]["card_events_per_match"] for s in seasons], "s-", label="Card events"); ax.set_xticks(x, seasons, rotation=30, ha="right"); ax.set_ylabel("Mean per regular-phase match"); ax.set_title("HN-LigaNacional levels by season"); ax.legend(); fig.tight_layout(); fig.savefig(CHARTS / "levels_by_season.png", dpi=160); plt.close(fig)
    vals = [d["trait_reliability"][k]["r"] or 0 for k in ("goals_for", "goals_against")]; fig, ax = plt.subplots(figsize=(7, 5)); ax.bar([0, 1], vals, color="#315f8c"); ax.set_ylim(-1, 1); ax.set_xticks([0, 1], ["Goals for", "Goals against"]); ax.set_ylabel("Split-half Pearson r"); ax.set_title("Career-pooled trait reliability"); fig.tight_layout(); fig.savefig(CHARTS / "trait_reliability.png", dpi=160); plt.close(fig)
    h = d["halves"]; fig, ax = plt.subplots(figsize=(9, 5)); labels = ["Observed", "Expected\nbinomial", "Excess\ntrue"]
    ax.bar(labels, [h["observed_share_variance"], h["expected_binomial_variance"], h["excess_true_variance"]], color=["#b77b4c", "#315f8c", "#6a994e"])
    ax.axhline(0, color="black", linewidth=.8); ax.set_ylabel("Variance of per-match 1H share"); ax.set_title(f"Halves constant FROZEN: {h['frozen_constant']:.4f} (p); true SD {h['true_sd_pp']:.2f}pp")
    ax.text(.02, .95, f"n={h['nonzero_goal_matches']}\nverdict={h['verdict']}", transform=ax.transAxes, va="top"); fig.tight_layout(); fig.savefig(CHARTS / "halves_constants.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10, 4)); ax.bar(x, [0]*len(x), color="#777"); ax.set_ylim(0, 100); ax.set_xticks(x, seasons, rotation=30, ha="right"); ax.set_ylabel("Named referee (%)"); ax.set_title("Referee coverage — 0% in every payload"); fig.tight_layout(); fig.savefig(CHARTS / "referee_coverage.png", dpi=160); plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.8)); axes[0].bar(["named\nreferee"], [0], color="#777"); axes[0].set_ylim(0, 1); axes[0].set_title("Referee coverage (0%)"); axes[1].bar(["territorial\nproxy"], [0], color="#90a4ae"); axes[1].set_ylim(0, 1); axes[1].set_title("No stats territory source"); fig.tight_layout(); fig.savefig(CHARTS / "referee_and_territory.png", dpi=160); plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4)); ax.text(.5, .5, "No Honduran sibling league\nX2 mover evidence = 0", ha="center", va="center", fontsize=14); ax.set_axis_off(); ax.set_title("Cross-tier mover evidence"); fig.tight_layout(); fig.savefig(CHARTS / "tier_gap.png", dpi=160); plt.close(fig)
    print(f"Wrote charts to {CHARTS}")
if __name__ == "__main__": main()
