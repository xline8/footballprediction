"""Build the PE-Liga1 analysis CSVs from the FotMob world warehouse.

One row per played match (league_id 131). Adapted from the
CO-PrimeraA builder / league/jleague_lib.py rules: FT score from
header, team stats from content.stats.Periods (All/FirstHalf),
events from matchFacts, referee + stadium from matchFacts.infoBox.

Peru Liga 1 specifics (measured 2026-11-10, see
analysis/DATA_UNDERSTANDING.md):
- Index n = 1,860; every indexed file is finished. Calendar-year
  seasons 2021-2026; 2026 is in progress (Apertura complete,
  Clausura at round 16 of 17 at pull time) and is reserved as the
  confirmatory window -- it is in the CSV, flagged by its labels,
  and the modelling layer never reads it in this build.
- Format: two regular tournaments per year (2021: Fase 1 + Fase 2;
  2022-2025: Apertura + Clausura; 2026: plain 'Liga 1' payload with
  rounds '1'..'17' = Apertura and 'Clausura - Round N' = Clausura),
  plus tiny play-off tails carried under separate sub-league names
  (Final Stage, Championship Playoff, Qualification, Placement
  Playoff; 15 matches total). `phase` = regular / playoff from the
  payload's sub-league name (frozen phase rule: play-offs are
  EXCLUDED from all fitting and evaluation; see PREPROCESSING.md).
- Nine matches carry status.awarded = True (eight in the 2023
  walkover wave, one in 2025 Clausura). They were not played;
  `awarded` = 1 and the modelling layer excludes them everywhere.
- NO xG anywhere (no expected_goals key in any file) and NO shotmap
  in any file: the goals model is goals-only by construction.
- Stats feed: a sparse block (BallPossesion, total_shots,
  ShotsOnTarget, corners) in ~92% of matches in every season, and a
  rich block (yellow_cards, touches_opp_box, big_chance, fouls, ...)
  in a subset that grows over time (2021 ~41 matches to 2026 all).
  Period splits (FirstHalf/SecondHalf) exist in 8 matches before
  2025, 199 in 2025 and all 297 in 2026. Duplicate stat keys across
  sections (top_stats vs shots/discipline) are de-duplicated by
  first occurrence.
- Cards are captured BOTH ways (stats-feed yellow_cards and
  event-derived yellows, plain and including second-yellow) so the
  EDA feed check can pick the target on dev-era evidence only.
- HT goals come from the Half event's HT score where present, else
  from goal-event times (events_exact guard), else none.
- Entrants: no Peru Liga 2 exists in the warehouse, so there is no
  feeder corpus. home/away_absent_prev flags a club absent from
  Liga 1 in the previous calendar year (promoted or returning);
  there is no mover_up flag.
- Team identity = FotMob team_id; display names canonicalised to
  the most frequent spelling per id (2026 payloads add accents to
  three clubs' names; ids never change).

Regenerate: .venv/bin/python league/PE-Liga1/data/build_data.py
Outputs (gitignored): pe_liga1_matches.csv + pe_liga1_team_matches.csv
"""
import csv, json
from collections import Counter
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")  # warehouse lives in main checkout (gitignored data)
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "131"

STAT_KEYS = ["BallPossesion", "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
             "shots_inside_box", "shots_outside_box", "big_chance", "touches_opp_box", "corners",
             "yellow_cards", "red_cards", "fouls", "Offsides", "keeper_saves",
             "expected_goals", "expected_goals_set_play", "expected_goals_open_play",
             "expected_goals_non_penalty", "expected_goals_on_target"]

EXPECTED_COUNTS = {"2021": 239, "2022": 346, "2023": 344, "2024": 306, "2025": 328, "2026": 297}
PLAYOFF_NAMES = ("Final Stage", "Championship Playoff", "Qualification", "Placement Playoff")


def _num(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, str):
        try: return float(v.split(" ")[0].replace("%", ""))
        except ValueError: return None
    return None


def flat_stats(content):
    """First occurrence wins: top_stats duplicates the shots/discipline
    sections in the rich era with identical values."""
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for s in group.get("stats", []) or []:
                if (period, s.get("key")) in out: continue
                vals = s.get("stats") or [None, None]
                h = _num(vals[0]); a = _num(vals[1]) if len(vals) > 1 else None
                if h is None and a is None: continue
                out[(period, s.get("key"))] = (h, a)
    return out


def load(row):
    return json.load(open(MAIN_REPO / row["path"], encoding="utf-8"))


def block_label(season, sub_name, match_round):
    if season == "2021":
        return "2021 - Fase 1" if "Fase 1" in sub_name else "2021 - Fase 2"
    if season == "2026":
        return "2026 - Clausura" if str(match_round).startswith("Clausura") else "2026 - Apertura"
    return f"{season} - {'Apertura' if 'Apertura' in sub_name else 'Clausura'}"


def main():
    index_rows = list(csv.DictReader(open(INDEX, encoding="utf-8")))
    rows = [r for r in index_rows if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))

    # Pass 1 (streaming): Liga 1 membership by calendar year + finished assert.
    a_teams_by_year = {}
    for r in rows:
        d = load(r)
        hdr = d.get("header") or {}; st = hdr.get("status") or {}
        assert st.get("finished"), f"unfinished file in corpus: {r['match_id']} {r['season']}"
        gen = d.get("general") or {}
        a_teams_by_year.setdefault(r["season"], set()).update((gen["homeTeam"]["id"], gen["awayTeam"]["id"]))
        del d

    # Pass 2 (streaming): one payload at a time, never retained.
    out = []
    for r in rows:
        d = load(r)
        gen = d.get("general") or {}; hdr = d.get("header") or {}; st = hdr.get("status") or {}
        c = d.get("content") or {}
        fs = flat_stats(c)
        def g(period, key):
            v = fs.get((period, key)); return v if v else (None, None)
        info = ((c.get("matchFacts") or {}).get("infoBox") or {})
        sub_name = gen.get("leagueName") or ""
        phase = "playoff" if any(p in sub_name for p in PLAYOFF_NAMES) else "regular"
        rec = {"match_id": r["match_id"], "league": "PE-Liga1", "season": r["season"],
               "block": block_label(r["season"], sub_name, gen.get("matchRound")),
               "tournament": sub_name, "phase": phase,
               "awarded": int(bool(st.get("awarded"))),
               "date": r["date"], "round": str(gen.get("matchRound")),
               "home_team_id": gen["homeTeam"]["id"], "home_team": gen["homeTeam"]["name"],
               "away_team_id": gen["awayTeam"]["id"], "away_team": gen["awayTeam"]["name"]}
        rec["home_goals"] = int(hdr["teams"][0]["score"]); rec["away_goals"] = int(hdr["teams"][1]["score"])
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        goals = [e for e in evs if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent", False)]
        rec["events_exact"] = int(len(goals) == rec["home_goals"] + rec["away_goals"])
        ht_ev = next((e for e in evs if e.get("type") == "Half" and e.get("halfStrShort") == "HT"), None)
        if ht_ev is not None and ht_ev.get("homeScore") is not None:
            rec["ht_home_goals"] = int(ht_ev["homeScore"]); rec["ht_away_goals"] = int(ht_ev["awayScore"])
            rec["ht_source"] = "half_event"
        elif rec["events_exact"]:
            rec["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
            rec["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
            rec["ht_source"] = "events"
        else:
            rec["ht_home_goals"] = None; rec["ht_away_goals"] = None; rec["ht_source"] = "none"
        for nm, cardset in (("ev_yellow", ("Yellow",)), ("ev_yellow_inc2nd", ("Yellow", "YellowRed"))):
            rec[nm + "_home"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in cardset and e.get("isHome"))
            rec[nm + "_away"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in cardset and not e.get("isHome"))
        rec["ev_red_home"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and e.get("isHome"))
        rec["ev_red_away"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed") and not e.get("isHome"))
        rec["fh_ev_yellow_inc2nd_home"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
        rec["fh_ev_yellow_inc2nd_away"] = sum(1 for e in evs if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed") and e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
        rec["n_events"] = len(evs)
        for k in STAT_KEYS:
            for per, suf in (("All", ""), ("FirstHalf", "_1h")):
                h, a = g(per, k)
                rec[f"{k.lower()}_home{suf}"] = h; rec[f"{k.lower()}_away{suf}"] = a
        rec["n_shotmap"] = len(((c.get("shotmap") or {}).get("shots") or []))
        rec["referee"] = ((info.get("Referee") or {}).get("text") or "")
        stadium = info.get("Stadium") or {}
        rec["stadium"] = stadium.get("name", ""); rec["stadium_city"] = stadium.get("city", "")
        rec["has_stats"] = int(fs.get(("All", "total_shots")) is not None)
        rec["has_rich_stats"] = int(fs.get(("All", "yellow_cards")) is not None)
        rec["has_period_splits"] = int(fs.get(("FirstHalf", "total_shots")) is not None)
        rec["has_xg"] = int(fs.get(("All", "expected_goals")) is not None)
        year = r["season"]; prev = str(int(year) - 1)
        prev_a = a_teams_by_year.get(prev, set())
        for side in ("home", "away"):
            tid = rec[f"{side}_team_id"]
            rec[f"{side}_absent_prev"] = int(year != "2021" and tid not in prev_a)
        out.append(rec)

    names = {}
    for r in out:
        for side in ("home", "away"):
            names.setdefault(r[f"{side}_team_id"], Counter())[r[f"{side}_team"]] += 1
    canon = {tid: cnt.most_common(1)[0][0] for tid, cnt in names.items()}
    for r in out:
        r["home_team"] = canon[r["home_team_id"]]; r["away_team"] = canon[r["away_team_id"]]

    counts = Counter(r["season"] for r in out)
    assert all(counts[season] >= expected for season, expected in EXPECTED_COUNTS.items()), dict(counts)
    assert len(out) >= 1860, len(out)
    ids = [r["match_id"] for r in out]; assert len(set(ids)) == len(ids)

    with open(OUT / "pe_liga1_matches.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    tm = []
    for r in out:
        for side, opp in (("home", "away"), ("away", "home")):
            tm.append({"match_id": r["match_id"], "season": r["season"], "block": r["block"],
                       "phase": r["phase"], "awarded": r["awarded"], "date": r["date"],
                       "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                       "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"],
                       "sot_for": r[f"shotsontarget_{side}"], "sot_against": r[f"shotsontarget_{opp}"],
                       "corners_for": r[f"corners_{side}"], "corners_against": r[f"corners_{opp}"],
                       "shots_for": r[f"total_shots_{side}"], "shots_against": r[f"total_shots_{opp}"],
                       "yellow_for": r[f"yellow_cards_{side}"], "yellow_against": r[f"yellow_cards_{opp}"],
                       "ev_yellow_for": r[f"ev_yellow_inc2nd_{side}"], "ev_yellow_against": r[f"ev_yellow_inc2nd_{opp}"]})
    with open(OUT / "pe_liga1_team_matches.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tm[0].keys())); w.writeheader(); w.writerows(tm)
    print(f"matches {len(out)} team_rows {len(tm)}")
    print("per-season:", dict(sorted(counts.items())))


if __name__ == "__main__":
    main()
