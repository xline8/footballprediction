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
# Jangkar tanggal run: main() mengaturnya dari --date. Loader memakai
# ini (bukan tanggal riil) sebagai lantai fixture, supaya run untuk
# tanggal tertentu tidak diam-diam berjangkar ke hari ini.
ANCHOR = TODAY

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
    """Load corner picks from corner predictions CSVs (probabilistic).

    Sumber: predictions_corners_upcoming.csv (liga) dan
    predictions_corners_cups.csv (piala EFL Cup/DFB Pokal).
    Generate picks for lines 8.5/9.5/10.5.
    Only pick if prob > 0.60 (Over) or prob < 0.40 (Under).
    """
    sources = [
        ("predictions_corners_upcoming.csv", ""),
        ("predictions_corners_cups.csv", None),  # competition dibaca dari baris
    ]
    picks = []
    for fn, default_comp in sources:
        rows = _read_csv(os.path.join(PROJ, fn))
        for r in rows:
            if r["date"] < ANCHOR:
                continue  # hanya fixture yang akan datang
            comp = r.get("competition") or default_comp or ""
            for ln in CORNER_LINES:
                p_over = _num(r.get(f"p_gt_{ln}"))
                if p_over is None:
                    continue
                p_under = 1.0 - p_over
                if p_over > 0.60:
                    picks.append({
                        "div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                        "market": "Corners", "line": str(ln), "side": "Over",
                        "prob": round(p_over, 4), "ev": None, "source": "model",
                        "tier": "best", "competition": comp,
                    })
                elif p_under > 0.60:
                    picks.append({
                        "div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                        "market": "Corners", "line": str(ln), "side": "Under",
                        "prob": round(p_under, 4), "ev": None, "source": "model",
                        "tier": "best", "competition": comp,
                    })
    return picks

def _load_dixon_coles_picks():
    """Load picks from goal prediction CSVs (1X2, DC, BTTS).

    Sumber: predictions_upcoming.csv (liga) dan predictions_cups_upcoming.csv
    (piala). Ketatkan threshold:
    - 1X2: ph > 0.60 (atau pd/pa > 0.55)
    - DC: (ph+pd) > 0.65 dan ph < 0.75 (atau analog untuk X2/12)
    - BTTS: p_btts > 0.60
    """
    sources = [
        ("predictions_upcoming.csv", ""),
        ("predictions_cups_upcoming.csv", None),  # competition dibaca dari baris
    ]
    picks = []
    for fn, default_comp in sources:
        rows = _read_csv(os.path.join(PROJ, fn))
        for r in rows:
            if r["date"] < ANCHOR:
                continue
            comp = r.get("competition") or default_comp or ""
            ph = _num(r.get("ph_dc"))
            pd = _num(r.get("pd_dc"))
            pa = _num(r.get("pa_dc"))
            pbtts = _num(r.get("p_btts"))
            if not all((ph, pd, pa)):
                continue

            # 1X2 picks — ev_model = EV terhadap harga B365 di baris
            # prediksi (satu-satunya harga pasar yang tersedia di sini);
            # tanpa harga, ev_model None (lihat _fill_ev_model).
            _o = {"1": _num(r.get("b365h")), "X": _num(r.get("b365d")),
                  "2": _num(r.get("b365a"))}
            if ph > 0.60:
                picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                              "market": "1X2", "line": "", "side": "1", "prob": round(ph,4), "ev": None, "ev_model": round(ph * _o["1"] - 1, 4) if _o["1"] else None, "source": "model", "competition": comp})
            elif pd > 0.55:
                picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                              "market": "1X2", "line": "", "side": "X", "prob": round(pd,4), "ev": None, "ev_model": round(pd * _o["X"] - 1, 4) if _o["X"] else None, "source": "model", "competition": comp})
            elif pa > 0.60:
                picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                              "market": "1X2", "line": "", "side": "2", "prob": round(pa,4), "ev": None, "ev_model": round(pa * _o["2"] - 1, 4) if _o["2"] else None, "source": "model", "competition": comp})

            # DC picks
            if (ph + pd) > 0.65 and ph < 0.75:
                picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                              "market": "DC", "line": "", "side": "1X", "prob": round(ph + pd,4), "ev": None, "source": "model", "competition": comp})
            if (pd + pa) > 0.65 and pa < 0.75:
                picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                              "market": "DC", "line": "", "side": "X2", "prob": round(pd + pa,4), "ev": None, "source": "model", "competition": comp})
            if (ph + pa) > 0.70:  # 12 tidak punya draw
                picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                              "market": "DC", "line": "", "side": "12", "prob": round(ph + pa,4), "ev": None, "source": "model", "competition": comp})

            # BTTS picks
            if pbtts and pbtts > 0.60:
                picks.append({"div": r["div"], "date": r["date"], "home": r["home"], "away": r["away"],
                              "market": "BTS", "line": "", "side": "Yes", "prob": round(pbtts,4), "ev": None, "source": "model", "competition": comp})
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
        if not kickoff or kickoff[:10] < ANCHOR:
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
            "competition": "",
        })
    return picks

def _top_pick_per_match(picks):
    """Select 1 best pick per match.

    Priority:
    1. Highest model probability (Pick Teraman) — probabilitas tertinggi menang
    2. EV as tie-breaker (info, bukan penentu utama)
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
        # Sort by: prob (highest first), then EV
        pg_sorted = sorted(pg, key=lambda x: (
            -(x.get('prob') or 0),
            -(x.get('ev') or float('-inf'))
        ))
        top = pg_sorted[0]

        # Calculate ev_model for non-ta_model picks
        # ev_model hanya boleh berasal dari harga pasar nyata (diisi
        # loader untuk 1X2 dan OU 2.5 Over dari kolom B365 baris
        # prediksi). Rumus lama — prob*(1/prob - 1) - (1 - prob) —
        # identik 0 untuk semua prob, sehingga kolom ini selalu
        # tercetak 0.0 dan tidak menyampaikan apa pun (audit ronde 3).
        if top.get('ev') is None and top.get('ev_model') is None:
            top['ev_model'] = None

        best.append(top)

    best.sort(key=lambda x: (x["date"], x["div"], x["home"]))
    return best

GOAL_LINES = (1.5, 2.5, 3.5)
# Kandidat pick corner dibatasi ke band 8.5–10.5 (kolom p_gt_* di CSV
# dan ladder prob_over di API tetap utuh — hanya kandidat yang dibatasi).
CORNER_LINES = (8.5, 9.5, 10.5)


def _norm_name(x):
    try:
        from football_etl import normalize_name as _n
        return _n(x)
    except ImportError:
        return x


def _scan_candidates(pred_row, corner_row):
    """Seluruh seleksi dari pemindaian lengkap untuk satu laga (ev=None).

    Mencakup 1X2 (3 sisi), DC (3 sisi), O/U gol 1.5/2.5/3.5 Over/Under,
    BTTS Yes/No, dan corner line 8.5/9.5/10.5 Over/Under (jika baris corner ada).
    """
    cands = []
    ph = _num(pred_row.get("ph_dc"))
    pd = _num(pred_row.get("pd_dc"))
    pa = _num(pred_row.get("pa_dc"))
    if all(v is not None for v in (ph, pd, pa)):
        _o = {"1": _num(pred_row.get("b365h")), "X": _num(pred_row.get("b365d")),
              "2": _num(pred_row.get("b365a"))}
        for side, pr in (("1", ph), ("X", pd), ("2", pa)):
            cands.append({"market": "1X2", "line": "", "side": side, "prob": pr,
                          "ev_model": round(pr * _o[side] - 1, 4) if _o[side] else None})
        for side, pr in (("1X", ph + pd), ("X2", pd + pa), ("12", ph + pa)):
            cands.append({"market": "DC", "line": "", "side": side, "prob": pr})
        _o25 = _num(pred_row.get("b365o25"))
        for ln, col in ((1.5, "p_over15_dc"), (2.5, "p_over_dc"), (3.5, "p_over35_dc")):
            po = _num(pred_row.get(col))
            if po is None:
                continue
            cands.append({"market": "OU", "line": str(ln), "side": "Over", "prob": po,
                          "ev_model": round(po * _o25 - 1, 4) if (ln == 2.5 and _o25) else None})
            cands.append({"market": "OU", "line": str(ln), "side": "Under", "prob": 1 - po})
    pb = _num(pred_row.get("p_btts"))
    if pb is not None:
        cands.append({"market": "BTS", "line": "", "side": "Yes", "prob": pb})
        cands.append({"market": "BTS", "line": "", "side": "No", "prob": 1 - pb})
    if corner_row:
        for ln in CORNER_LINES:
            po = _num(corner_row.get(f"p_gt_{ln}"))
            if po is None:
                continue
            cands.append({"market": "Corners", "line": str(ln), "side": "Over", "prob": po})
            cands.append({"market": "Corners", "line": str(ln), "side": "Under", "prob": 1 - po})
    for c in cands:
        c.update({"ev": None, "source": "model", "tier": "fallback",
                  "div": pred_row["div"], "date": pred_row["date"],
                  "home": pred_row["home"], "away": pred_row["away"],
                  "competition": pred_row.get("competition") or ""})
    return cands


def _fallback_candidate(pred_row, corner_row):
    """Pick satu selection berprobabilitas tertinggi untuk laga tanpa best pick."""
    cands = _scan_candidates(pred_row, corner_row)
    if not cands:
        return None
    return max(cands, key=lambda c: c["prob"])


def _select_safest(best_cands, scan_cands):
    """Gabungkan kandidat best + pemindaian lengkap; pilih probabilitas tertinggi.

    Tie-break: tier best lebih dulu, lalu EV lebih tinggi. Hasil membawa tier
    sesuai asal seleksi (best vs fallback).
    """
    combined = list(best_cands) + list(scan_cands)
    if not combined:
        return None
    key = lambda c: ((c.get('prob') or 0),
                     1 if c.get('tier') == 'best' else 0,
                     c.get('ev') or 0)
    return max(combined, key=key)


def _fill_ev_model(p):
    """Pastikan kunci ev_model ada; JANGAN mengarang nilainya.

    ev_model yang sah diisi loader dari harga pasar nyata (B365 untuk
    1X2 / OU 2.5 Over). Untuk seleksi tanpa harga (DC, BTS, corner,
    OU garis lain) nilainya None — kolom kosong di CSV berarti 'tidak
    tersedia', bukan 0.0 karangan rumus tautologi lama.
    """
    if p.get('ev') is not None or p.get('ev_model') is not None:
        return
    p['ev_model'] = None


def main():
    global ANCHOR
    target = date.today().isoformat()
    args = sys.argv[1:]
    if "--date" in args:
        i = args.index("--date")
        if i + 1 < len(args):
            target = args[i + 1]
    ANCHOR = target
    print(f"target date: {target}")

    corner = _load_corner_picks()
    dc = _load_dixon_coles_picks()
    ta = _load_ta_picks()

    all_picks = corner + dc + ta
    for p in all_picks:
        p.setdefault("tier", "best")
    best = _top_pick_per_match(all_picks)

    cols = ["div", "date", "home", "away", "market", "line", "side",
            "prob", "ev", "ev_model", "source", "tier", "competition"]
    _write_csv(OUT, best, cols)
    _write_csv(os.path.join(PROJ, "best_picks_full.csv"), all_picks, cols)

    print(f"corner picks: {len(corner)} | DC picks: {len(dc)} | ta_model picks: {len(ta)}")
    print(f"-> {OUT} ({len(best)} top picks, 1 per match)")
    print(f"-> best_picks_full.csv ({len(all_picks)} all picks)")

    markets = {}
    for p in best:
        markets[p["market"]] = markets.get(p["market"], 0) + 1
    print(f"  Top picks by market: {markets}")

    # --- best_picks_today.csv: TEPAT satu baris per laga terjadwal hari target.
    # Pick teraman = probabilitas tertinggi di antara gabungan kandidat best
    # (lolos threshold/EV) dan pemindaian lengkap _scan_candidates().
    # Cakupan: laga liga (predictions_upcoming.csv) + piala (predictions_cups_upcoming.csv).
    pred_rows = []
    for fn in ("predictions_upcoming.csv", "predictions_cups_upcoming.csv"):
        pred_rows += [r for r in _read_csv(os.path.join(PROJ, fn))
                      if (r.get("date") or "") == target]
    corner_by = {}
    for fn in ("predictions_corners_upcoming.csv", "predictions_corners_cups.csv"):
        for r in _read_csv(os.path.join(PROJ, fn)):
            corner_by.setdefault((r["div"], r["date"], _norm_name(r["home"]), _norm_name(r["away"])), r)
    best_group_by = defaultdict(list)
    for p in all_picks:
        best_group_by[(p["div"], p["date"], _norm_name(p["home"]), _norm_name(p["away"]))].append(p)

    today_rows = []
    for r in pred_rows:
        k = (r["div"], r["date"], _norm_name(r["home"]), _norm_name(r["away"]))
        sel = _select_safest(best_group_by.get(k, []),
                             _scan_candidates(r, corner_by.get(k)))
        if sel is None:
            today_rows.append({"div": r["div"], "date": r["date"], "home": r["home"],
                               "away": r["away"], "market": "", "line": "", "side": "",
                               "prob": None, "ev": None, "ev_model": None,
                               "source": "model", "tier": "fallback",
                               "competition": r.get("competition") or ""})
            continue
        _fill_ev_model(sel)
        today_rows.append({c: sel.get(c) for c in cols})

    TODAY_OUT = os.path.join(PROJ, "best_picks_today.csv")
    _write_csv(TODAY_OUT, today_rows, cols)
    from collections import Counter
    tiers = Counter(r["tier"] for r in today_rows)
    print(f"-> {TODAY_OUT} ({len(today_rows)} baris, 1 per laga hari {target}; tier={dict(tiers)})")


if __name__ == "__main__":
    main()
