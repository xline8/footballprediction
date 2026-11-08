"""Build the BA-PremierLeague analysis CSV from the FotMob world warehouse.

One row per played match (FotMob league id 267). Source of truth for the
score is the index CSV score (official FT score); payloads supply team
ids, round, HT score (from the Half event at minute 45), event counts
and the awarded flag.

Coverage facts (measured 2026-11-10 on all 1,036 payloads):
- team stats: 0/1,036 non-null; shotmap shots: 0/1,036; lineups: 13/1,036;
  referee text: 0/1,036. This league is scores + events only.
- Events: Goal 2,568 / Half 1,920 / Card 205 (all YellowRed/Red; zero
  Yellow cards). Goal events reproduce the official score except the
  4 awarded matches, whose official 3-0/0-3 does not reflect play.
- HT score present for 961/1,036 matches; agrees with goal-events<=45
  on 961/961.

Output: league/BA-PremierLeague/data/ba_matches.csv (gitignored by repo
norm; this script is the committed reproducible source).
Usage: python3 league/BA-PremierLeague/data/build_data.py
"""
import csv
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
# When run from the repo root, REPO resolves to the repo root; the
# index path below is relative to it either way.
INDEX = os.path.join(REPO, "data_enrichment", "fotmob_world_index.csv")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "ba_matches.csv")
LEAGUE_ID = "267"


def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for r in rows:
        d = json.load(open(os.path.join(REPO, r["path"])))
        g = d["general"]
        st = (d.get("header") or {}).get("status") or {}
        mf = (d.get("content") or {}).get("matchFacts") or {}
        evs = (mf.get("events") or {}).get("events") or []
        ib = mf.get("infoBox") or {}
        tourn = ib.get("Tournament") or {}
        ht_hg = ht_ag = None
        n_goal = n_card = n_half = 0
        for e in evs:
            t = e.get("type")
            if t == "Goal":
                n_goal += 1
            elif t == "Card":
                n_card += 1
            elif t == "Half":
                n_half += 1
                if e.get("time") == 45:
                    ht_hg, ht_ag = e.get("homeScore"), e.get("awayScore")
        hg, ag = map(int, r["score"].split("-"))
        out.append({
            "match_id": r["match_id"],
            "season": r["season"],
            "date": r["date"],
            "round": tourn.get("round") or "",
            "home_team_id": g["homeTeam"]["id"],
            "home_team": g["homeTeam"]["name"],
            "away_team_id": g["awayTeam"]["id"],
            "away_team": g["awayTeam"]["name"],
            "home_goals": hg,
            "away_goals": ag,
            "ht_home_goals": "" if ht_hg is None else ht_hg,
            "ht_away_goals": "" if ht_ag is None else ht_ag,
            "awarded": bool(st.get("awarded")),
            "n_events": len(evs),
            "n_goal_events": n_goal,
            "n_card_events": n_card,
            "n_half_events": n_half,
            "events_present": len(evs) > 0,
        })
    fields = list(out[0].keys())
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    print(f"wrote {OUT}: {len(out)} rows")
    print(f"awarded: {sum(1 for x in out if x['awarded'])}; "
          f"HT present: {sum(1 for x in out if x['ht_home_goals'] != '')}")


if __name__ == "__main__":
    main()
