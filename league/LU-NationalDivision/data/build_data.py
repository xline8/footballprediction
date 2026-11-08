"""LU-NationalDivision data builder: FotMob warehouse JSONs -> match-level CSV.

Usage: python3 build_data.py
Reads the world index (league_id 229) and the payload JSONs under
data_enrichment/fotmob_world/Luxembourg/National Division/<season>/.
Writes league/LU-NationalDivision/data/lu_matches.csv (gitignored by
repo norm *.csv; this script is the reproducible source).

LU-forced facts (verified in raw payloads, all 1,296 index rows present
on disk, all finished=True, scores present in every row):
- Single competition: general.leagueName is "National Division" and
  parentLeagueId 229 in all 1,296 payloads; 30 rounds x 8 matches,
  16 teams, 240 matches per full season. No sub-competitions, no
  playoffs (content.hasPlayoff False where present, absent before
  2025/26). No sibling Luxembourg league exists in the warehouse
  (index: only league_id 229 for country Luxembourg) -> no X2 mover
  prior is possible.
- content.stats is ABSENT (null) in all 1,296 payloads; shotmap.shots
  is an empty list in all 1,296. The world-index has_stats/has_shotmap
  flags are False everywhere here (and are key-presence flags anyway).
  Scores-only league: no SOT, corners, total shots, xG, or yellows
  exist in any season.
- Events (content.matchFacts.events.events) exist in 1,251/1,296
  matches: types Goal (4,062), Half (2,502), Card (385). Card events
  are ONLY Red (232) and YellowRed (153) -- no plain Yellow event
  exists anywhere, so no total-cards target can be built. Goal-event
  times give the 1H/2H goal split (minute <= 45 is 1H).
- 45 matches have an empty events list; 44 of them are 0-0, so their
  halves are 0/0 by construction. Exactly ONE match has goals but no
  goal events: 4520839 (2024/25, Swift Hesperange 0-3 US Mondorf les
  Bains) -- its halves columns are left empty (missing, not zero).
  Score-vs-event goal totals agree everywhere else (4,062 events vs
  4,065 scored goals; the 3-goal gap is that one match).
- Referee: infoBox.Referee key exists in all 1,296 payloads but its
  text is "" in every one. Stadium and Attendance are null everywhere.
  No referee feature is possible.
- Team identity is keyed by FotMob team id (header.teams[].id);
  names are carried for readability only.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
# The warehouse (data_enrichment/) is gitignored, so a fresh worktree
# does not contain it. Pass the checkout that holds it as argv[1]
# (default: this repo root).
BASE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO
INDEX = BASE / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent / "lu_matches.csv"
LEAGUE_ID = "229"

COLUMNS = [
    "match_id", "season", "date", "round",
    "home_team", "away_team", "home_id", "away_id",
    "home_goals", "away_goals",
    "goals_1h_home", "goals_1h_away", "goals_2h_home", "goals_2h_away",
    "red_cards_home", "red_cards_away", "has_events", "referee",
    "source_path",
]


def build():
    rows = []
    log = Counter()
    with open(INDEX, newline="") as f:
        index_rows = [r for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID]
    log["index_rows"] = len(index_rows)
    for ir in index_rows:
        path = BASE / ir["path"]
        d = json.loads(path.read_text())
        g = d["general"]
        assert g["leagueId"] == 229 and g["leagueName"] == "National Division", ir
        assert g["parentLeagueId"] == 229, ir
        header = d["header"]
        assert header["status"]["finished"] is True, ir
        home, away = header["teams"][0], header["teams"][1]
        hs, aws = home["score"], away["score"]
        assert hs is not None and aws is not None, ir
        assert header["status"].get("scoreStr") == f"{hs} - {aws}", ir
        events = (d["content"]["matchFacts"].get("events") or {}).get("events") or []
        has_events = len(events) > 0
        g1h = g1a = g2h = g2a = None
        red_h = red_a = 0
        n_goal_events = 0
        if has_events:
            for e in events:
                if e.get("type") == "Goal":
                    n_goal_events += 1
                    if e.get("time") is None:
                        continue
                    if e["time"] <= 45:
                        if e.get("isHome"):
                            g1h = (g1h or 0) + 1
                        else:
                            g1a = (g1a or 0) + 1
                    else:
                        if e.get("isHome"):
                            g2h = (g2h or 0) + 1
                        else:
                            g2a = (g2a or 0) + 1
                elif e.get("type") == "Card":
                    if e.get("isHome"):
                        red_h += 1
                    else:
                        red_a += 1
            # Fill zeros for halves where events exist but a side scored
            # no goals in that half.
            g1h = g1h or 0
            g1a = g1a or 0
            g2h = g2h or 0
            g2a = g2a or 0
            if n_goal_events != hs + aws:
                log["score_event_mismatch"] += 1
        else:
            # Empty events list: halves are 0/0 only for a 0-0 scoreline;
            # otherwise genuinely missing (exactly one match: 4520839).
            if hs + aws == 0:
                g1h = g1a = g2h = g2a = 0
            else:
                log["halves_missing_goals_present"] += 1
        ref = (d["content"]["matchFacts"].get("infoBox") or {}).get("Referee") or {}
        ref_text = ref.get("text") or ""
        if ref_text:
            log["referee_named"] += 1
        rows.append({
            "match_id": g["matchId"], "season": ir["season"],
            "date": ir["date"], "round": g.get("leagueRoundName") or "",
            "home_team": home["name"], "away_team": away["name"],
            "home_id": home["id"], "away_id": away["id"],
            "home_goals": hs, "away_goals": aws,
            "goals_1h_home": g1h, "goals_1h_away": g1a,
            "goals_2h_home": g2h, "goals_2h_away": g2a,
            "red_cards_home": red_h, "red_cards_away": red_a,
            "has_events": has_events, "referee": ref_text,
            "source_path": ir["path"],
        })
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    print("build log:", dict(log))
    print("seasons:", dict(Counter(r["season"] for r in rows)))


if __name__ == "__main__":
    build()
