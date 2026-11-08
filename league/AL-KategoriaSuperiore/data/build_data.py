"""Build the AL-KategoriaSuperiore analysis CSV from the FotMob world warehouse.

One row per played match (FotMob league id 260). Source of truth for the
score is the index CSV score (official FT score); payloads supply team
ids, round, HT score (from the Half event at time 45, halfStrShort HT),
event counts, and the playoff flag.

Coverage facts (measured 2026-11-10 on all 969 payloads):
- team stats: 0/969 non-null; shotmap shots: 0/969; lineups: 0/969;
  playerStats: 0/969; referee text: 0/969. This league is scores +
  events only.
- Events: Goal 2,190 / Half 1,774 / Card 230 (all YellowRed/Red; zero
  Yellow cards). Goal events reproduce the official score in 969/969.
- HT score present for 887/969 matches; agrees with goal-events<=45
  on 887/887.
- Format: 10 teams x 36 rounds every season. From 2023/2024 a Final
  Four playoff follows the regular season: 2023/24 + 2024/25 = 2
  semi-finals (round "1/2") + bronze + final (4 matches); 2025/26 =
  a 6-match Final Four round-robin mislabelled by FotMob as rounds
  "1"/"2"/"3" and dated 2026-05-16..31 (regular season ended
  2026-05-10). Playoff matches (14) are flagged `playoff=True` and
  are excluded from every fit and evaluation (knockout / mini-league
  format, top-4 only); they stay in the CSV so the exclusion is
  auditable.
- No awarded matches in this league (0/969).

Payload root: the worktree does not carry the 24 GB warehouse
(gitignored), so payloads are resolved from this repo when present,
else from FOOTBALLPREDICTION_ROOT, else ~/workspace/footballprediction
(the main checkout). The index CSV itself is tracked, so the row list
is identical in every checkout.

Output: league/AL-KategoriaSuperiore/data/al_matches.csv (gitignored
by repo norm; this script is the committed reproducible source).
Usage: python3 league/AL-KategoriaSuperiore/data/build_data.py
"""
import csv
import json
import os
import sys

LEAGUE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(LEAGUE_DIR)))
INDEX = os.path.join(REPO, "data_enrichment", "fotmob_world_index.csv")
OUT = os.path.join(LEAGUE_DIR, "al_matches.csv")
LEAGUE_ID = "260"

PLAYOFF_ROUNDS = {"1/2", "bronze", "final"}
# 2025/2026 Final Four round-robin: FotMob labels them rounds 1-3.
PLAYOFF_2526_FROM = "2026-05-16"


def payload_roots():
    roots = [REPO]
    env = os.environ.get("FOOTBALLPREDICTION_ROOT")
    if env:
        roots.append(env)
    roots.append(os.path.expanduser("~/workspace/footballprediction"))
    seen, out = set(), []
    for r in roots:
        if r and r not in seen:
            seen.add(r)
            out.append(r)
    return out


def resolve_payload(rel_path):
    for root in payload_roots():
        p = os.path.join(root, rel_path)
        if os.path.exists(p):
            return p
    raise FileNotFoundError(rel_path)


def is_playoff(r, round_name):
    if round_name in PLAYOFF_ROUNDS:
        return True
    if r["season"] == "2025/2026" and round_name in ("1", "2", "3") \
            and r["date"] >= PLAYOFF_2526_FROM:
        return True
    return False


def main():
    rows = [r for r in csv.DictReader(open(INDEX)) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = []
    for r in rows:
        d = json.load(open(resolve_payload(r["path"])))
        g = d["general"]
        st = (d.get("header") or {}).get("status") or {}
        mf = (d.get("content") or {}).get("matchFacts") or {}
        evs = (mf.get("events") or {}).get("events") or []
        round_name = g.get("leagueRoundName") or ""
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
            "round": round_name,
            "playoff": is_playoff(r, round_name),
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
    print(f"playoff: {sum(1 for x in out if x['playoff'])}; "
          f"awarded: {sum(1 for x in out if x['awarded'])}; "
          f"HT present: {sum(1 for x in out if x['ht_home_goals'] != '')}")


if __name__ == "__main__":
    main()
