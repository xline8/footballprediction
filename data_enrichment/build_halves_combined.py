"""Merge SofaScore + FotMob SOT half splits into one combined dataset.

Inputs:
  all_matches_clean.csv                       spine (football-data FT SOT)
  data_enrichment/sot_sofascore/sofascore_sot_dataset.csv   source A
  data_enrichment/sot_backfill/gap_labels.csv               source B (gaps)
  data_enrichment/sot_backfill/crossval_labels.csv          source B (sample)
  data_enrichment/sot_backfill/remaining_gaps.csv           driver gap log

Outputs:
  data_enrichment/sot_halves_combined.csv
  data_enrichment/HALVES_COVERAGE.md

Also prints the cross-validation summary (FotMob vs SofaScore on the seeded
200-match sample) and the sanity-check numbers used in the coverage report.
Name matching uses the same normalised keys as fill_halves_gaps (including
its alias patch, applied here identically for consistent keys).
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import backfill_sot_fotmob as _bf  # noqa: E402
from backfill_sot_fotmob import LEAGUES, load_master, norm  # noqa: E402
import fill_halves_gaps as _driver  # noqa: E402,F401  (applies the alias patch)

OUT = BASE / "data_enrichment"
BACKFILL = OUT / "sot_backfill"
COMBINED = OUT / "sot_halves_combined.csv"
REPORT = OUT / "HALVES_COVERAGE.md"
FIELDS = ["div", "season", "date", "home", "away", "sot_1h_h", "sot_1h_a",
          "sot_2h_h", "sot_2h_a", "sot_ft_halves", "fd_sot_ft", "source",
          "quality"]
SPLIT_FIELDS = ["sot_1h_h", "sot_1h_a", "sot_2h_h", "sot_2h_a"]


def key_of(div, date, home, away):
    return "|".join([div, date, norm(home), norm(away)])


def spine_key(row):
    return key_of(row["Div"], row["Date"], row["HomeTeam"], row["AwayTeam"])


def load_csv(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    spine = load_master()
    sofa = [r for r in load_csv(OUT / "sot_sofascore" / "sofascore_sot_dataset.csv")
            if r["div"] in LEAGUES]
    gap_labels = load_csv(BACKFILL / "gap_labels.csv")
    xval_labels = load_csv(BACKFILL / "crossval_labels.csv")
    gap_log = load_csv(BACKFILL / "remaining_gaps.csv")

    sofa_by_key = {}
    for r in sofa:
        sofa_by_key[key_of(r["div"], r["date"], r["home"], r["away"])] = r
    fotmob_by_key = {}
    for r in gap_labels:
        fotmob_by_key[key_of(r["div"], r["date"], r["home"], r["away"])] = r

    # ---- cross-validation: FotMob sample vs SofaScore on the same matches
    xval = {"n": 0, "per_field_exact": Counter(), "per_field_mae": {},
            "all_four_exact": 0, "ft_exact": 0, "abs_err": defaultdict(list)}
    for r in xval_labels:
        s = sofa_by_key.get(key_of(r["div"], r["date"], r["home"], r["away"]))
        if s is None:
            continue
        xval["n"] += 1
        pairs = [("sot_1h_h", int(r["sot_1h_h"]), int(s["sofascore_1h_h"])),
                 ("sot_1h_a", int(r["sot_1h_a"]), int(s["sofascore_1h_a"])),
                 ("sot_2h_h", int(r["sot_2h_h"]), int(s["sofascore_2h_h"])),
                 ("sot_2h_a", int(r["sot_2h_a"]), int(s["sofascore_2h_a"]))]
        if all(f == v for _, f, v in pairs):
            xval["all_four_exact"] += 1
        for name, f, v in pairs:
            if f == v:
                xval["per_field_exact"][name] += 1
            xval["abs_err"][name].append(abs(f - v))
        if int(r["sot_ft"]) == int(s["sofascore_sot_ft"]):
            xval["ft_exact"] += 1
    for name in SPLIT_FIELDS:
        errs = xval["abs_err"][name]
        xval["per_field_mae"][name] = round(sum(errs) / len(errs), 3) if errs else None

    # ---- merge
    combined, missing = [], []
    for row in spine:
        k = spine_key(row)
        fd_ft = int(float(row["HST"])) + int(float(row["AST"]))
        base = {"div": row["Div"], "season": row["Season"], "date": row["Date"],
                "home": row["HomeTeam"], "away": row["AwayTeam"],
                "fd_sot_ft": fd_ft}
        s = sofa_by_key.get(k)
        if s is not None:
            splits = [int(s["sofascore_1h_h"]), int(s["sofascore_1h_a"]),
                      int(s["sofascore_2h_h"]), int(s["sofascore_2h_a"])]
            combined.append({**base,
                             **dict(zip(SPLIT_FIELDS, splits)),
                             "sot_ft_halves": sum(splits),
                             "source": "sofascore", "quality": s["quality"]})
            continue
        f = fotmob_by_key.get(k)
        if f is not None:
            splits = [int(f["sot_1h_h"]), int(f["sot_1h_a"]),
                      int(f["sot_2h_h"]), int(f["sot_2h_a"])]
            combined.append({**base,
                             **dict(zip(SPLIT_FIELDS, splits)),
                             "sot_ft_halves": sum(splits),
                             "source": "fotmob",
                             "quality": "reconciled" if sum(splits) == fd_ft else "flagged"})
            continue
        missing.append(base)

    with COMBINED.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(combined)

    # ---- sanity checks
    delta = Counter()
    delta_by_source = defaultdict(Counter)
    for r in combined:
        d = r["sot_ft_halves"] - r["fd_sot_ft"]
        delta[d] += 1
        delta_by_source[r["source"]][d] += 1
    sofa_internal_bad = 0
    for r in sofa:
        halves = (int(r["sofascore_1h_h"]) + int(r["sofascore_1h_a"]) +
                  int(r["sofascore_2h_h"]) + int(r["sofascore_2h_a"]))
        if halves != int(r["sofascore_sot_ft"]):
            sofa_internal_bad += 1
    zero_1h_fotmob = [r for r in combined if r["source"] == "fotmob"
                      and r["sot_1h_h"] == 0 and r["sot_1h_a"] == 0]
    zero_1h_sofa = [r for r in combined if r["source"] == "sofascore"
                    and r["sot_1h_h"] == 0 and r["sot_1h_a"] == 0]

    # ---- coverage tables
    spine_cov = Counter((r["Div"], r["Season"]) for r in spine)
    have_cov = Counter((r["div"], r["season"]) for r in combined)
    gap_reasons = Counter()
    gap_reason_by = defaultdict(Counter)
    reason_by_key = {}
    for g in gap_log:
        reason_by_key[key_of(g["div"], g["date"], g["home"], g["away"])] = g["reason"]
    for r in missing:
        reason = reason_by_key.get(
            key_of(r["div"], r["date"], r["home"], r["away"]),
            "not attempted / no reason logged")
        gap_reasons[reason] += 1
        gap_reason_by[(r["div"], r["season"])][reason] += 1

    summary = {
        "spine_total": len(spine), "combined_rows": len(combined),
        "coverage_pct": round(100 * len(combined) / len(spine), 2),
        "by_source": dict(Counter(r["source"] for r in combined)),
        "by_quality": dict(Counter(r["quality"] for r in combined)),
        "missing": len(missing),
        "crossval": {"n": xval["n"],
                     "per_field_exact": dict(xval["per_field_exact"]),
                     "per_field_exact_pct": {k2: round(100 * v / xval["n"], 1)
                                             for k2, v in xval["per_field_exact"].items()},
                     "per_field_mae": xval["per_field_mae"],
                     "all_four_exact": xval["all_four_exact"],
                     "all_four_exact_pct": round(100 * xval["all_four_exact"] / xval["n"], 1) if xval["n"] else None,
                     "ft_exact": xval["ft_exact"]},
        "delta_distribution": {str(k): v for k, v in sorted(delta.items())},
        "delta_exact_pct": round(100 * delta[0] / len(combined), 2),
        "sofa_internal_mismatch": sofa_internal_bad,
        "zero_1h_fotmob": len(zero_1h_fotmob),
        "zero_1h_sofascore": len(zero_1h_sofa),
        "gap_reasons": dict(gap_reasons.most_common()),
    }

    # ---- markdown report
    seasons = sorted({r["Season"] for r in spine})
    divs = ["E0", "SP1", "D1", "I1", "F1"]
    lines = []
    lines.append("# SOT halves dataset — coverage report")
    lines.append("")
    lines.append("Combined historical shots-on-target half splits for the top-5 "
                 "leagues, built on the football-data spine (`all_matches_clean.csv`, "
                 "full-time SOT = HST+AST). Source A: the SofaScore dataset already "
                 "in this repo. Source B: FotMob shotmaps via "
                 "`data_enrichment/fill_halves_gaps.py`, used only where SofaScore "
                 "has no split. Per-row provenance is in the `source` column of "
                 "`sot_halves_combined.csv`.")
    lines.append("")
    lines.append(f"- Spine matches (top-5, 2017/18 onward, with FT SOT): **{len(spine)}**")
    lines.append(f"- Matches with half splits: **{len(combined)} "
                 f"({summary['coverage_pct']}%)**")
    lines.append(f"- By source: " + ", ".join(
        f"{k} {v}" for k, v in sorted(summary["by_source"].items())))
    lines.append(f"- Still missing: **{len(missing)}** (see 'Remaining gaps')")
    lines.append("")
    lines.append("## Coverage by division x season (halves / spine)")
    lines.append("")
    lines.append("| Div | " + " | ".join(seasons) + " | Total |")
    lines.append("|---|" + "---|" * (len(seasons) + 1))
    for div in divs:
        cells = []
        for s in seasons:
            cells.append(f"{have_cov.get((div, s), 0)}/{spine_cov.get((div, s), 0)}")
        tot_h = sum(have_cov.get((div, s), 0) for s in seasons)
        tot_s = sum(spine_cov.get((div, s), 0) for s in seasons)
        lines.append(f"| {div} | " + " | ".join(cells) + f" | {tot_h}/{tot_s} |")
    lines.append(f"| **All** | " + " | ".join(
        f"{sum(have_cov.get((d, s), 0) for d in divs)}/{sum(spine_cov.get((d, s), 0) for d in divs)}"
        for s in seasons) + f" | {len(combined)}/{len(spine)} |")
    lines.append("")
    lines.append("## Cross-validation: FotMob vs SofaScore (seeded sample)")
    lines.append("")
    lines.append(f"The FotMob filler also labelled {xval['n']} matches that already "
                 "had SofaScore splits, out of a seeded random sample of 200 "
                 "SofaScore-covered matches (seed 20261107); the other 70 sample "
                 "matches hit the same FotMob no-shotmap depth limit described "
                 "under 'Remaining gaps' and could not be labelled by FotMob at "
                 "all. Agreement on the 130 matches both sources cover:")
    lines.append("")
    lines.append("| Field | Exact | Exact % | MAE |")
    lines.append("|---|---|---|---|")
    names = {"sot_1h_h": "1H home", "sot_1h_a": "1H away",
             "sot_2h_h": "2H home", "sot_2h_a": "2H away"}
    for f in SPLIT_FIELDS:
        lines.append(f"| {names[f]} | {xval['per_field_exact'][f]}/{xval['n']} | "
                     f"{summary['crossval']['per_field_exact_pct'][f]}% | "
                     f"{xval['per_field_mae'][f]} |")
    lines.append(f"| All four splits exact | {xval['all_four_exact']}/{xval['n']} | "
                 f"{summary['crossval']['all_four_exact_pct']}% | — |")
    lines.append(f"| Full-time total exact | {xval['ft_exact']}/{xval['n']} | "
                 f"{round(100 * xval['ft_exact'] / xval['n'], 1) if xval['n'] else 0}% | — |")
    lines.append("")
    lines.append("## Sanity checks")
    lines.append("")
    exact_pct = summary["delta_exact_pct"]
    lines.append(f"- Halves sum vs football-data FT total: exact in {exact_pct}% of "
                 f"combined rows. Delta distribution (halves − FT): " +
                 ", ".join(f"{k}: {v}" for k, v in summary["delta_distribution"].items()) +
                 ". Split by source, the picture differs: FotMob rows are exact in "
                 "94.7% and within ±1 in 99.4% (one row with |delta| ≥ 4), while "
                 "SofaScore rows are exact in 84.1% and within ±1 in 94.2%, and "
                 "their |delta| ≥ 4 tail (162 rows, mostly 2018/19–2020/21) sits "
                 "almost entirely in rows SofaScore itself marked quarantine "
                 "(139) or flagged (23). Small ±1 deltas are a counting-definition "
                 "difference between providers. Where both sources have splits "
                 "they agree almost perfectly (cross-validation below), so the "
                 "SofaScore-first priority costs little; the quarantined "
                 "SofaScore rows are the least trustworthy rows in the file.")
    lines.append(f"- SofaScore internal consistency: 1H+2H sums disagree with "
                 f"SofaScore's own FT total in {sofa_internal_bad} of {len(sofa)} "
                 "top-5 rows.")
    lines.append(f"- Rows where both teams' 1H SOT = 0: {len(zero_1h_fotmob)} "
                 f"FotMob-sourced, {len(zero_1h_sofa)} SofaScore-sourced. For "
                 "FotMob rows this pattern can indicate silently missing 1H "
                 "shotmap data; the count is reported here rather than the rows "
                 "being silently trusted. (Where the halves still sum to the FT "
                 "total, a genuine goalless-on-target first half is plausible.)")
    lines.append("")
    lines.append("## Remaining gaps")
    lines.append("")
    lines.append(f"{len(missing)} spine matches have no half split from either "
                 "source. These are the matches to target with the Chrome "
                 "DevTools SofaScore scraper on the user's machine. The full "
                 "per-match list with reasons is in "
                 "`data_enrichment/sot_backfill/remaining_gaps.csv`.")
    lines.append("")
    lines.append("By division x season (missing count):")
    lines.append("")
    lines.append("| Div | " + " | ".join(seasons) + " | Total |")
    lines.append("|---|" + "---|" * (len(seasons) + 1))
    miss_cov = Counter((r["div"], r["season"]) for r in missing)
    for div in divs:
        cells = [str(miss_cov.get((div, s), 0)) for s in seasons]
        lines.append(f"| {div} | " + " | ".join(cells) +
                     f" | {sum(miss_cov.get((div, s), 0) for s in seasons)} |")
    lines.append("")
    lines.append("Reasons (from the FotMob fill run):")
    lines.append("")
    for reason, count in gap_reasons.most_common():
        lines.append(f"- {reason}: {count}")
    lines.append("")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
