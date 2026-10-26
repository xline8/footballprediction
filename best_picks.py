"""best_picks.py — gabungkan semua pick dari tiap market ke satu file.

Sumber:
  predictions_upcoming.csv         — Dixon-Coles 1X2, O/U, BTTS (blended w/ FD odds jika ada)
  predictions_corners_upcoming.csv — corner model (probabilistic, Over/Under 8.5)
  ta/best_bets.csv                 — picks yang sudah melewati ta_model (dengan EV jika ada odds)

Output:
  best_picks.csv — satu pick per laga per market, kolom:
    div, date, home, away, market, line, side, prob, ev, source

Tanpa odds (corner model): kolom ev = None, prob = model confidence
Dengan odds (ta_model picks): kolom ev terisi, prob = model * odds

NOTE: Untuk corner picks, rekomendasi berdasarkan model probabilistic:
  - p_over_8.5 > 0.60 → Over 8.5
  - p_over_8.5 < 0.40 → Under 8.5
  - selain itu → SKIP (tidak yakin cukup)
Ini bukan "value pick" — hanya rekomendasi "yang paling mungkin terjadi".
Untuk value pick corner, perlu odds pasar.
"""
import csv
import os
import sys
from datetime import date
from collections import defaultdict

import paths

PROJ = paths.BASE
TODAY = date.today().isoformat()

OUT = os.path.join(PROJ, "best_picks.csv")

def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def _read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def _write_csv(path, rows, cols):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def _load_corner_picks():
    """Load corner picks from predictions_corners_upcoming.csv (probabilistic).

    Generate picks for multiple lines: Over/Under 8.5, 9.5, 10.5
    Only pick if prob > 0.60 (Over) or prob < 0.40 (Under)
    """
    rows = _read_csv(os.path.join(PROJ, "predictions_corners_upcoming.csv"))
    picks = []
    for r in rows:
        if r["date"] < TODAY:
            continue  # hanya fixture yang akan datang
        for ln in (8.5, 9.5, 10.5):
            p_over = _num(r.get(f"p_gt_{ln}"))
            if p_over is None:
                continue
            p_under = 1.0 - p_over
            if p_over > 0.60:
                picks.append({
                    "div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                    "market": "Corners", "line": str(ln), "side": "Over",
                    "prob": round(p_over, 4), "ev": None, "source": "model",
                })
            elif p_under > 0.60:
                picks.append({
                    "div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                    "market": "Corners", "line": str(ln), "side": "Under",
                    "prob": round(p_under, 4), "ev": None, "source": "model",
                })
    return picks

def _load_dixon_coles_picks():
    """Load picks from predictions_upcoming.csv (1X2, DC, BTTS).

    Ketatkan threshold:
    - 1X2: ph > 0.60 (atau pd/pa > 0.55)
    - DC: (ph+pd) > 0.65 dan ph < 0.75 (atau analog untuk X2/12)
    - BTTS: p_btts > 0.60
    """
    rows = _read_csv(os.path.join(PROJ, "predictions_upcoming.csv"))
    picks = []
    for r in rows:
        if r["date"] < TODAY:
            continue
        ph = _num(r.get("ph_dc"))
        pd = _num(r.get("pd_dc"))
        pa = _num(r.get("pa_dc"))
        pbtts = _num(r.get("p_btts"))
        if not all((ph, pd, pa)):
            continue

        # 1X2 picks
        if ph > 0.60:
            picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                          "market": "1X2", "line": "", "side": "1", "prob": round(ph,4), "ev": None, "source": "model"})
        elif pd > 0.55:
            picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                          "market": "1X2", "line": "", "side": "X", "prob": round(pd,4), "ev": None, "source": "model"})
        elif pa > 0.60:
            picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                          "market": "1X2", "line": "", "side": "2", "prob": round(pa,4), "ev": None, "source": "model"})

        # DC picks
        if (ph + pd) > 0.65 and ph < 0.75:
            picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                          "market": "DC", "line": "", "side": "1X", "prob": round(ph + pd,4), "ev": None, "source": "model"})
        if (pd + pa) > 0.65 and pa < 0.75:
            picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                          "market": "DC", "line": "", "side": "X2", "prob": round(pd + pa,4), "ev": None, "source": "model"})
        if (ph + pa) > 0.70:  # 12 tidak punya draw
            picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                          "market": "DC", "line": "", "side": "12", "prob": round(ph + pa,4), "ev": None, "source": "model"})

        # BTTS picks
        if pbtts and pbtts > 0.60:
            picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                          "market": "BTS", "line": "", "side": "Yes", "prob": round(pbtts,4), "ev": None, "source": "model"})
    return picks

_LEAGUE_MAP = {
    "Premier League": "E0", "Bundesliga": "D1", "Serie A": "I1",
    "La Liga": "SP1", "Ligue 1": "F1",
    "Spain - Primera Division": "SP1",  # nama TA utk La Liga
}

def _league_div(league):
    # league dari ta_scrape: "England - Premier League" -> E0 (substring match)
    lg = league.strip().lower()
    for key, div in _LEAGUE_MAP.items():
        if key.lower() in lg:
            return div
    return None

def _load_ta_picks():
    """Load picks yang sudah melewati ta_model (dengan EV jika ada odds).

    Filter:
    - Status pending/open (selain SETTLED)
    - Kickoff date >= today
    - EV > 0 (hanya picks yang menguntungkan)
    - div bisa dipetakan
    """
    rows = _read_csv(os.path.join(PROJ, "ta", "best_bets.csv"))
    picks = []
    for r in rows:
        status = (r.get("status") or "").upper()
        if status in ("SETTLED", "LOSE", "WIN", "PUSH"):
            continue
        kickoff = r.get("kickoff_utc", "")
        if not kickoff or kickoff[:10] < TODAY:
            continue
        league = r.get("league", "").strip()
        div = _league_div(league)
        if not div:
            continue
        ev = _num(r.get("edge_pp") or r.get("ev"))
        if not ev or ev <= 0:
            continue
        prob = _num(r.get("p_model"))
        if prob is None:
            continue
        picks.append({
            "div": div,
            "date": kickoff[:10],
            "home": r.get("home", ""),
            "away": r.get("away", ""),
            "market": r.get("market", ""),
            "line": r.get("line", ""),
            "side": r.get("selection", ""),
            "prob": round(prob, 4),
            "ev": round(ev, 4),
            "source": "ta_model",
        })
    return picks

def _top_pick_per_match(picks):
    """Select 1 best pick per match.

    Priority:
    1. Picks with +EV (from ta_model with odds) — measurable value
    2. Highest model probability
    Only 1 pick per match — dedup by date+home+away
    """
    # Normalize names for key matching (corner CSV vs predictions may differ in case)
    try:
        from football_etl import normalize_name as _norm
    except ImportError:
        _norm = lambda x: x

    by_match = defaultdict(list)
    for p in picks:
        key = (p["div"], p["date"], _norm(p["home"]), _norm(p["away"]))
        by_match[key].append(p)

    best = []
    for key, pg in by_match.items():
        # Sort by: EV (highest first), then prob
        pg_sorted = sorted(pg, key=lambda x: (
            -(x.get('ev') or float('-inf')),
            -(x.get('prob') or 0)
        ))
        top = pg_sorted[0]

        # Calculate ev_model for non-ta_model picks
        # ev_model = p_model * (fair_odds - 1) - (1 - p_model)
        # Using typical odds range as estimate
        if top.get('ev') is None:
            prob = top.get('prob') or 0
            if prob > 0:
                # Estimate: assume fair odds ~ 1/prob
                fair_odds = 1.0 / prob
                top['ev_model'] = round(prob * (fair_odds - 1.0) - (1.0 - prob), 4)
            else:
                top['ev_model'] = None

        best.append(top)

    best.sort(key=lambda x: (x["date"], x["div"], x["home"]))
    return best

def main():
    corner = _load_corner_picks()
    dc = _load_dixon_coles_picks()
    ta = _load_ta_picks()

    all_picks = corner + dc + ta
    best = _top_pick_per_match(all_picks)

    cols = ["div", "date", "home", "away", "market", "line", "side",
            "prob", "ev", "ev_model", "source"]
    _write_csv(OUT, best, cols)

    # Also write full picks (all markets) for reference
    _write_csv(os.path.join(PROJ, "best_picks_full.csv"), all_picks, cols)

    print(f"corner picks: {len(corner)} | DC picks: {len(dc)} | ta_model picks: {len(ta)}")
    print(f"-> {OUT} ({len(best)} top picks, 1 per match)")
    print(f"-> best_picks_full.csv ({len(all_picks)} all picks)")

    # Show market distribution
    markets = {}
    for p in best:
        m = p["market"]
        markets[m] = markets.get(m, 0) + 1
    print(f"  Top picks by market: {markets}")

    # Validation: cek picks ada di predictions_upcoming.csv (gunakan normalized names)
    sys.path.insert(0, PROJ)
    try:
        from football_etl import normalize_name as norm
    except ImportError:
        norm = lambda x: x

    pred_rows = _read_csv(os.path.join(PROJ, "predictions_upcoming.csv"))
    pred_keys = set()
    for r in pred_rows:
        pred_keys.add((r.get("div",""), r.get("date",""),
                       norm(r.get("home","")), norm(r.get("away",""))))
    bp_keys = set((p["div"], p["date"], norm(p["home"]), norm(p["away"])) for p in best)
    missing = bp_keys - pred_keys
    if missing:
        print(f"  WARNING: {len(missing)} picks tidak ada di predictions_upcoming.csv")
    else:
        print(f"  OK: semua {len(bp_keys)} picks terverifikasi di predictions_upcoming.csv")

if __name__ == "__main__":
    main()
