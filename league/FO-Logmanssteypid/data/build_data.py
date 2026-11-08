#!/usr/bin/env python3
"""Build the FO-Logmanssteypid analysis CSV (6 rows) from the FotMob world warehouse.

Reads the warehouse index (league_id 9523) + the 6 match payloads and
emits one row per played match with payload-verified targets. Stats /
shotmap / events / lineups are absent in ALL 6 payloads — the columns
stay empty, never imputed.

Run from the main checkout, where the (gitignored, 24 GB) warehouse
lives — this worktree does not contain it:
    python3 league/FO-Logmanssteypid/data/build_data.py \
        --repo-root ~/workspace/footballprediction \
        --out league/FO-Logmanssteypid/data/fo_logmanssteypid_matches.csv
The CSV is gitignored (repo norm); this script is the committed record.
It feeds NO fitting: the league is NOT BUILDABLE (see prereg/).
"""
import argparse
import csv
import json
from pathlib import Path

LEAGUE_ID = "9523"


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
        g = d.get("general", {})
        st = d.get("header", {}).get("status", {})
        c = d.get("content", {})
        reason = st.get("reason", {}) or {}
        pens = reason.get("penalties")
        ev = (c.get("matchFacts", {}) or {}).get("events", {}) or {}
        out_rows.append({
            "match_id": r["match_id"], "season": r["season"], "date": r["date"],
            "round": g.get("leagueRoundName", ""),
            "home": r["home"], "away": r["away"],
            "home_goals": h, "away_goals": a,
            "result": reason.get("long", ""),
            "penalties_h": pens[0] if pens else "",
            "penalties_a": pens[1] if pens else "",
            "loser_on_penalties": st.get("whoLostOnPenalties", ""),
            "has_stats": c.get("stats") is not None,
            "shotmap_shots": len((c.get("shotmap") or {}).get("shots") or []),
            "n_events": len(ev.get("events") or []),
            "red_cards_h": st.get("numberOfHomeRedCards", ""),
            "red_cards_a": st.get("numberOfAwayRedCards", ""),
            "referee": "",  # no referee field in any payload (0/6)
            "coverage_level": g.get("coverageLevel", ""),
        })
    out = Path(args.out) if args.out else (
        Path(__file__).resolve().parent / "fo_logmanssteypid_matches.csv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    print(f"wrote {len(out_rows)} rows -> {out}")


if __name__ == "__main__":
    main()
