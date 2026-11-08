#!/usr/bin/env python3
"""Build the CO-Superliga analysis CSV (12 rows) from the FotMob world warehouse.

Reads the warehouse index (league_id 11536) + the 12 match payloads and
emits one row per played match with payload-verified targets. Absent
stats/shotmap stay empty — never imputed.

Run from the main checkout, where the (gitignored, 24 GB) warehouse
lives — this worktree does not contain it:
    python3 league/CO-Superliga/data/build_data.py \
        --repo-root ~/workspace/footballprediction \
        --out league/CO-Superliga/data/co_superliga_matches.csv
The CSV is gitignored (repo norm); this script is the committed record.
It feeds NO fitting: the league is NOT BUILDABLE (see prereg/).
"""
import argparse
import csv
import json
from pathlib import Path

LEAGUE_ID = "11536"


def statmap(payload, period="All"):
    st = payload.get("content", {}).get("stats")
    if not st:
        return None
    out = {}
    for grp in st["Periods"][period]["stats"]:
        for s in grp.get("stats", []):
            out[s["key"]] = s.get("stats")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    root = Path(args.repo_root)
    index = root / "data_enrichment" / "fotmob_world_index.csv"
    rows = [r for r in csv.DictReader(open(index)) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["season"], r["date"]))
    out_rows = []
    for r in rows:
        d = json.loads((root / r["path"]).read_text())
        h, a = map(int, r["score"].split("-"))
        sm = statmap(d)
        sm1 = statmap(d, "FirstHalf") if sm else None
        shots = d.get("content", {}).get("shotmap", {}).get("shots") or []
        ev = d["content"]["matchFacts"]["events"]["events"]
        status = d.get("header", {}).get("status", {})
        leg = d["content"]["matchFacts"]["infoBox"].get("legInfo", {})

        def get(m, k):
            if m is None or k not in m:
                return ""
            v = m[k]
            return v[0] if isinstance(v, list) and len(v) == 1 else v

        def pair(m, k):
            if m is None or k not in m:
                return ("", "")
            v = m[k]
            return (v[0], v[1]) if isinstance(v, list) and len(v) == 2 else ("", "")

        th, ta = pair(sm, "total_shots")
        ch, ca = pair(sm, "corners")
        sh, sa = pair(sm, "ShotsOnTarget")
        yh, ya = pair(sm, "yellow_cards")
        xgh, xga = pair(sm, "expected_goals")
        th1, ta1 = pair(sm1, "total_shots")
        ch1, ca1 = pair(sm1, "corners")
        sh1, sa1 = pair(sm1, "ShotsOnTarget")
        out_rows.append({
            "match_id": r["match_id"], "season": r["season"], "date": r["date"],
            "leg": leg.get("localizedString", {}).get("fallback", ""),
            "home": r["home"], "away": r["away"],
            "home_goals": h, "away_goals": a,
            "aggregate": status.get("aggregatedStr", ""),
            "loser_on_aggregate": status.get("whoLostOnAggregated", ""),
            "loser_on_penalties": status.get("whoLostOnPenalties", ""),
            "result": status.get("reason", {}).get("long", ""),
            "has_stats": sm is not None,
            "shotmap_shots": len(shots),
            "shotmap_sot": sum(1 for s in shots if s.get("isOnTarget")),
            "total_shots_h": th, "total_shots_a": ta,
            "corners_h": ch, "corners_a": ca,
            "sot_h": sh, "sot_a": sa,
            "yellow_cards_h": yh, "yellow_cards_a": ya,
            "xg_h": xgh, "xg_a": xga,
            "total_shots_1h_h": th1, "total_shots_1h_a": ta1,
            "corners_1h_h": ch1, "corners_1h_a": ca1,
            "sot_1h_h": sh1, "sot_1h_a": sa1,
            "card_events": sum(1 for e in ev if e.get("type") == "Card"),
            "referee": "",  # no referee field in any payload (0/12)
        })
    out = Path(args.out) if args.out else (
        Path(__file__).resolve().parent / "co_superliga_matches.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {len(out_rows)} rows -> {out}")


if __name__ == "__main__":
    main()
