"""Build K League 3 score-only analysis tables from the FotMob warehouse.

The warehouse is read from the main checkout because this worktree does not
contain it. Names are canonicalized by most frequent spelling per team ID.
The eight unplayed 2021 fixtures are excluded:
3548124, 3548130, 3548133, 3548134, 3548135, 3548139, 3548147, 3548154.
"""
import csv, json
from collections import Counter, defaultdict
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
UNPLAYED = {"3548124", "3548130", "3548133", "3548134", "3548135", "3548139", "3548147", "3548154"}

def score(s):
    try:
        a, b = str(s).replace(" ", "").split("-")[:2]
        return int(a), int(b)
    except Exception as e:
        raise ValueError(f"invalid score {s!r}") from e

def flat_goal_events(header_events):
    out = []
    for side, key in (("home", "homeTeamGoals"), ("away", "awayTeamGoals")):
        for vals in ((header_events or {}).get(key) or {}).values():
            for e in vals or []:
                if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent"):
                    out.append((side, e))
    return out

def card_events(content):
    return [e for e in (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])
            if e.get("type") == "Card"]

def main():
    idx = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == "9537"]
    payloads = []
    names = defaultdict(Counter)
    for r in idx:
        d = json.loads((MAIN_REPO / r["path"]).read_text())
        payloads.append((r, d))
        for side in ("home", "away"):
            t = (d.get("general") or {}).get(side + "Team") or {}
            names[str(t.get("id"))][t.get("name", "")] += 1
    canonical = {tid: sorted(c.items(), key=lambda x: (-x[1], x[0]))[0][0] for tid, c in names.items()}
    out, tm, mismatch = [], [], []
    event_ok_regular = event_bad_regular = event_ok_all = event_bad_all = 0
    for r, d in sorted(payloads, key=lambda x: (x[0]["date"], x[0]["match_id"])):
        g = d.get("general") or {}; h = d.get("header") or {}; st = h.get("status") or {}
        started, finished = bool(st.get("started", g.get("started"))), bool(st.get("finished", g.get("finished")))
        if not (started and finished):
            continue
        ps, iscore = score(st.get("scoreStr")), score(r["score"])
        if ps != iscore: mismatch.append((r["match_id"], iscore, ps))
        home, away = g.get("homeTeam") or {}, g.get("awayTeam") or {}
        hid, aid = str(home["id"]), str(away["id"])
        he = h.get("events") or {}
        goals = flat_goal_events(he)
        eg = (sum(1 for side, _ in goals if side == "home"), sum(1 for side, _ in goals if side == "away"))
        event_reconciles = eg == ps
        if event_reconciles: event_ok_all += 1
        else: event_bad_all += 1
        regular = g.get("leagueName") != "K3 League Playoff"
        if regular:
            if event_reconciles: event_ok_regular += 1
            else: event_bad_regular += 1
        facts_events = (((d.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []
        if event_reconciles:
            hh = sum(1 for side, e in goals if side == "home" and (e.get("time") or 999) <= 45)
            aa = sum(1 for side, e in goals if side == "away" and (e.get("time") or 999) <= 45)
            hts, hta, source = hh, aa, "events"
        else:
            hts = hta = ""
            source = "missing"
        cards = card_events(d.get("content") or {})
        rec = {"match_id": r["match_id"], "league": "KR-KLeague3", "season": r["season"],
               "date": (g.get("matchTimeUTCDate") or r["date"])[:10], "round": str(g.get("matchRound", "")),
               "phase": "playoff" if not regular else "regular", "home_team_id": hid,
               "home_team": canonical[hid], "away_team_id": aid, "away_team": canonical[aid],
               "coverage_level": g.get("coverageLevel", ""), "home_goals": ps[0], "away_goals": ps[1],
               "ht_home_goals": hts, "ht_away_goals": hta, "ht_source": source,
               "red_home": sum(1 for e in cards if e.get("card") in ("Red", "YellowRed") and e.get("isHome")),
               "red_away": sum(1 for e in cards if e.get("card") in ("Red", "YellowRed") and not e.get("isHome")),
               "has_events": int(bool(he) or bool(facts_events)), "event_reconciles": int(event_reconciles),
               "event_goal_events": len(goals), "index_has_stats": r["has_stats"],
               "index_has_shotmap": r["has_shotmap"], "index_has_lineup": r["has_lineup"],
               "index_has_period_splits": r["has_period_splits"]}
        out.append(rec)
    if mismatch: raise SystemExit(f"SCORE MISMATCHES: {mismatch}")
    if len(idx) != 1296 or len(out) != 1288: raise SystemExit(f"row-count mismatch: index={len(idx)} played={len(out)}")
    with (OUT / "kr3_matches.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, list(out[0])); w.writeheader(); w.writerows(out)
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            tm.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"], "phase": r["phase"],
                       "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                       "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"]})
    with (OUT / "kr3_team_matches.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, list(tm[0])); w.writeheader(); w.writerows(tm)
    regular_n = sum(r["phase"] == "regular" for r in out)
    print(f"index_rows={len(idx)} rows_in={len(idx)} rows_out={len(out)} regular={regular_n} playoff={len(out)-regular_n}")
    print(f"score_mismatches=0 event_reconciled_regular={event_ok_regular}/{regular_n} event_fail_regular={event_bad_regular} event_reconciled_all={event_ok_all}/{len(out)} event_fail_all={event_bad_all}")
    print(f"unplayed_excluded={len(idx)-len(out)} ids={sorted(UNPLAYED)} team_rows={len(tm)}")

if __name__ == "__main__": main()
