"""Build the Costa Rica Primera Division analysis CSV from the FotMob world warehouse.

Reads all league_id=121 JSONs under data_enrichment/fotmob_world/Costa Rica/Primera Division/
(the worktree carries a symlink data_enrichment/fotmob_world -> the warehouse)
and writes league/CR-PrimeraDivision/data/cr_matches.csv (one row per played match)
plus league/CR-PrimeraDivision/data/team_aliases.json.

Verified payload facts (coordinator, 2026-11-10; do not re-derive silently):
- content.stats is null in every match: no corners/SOT/shots/xG/shotmap. Goals + cards come
  from content.matchFacts.events.events (Goal/Card/Half/Substitution/MissedPenalty).
- header.teams[].score is the authoritative FT score. A Half event (time 45) carries HT score.
- Card values: Yellow / YellowRed / Red. YellowRed is always paired with an earlier Yellow
  event for the same player, so yellows = Yellow + YellowRed; reds = Red only.
- Referee text is empty in all seasons except 22 matches in 2025/2026.
- Team names have variants (Cartagines vs Cartaginés, ...): key teams by FotMob team id.

Usage: python3 league/CR-PrimeraDivision/data/build_data.py
"""
import csv
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
WARE = ROOT / "data_enrichment" / "fotmob_world" / "Costa Rica" / "Primera Division"
INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
OUT_CSV = HERE / "cr_matches.csv"
OUT_ALIASES = HERE / "team_aliases.json"

SEASON_DIRS = {
    "2021/2022": "2021-2022",
    "2022/2023": "2022-2023",
    "2023/2024": "2023-2024",
    "2024/2025": "2024-2025",
    "2025/2026": "2025-2026",
    "2026/2027": "2026-2027",
}

FIELDS = [
    "match_id", "season", "date_utc", "tournament", "stage", "round",
    "home_id", "home_name", "away_id", "away_name",
    "home_goals", "away_goals", "ht_home_goals", "ht_away_goals",
    "goals_1h_total", "goals_2h_total",
    "yellow_home", "yellow_away", "yellow_total", "red_home", "red_away",
    "yellow_1h_home", "yellow_1h_away", "yellow_2h_home", "yellow_2h_away",
    "cards_1h_total", "cards_2h_total", "referee", "events_present",
    "goal_event_mismatch",
]


def safe_write_text(path, text, tries=40):
    """Write text, verifying bytes landed (exec sandbox intermittently EPERMs writes)."""
    data = text.encode("utf-8")
    for _ in range(tries):
        try:
            tmp = str(path) + ".tmp%d" % os.getpid()
            with open(tmp, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            if os.path.getsize(tmp) != len(data):
                raise IOError("size mismatch")
            os.replace(tmp, path)
            if os.path.getsize(path) == len(data):
                return
        except (PermissionError, OSError):
            time.sleep(1.0)
    raise IOError("could not write %s after %d tries" % (path, tries))


def parse_match(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    g = d.get("general") or {}
    h = d.get("header") or {}
    mf = (d.get("content") or {}).get("matchFacts") or {}
    teams = h.get("teams") or []
    if len(teams) != 2:
        raise ValueError("expected 2 teams in %s" % path)
    home, away = teams[0], teams[1]
    hs, aws = home.get("score"), away.get("score")
    if hs is None or aws is None:
        raise ValueError("missing FT score in %s" % path)
    evs = (mf.get("events") or {}).get("events") or []
    ib = mf.get("infoBox") or {}
    tourn = ib.get("Tournament") or {}
    league_name = tourn.get("leagueName") or ""
    tournament = "Clausura" if "Clausura" in league_name else "Apertura"
    if "Championship Final" in league_name:
        stage = "championship_final"
    elif "Final Stage" in league_name:
        stage = "final_stage"
    else:
        stage = "regular"
    half = next((e for e in evs if e.get("type") == "Half"), None)
    ht_h = ht_a = None
    if half is not None:
        ht_h, ht_a = half.get("homeScore"), half.get("awayScore")
    n_goal_events = 0
    yh = ya = rh = ra = 0
    y1h_h = y1h_a = y2h_h = y2h_a = 0
    c1h = c2h = None
    if half is not None:
        c1h = c2h = 0
    seen_half = False
    for e in evs:
        t = e.get("type")
        if t == "Half":
            seen_half = True
            continue
        if t == "Goal":
            n_goal_events += 1
        elif t == "Card":
            card = e.get("card")
            is_home = bool(e.get("isHome"))
            if card in ("Yellow", "YellowRed"):
                if is_home:
                    yh += 1
                else:
                    ya += 1
                if c1h is not None:
                    if seen_half:
                        c2h += 1
                        if is_home:
                            y2h_h += 1
                        else:
                            y2h_a += 1
                    else:
                        c1h += 1
                        if is_home:
                            y1h_h += 1
                        else:
                            y1h_a += 1
            elif card == "Red":
                if is_home:
                    rh += 1
                else:
                    ra += 1
    ref = ((ib.get("Referee") or {}).get("text") or "").strip() or None
    row = {
        "match_id": str(g.get("matchId")),
        "season": None,  # filled by caller from directory
        "date_utc": (g.get("matchTimeUTCDate") or "")[:10],
        "tournament": tournament,
        "stage": stage,
        "round": tourn.get("roundName"),
        "home_id": int(home.get("id")),
        "home_name": home.get("name"),
        "away_id": int(away.get("id")),
        "away_name": away.get("name"),
        "home_goals": int(hs),
        "away_goals": int(aws),
        "ht_home_goals": ht_h,
        "ht_away_goals": ht_a,
        "goals_1h_total": (ht_h + ht_a) if ht_h is not None else None,
        "goals_2h_total": ((hs + aws) - (ht_h + ht_a)) if ht_h is not None else None,
        "yellow_home": yh,
        "yellow_away": ya,
        "yellow_total": yh + ya,
        "red_home": rh,
        "red_away": ra,
        "yellow_1h_home": y1h_h if half is not None else None,
        "yellow_1h_away": y1h_a if half is not None else None,
        "yellow_2h_home": y2h_h if half is not None else None,
        "yellow_2h_away": y2h_a if half is not None else None,
        "cards_1h_total": c1h,
        "cards_2h_total": c2h,
        "referee": ref,
        "events_present": bool(evs),
        "goal_event_mismatch": n_goal_events != (hs + aws),
    }
    return row


def main():
    # index cross-check: match_ids for league 121
    index_ids = {}
    with open(INDEX, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["league_id"] == "121":
                index_ids[r["match_id"]] = r["season"]
    rows = []
    name_counts = defaultdict(Counter)
    name_seasons = defaultdict(lambda: defaultdict(set))
    for season, dirname in SEASON_DIRS.items():
        folder = WARE / dirname
        files = sorted(folder.glob("*.json"))
        print("%s: %d files" % (season, len(files)))
        for fp in files:
            row = parse_match(fp)
            row["season"] = season
            rows.append(row)
            for key in ("home", "away"):
                tid = row["%s_id" % key]
                name_counts[tid][row["%s_name" % key]] += 1
                name_seasons[tid][row["%s_name" % key]].add(season)
    rows.sort(key=lambda r: (r["date_utc"], r["match_id"]))
    seen = [r["match_id"] for r in rows]
    assert len(seen) == len(set(seen)), "duplicate match_id"
    assert set(seen) == set(index_ids), (
        "CSV/index mismatch: in CSV not index %s; in index not CSV %s"
        % (sorted(set(seen) - set(index_ids))[:5], sorted(set(index_ids) - set(seen))[:5]))
    per_season = Counter(r["season"] for r in rows)
    print("per-season counts:", dict(sorted(per_season.items())))
    print("total rows:", len(rows))
    print("goal_event_mismatch:", [r["match_id"] for r in rows if r["goal_event_mismatch"]])
    print("no-events matches:", [r["match_id"] for r in rows if not r["events_present"]])
    # canonical names: most frequent variant per team id
    canonical = {}
    aliases = {}
    for tid, counter in name_counts.items():
        canon = counter.most_common(1)[0][0]
        canonical[tid] = canon
        aliases[str(tid)] = {
            "canonical_name": canon,
            "aliases": sorted(counter),
            "seasons": sorted({s for names in name_seasons[tid].values() for s in names}),
        }
    for r in rows:
        r["home_name"] = canonical[r["home_id"]]
        r["away_name"] = canonical[r["away_id"]]
    buf = []
    import io
    sio = io.StringIO()
    w = csv.DictWriter(sio, fieldnames=FIELDS)
    w.writeheader()
    for r in rows:
        w.writerow({k: ("" if r[k] is None else r[k]) for k in FIELDS})
    safe_write_text(OUT_CSV, sio.getvalue())
    safe_write_text(OUT_ALIASES, json.dumps(aliases, indent=2, ensure_ascii=False) + "\n")
    # verify by re-reading
    with open(OUT_CSV, newline="", encoding="utf-8") as f:
        back = list(csv.DictReader(f))
    assert len(back) == len(rows) == 1350, "row count %d" % len(back)
    print("wrote %s (%d rows) + %s (%d teams)" % (OUT_CSV, len(back), OUT_ALIASES, len(aliases)))


if __name__ == "__main__":
    main()
