"""Build the Montenegro 1. CFL scores/events analysis tables.

Phase-A builder (adapted from the Lithuania Toplyga builder
``league/LT-Toplyga/data/build_data.py`` — same payload anatomy, same
rules, different league). Official FT scores come from ``scoreStr``;
first-half goals come from credited Goal events in
``content.matchFacts.events.events``.

Measured corpus facts (see ``analysis/DATA_UNDERSTANDING.md``):

- 972 index rows; exactly one is NOT a played match — 3818692
  (Sutjeska vs Mornar, round 36, 2021/2022): ``started``/``finished``
  False, no ``scoreStr`` (the index "0-0" is a placeholder), and four
  phantom goal events. It is EXCLUDED; played rows = 971.
- 2024/2025 has 179 rows: round 36 carries 4 matches, not 5 — the
  Buducnost Podgorica vs Decic Tuzi fixture is absent from the index
  entirely (no file, no row). Treated as missing, never as zero.
- One played match has a goal-event feed that disagrees with the
  official score — 4711154 (Buducnost 5-2 Jedinstvo BP, 2024/2025):
  the event feed contains an extra away goal at minute 8 by player
  "<TBD>" (id 0), a phantom entry; the other two away goals are a
  Grivic own goal (8') and Komiya (15'). The official score stands;
  the HT split for this match is unreliable and is stored as NaN
  (``ht_source='mismatch_phantom'``).
- No stats block, no shotmap shots, no lineups, no referee text in
  any of the 972 payloads. Card events exist only as Red (74) and
  YellowRed (51) — there are NO Yellow card events at all.

The warehouse JSONs live outside this worktree (gitignored 24 GB
corpus in the main checkout); pass ``--warehouse-root`` pointing at
a checkout that carries ``data_enrichment/fotmob_world/``. Default
is this repo root, which works once the corpus is present there.
"""
import argparse, csv, json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEFAULT_WAREHOUSE = REPO
LEAGUE_ID = "232"
# Played matches per warehouse season (2021/2022 excludes the
# never-started ghost fixture 3818692; 2024/2025 is short one R36
# fixture absent from the index).
EXPECTED = {"2021/2022": 179, "2022/2023": 180, "2023/2024": 180,
            "2024/2025": 179, "2025/2026": 180, "2026/2027": 73}
GHOST_MATCH_ID = "3818692"
PHANTOM_HT_MATCH_ID = "4711154"


def event_minute(e):
    try:
        return float(e.get("time"))
    except (TypeError, ValueError):
        return None


def score(s):
    a, b = (s or "").split("-")[:2]
    return int(a.strip()), int(b.strip())


def load_row(index_row, root):
    path = root / index_row["path"].rstrip("\r")
    d = json.loads(path.read_text())
    g, h, c = d.get("general") or {}, d.get("header") or {}, d.get("content") or {}
    status = h.get("status") or {}
    home, away = g.get("homeTeam") or {}, g.get("awayTeam") or {}
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    events = (((c.get("matchFacts") or {}).get("events") or {}).get("events") or [])
    goals = [e for e in events if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    evh = sum(e.get("isHome") is True for e in goals)
    eva = sum(e.get("isHome") is False for e in goals)
    awarded = bool(status.get("awarded"))
    mismatch = (evh, eva) != (hg, ag)
    ht = [e for e in goals if event_minute(e) is not None and event_minute(e) <= 45]
    if index_row["match_id"] == PHANTOM_HT_MATCH_ID:
        ht_known, ht_source = False, "mismatch_phantom"
    else:
        ht_known = (not awarded) and bool(events) and not mismatch
        ht_source = "awarded_unknown" if awarded else ("events" if events and not mismatch else "none")
    row = {
        "match_id": index_row["match_id"], "season": index_row["season"],
        "date": (g.get("matchTimeUTCDate") or status.get("utcTime") or index_row.get("date", ""))[:10],
        "kickoff_utc": g.get("matchTimeUTCDate") or status.get("utcTime"),
        "round": str(g.get("matchRound") or ""),
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "ht_home_goals": "" if not ht_known else sum(e.get("isHome") is True for e in ht),
        "ht_away_goals": "" if not ht_known else sum(e.get("isHome") is False for e in ht),
        "ht_source": ht_source,
        "awarded": int(awarded), "has_events": int(bool(events)),
        "finished": int(bool(status.get("finished"))),
        "ev_goals_home": evh, "ev_goals_away": eva,
        "score_events_mismatch": int(mismatch),
        "coverage_level": g.get("coverageLevel"),
        "has_stats_content": int(c.get("stats") is not None),
        "has_shotmap": int(bool((c.get("shotmap") or {}).get("shots"))),
        "has_lineup": int(c.get("lineup") is not None),
        "referee": (((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "",
        "has_playoff_value": json.dumps(c.get("hasPlayoff"), ensure_ascii=False),
    }
    cards = [e for e in events if e.get("type") == "Card"]
    for kind in ("Yellow", "YellowRed", "Red"):
        row[f"card_{kind.lower()}_count"] = sum(e.get("card") == kind for e in cards)
    return row


def team_rows(m):
    out = []
    for side, other, venue in (("home", "away", "H"), ("away", "home", "A")):
        gf, ga = int(m[f"{side}_goals"]), int(m[f"{other}_goals"])
        out.append({
            "match_id": m["match_id"], "season": m["season"], "date": m["date"],
            "round": m["round"], "team_id": m[f"{side}_team_id"], "team": m[f"{side}_team"],
            "opponent_id": m[f"{other}_team_id"], "opponent": m[f"{other}_team"],
            "venue": venue, "goals_for": gf, "goals_against": ga,
            "ht_goals_for": m[f"ht_{side}_goals"], "ht_goals_against": m[f"ht_{other}_goals"],
            "result": "W" if gf > ga else ("D" if gf == ga else "L"),
            "points": 3 if gf > ga else (1 if gf == ga else 0), "awarded": m["awarded"],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse-root", type=Path, default=DEFAULT_WAREHOUSE)
    args = ap.parse_args()
    idx = args.warehouse_root / "data_enrichment" / "fotmob_world_index.csv"
    raw = [r for r in csv.DictReader(idx.open()) if r["league_id"] == LEAGUE_ID]
    assert len(raw) == 972, len(raw)
    excluded = [r for r in raw if r["match_id"] == GHOST_MATCH_ID]
    assert len(excluded) == 1, excluded
    played = []
    for r in raw:
        if r["match_id"] == GHOST_MATCH_ID:
            continue
        played.append(load_row(r, args.warehouse_root))
    assert len(played) == sum(EXPECTED.values()), len(played)
    assert all(r["finished"] for r in played)
    # The 86 empty-event rows keep ht_source 'none'; the one phantom
    # HT row is the only mismatch among played matches.
    played.sort(key=lambda r: (r["date"], str(r["match_id"])))
    counts = Counter(r["season"] for r in played)
    assert dict(counts) == EXPECTED, counts
    assert all(r["coverage_level"] == "lower" for r in played)
    assert sum(r["score_events_mismatch"] for r in played) == 1
    assert sum(r["awarded"] for r in played) == 0
    out = HERE
    with (out / "me_matches.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(played[0])); w.writeheader(); w.writerows(played)
    teams = [x for r in played for x in team_rows(r)]
    with (out / "me_team_matches.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(teams[0])); w.writeheader(); w.writerows(teams)
    print("season_counts=" + json.dumps(dict(sorted(counts.items()))))
    print(f"matches={len(played)} team_rows={len(teams)} excluded_ghost=1 awarded={sum(r['awarded'] for r in played)} mismatches={sum(r['score_events_mismatch'] for r in played)}")


if __name__ == "__main__":
    main()
