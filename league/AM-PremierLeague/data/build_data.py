"""Build the AM-PremierLeague analysis CSV from the FotMob world warehouse.

One row per played match (FotMob league id 118). Source of truth for the
score is the index CSV score (official FT score); payloads supply team
ids, round, HT score (from the Half event at time 45, halfStrShort HT),
event counts, and the awarded flag.

Coverage facts (measured 2026-11-10 on all 881 payloads):
- team stats: 0/881 non-null; shotmap shots: 0/881; lineups: 0/881 with
  real content (16 payloads in 2025/2026 carry a lineup shell with
  lineupType "unavailable", empty starters, no away-team starters);
  playerStats: 0/881; referee text: 0/881. This league is scores +
  events only.
- Events: Goal 2,372 / Half 1,656 / Card 186 (all Red 135 / YellowRed
  51; zero Yellow cards). Goal events reproduce the official score in
  874/881; the 7 exceptions are exactly the 7 awarded matches.
- HT score present for 828/881 matches; agrees with goal-events<=45
  on 828/828.
- Format: NO split-group / championship / relegation round / playoff
  in any season — round names are plain integers 1-36 in every season.
  Team count changes every season: 9 teams x 32 games (2021/22, 4
  matches/round x 36 rounds), 10 teams x 36 (2022/23, 2023/24),
  11 teams x 30 (2024/25, 5/round x 33 rounds), 10 teams x 27
  (2025/26, 5/round x 27 rounds, triple round-robin), 12 teams in
  progress in 2026/27 (6/round; rounds 1-13 played, n=77 as of
  2026-11-08, plus one round-15 fixture played early on 2026-08-20
  and one round-13 fixture still unplayed/postponed).
- 7 awarded matches, all in 2024/2025, all involving West Armenia
  (official 3-0/0-3, reason AW): 4558174, 4558250, 4558261, 4558323,
  4558316, 4558304, 4558305. They are flagged `awarded=True` and are
  excluded from every fit and evaluation (administrative scorelines,
  not played football — BA/AE precedent); they stay in the CSV so
  the exclusion is auditable.

Payload root: the worktree does not carry the 24 GB warehouse
(gitignored), so payloads are resolved from this repo when present,
else from FOOTBALLPREDICTION_ROOT, else ~/workspace/footballprediction
(the main checkout). The index CSV itself is tracked, so the row list
is identical in every checkout.

Output: league/AM-PremierLeague/data/am_matches.csv (gitignored
by repo norm; this script is the committed reproducible source).
Usage: python3 league/AM-PremierLeague/data/build_data.py
"""
import csv
import json
import os

LEAGUE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(LEAGUE_DIR)))
INDEX = os.path.join(REPO, "data_enrichment", "fotmob_world_index.csv")
OUT = os.path.join(LEAGUE_DIR, "am_matches.csv")
LEAGUE_ID = "118"


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
            "playoff": False,
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
