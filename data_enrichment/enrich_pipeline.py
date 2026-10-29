"""enrich_pipeline.py — left-join data eksogen ke data historis.

Tidak menimpa `all_matches_clean.csv`; hasil ditulis ke `all_matches_enriched.csv`.
Mode default = dry-run subset (EPL 2023/24) utk membuktikan logika join.

Kolom baru:
  ps_home/ps_draw/ps_away  (Pinnacle closing), mx_home, av_home
  midweek_home_flag/midweek_away_flag
  xg_home, xg_away, rolling_xg_diff
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from collections import defaultdict, deque
from datetime import date

from .fetch_closing_odds import extract_closing_odds
from .fetch_xg import build_xg_map
from .synthesize_european import build_midweek_map
from .utils import setup_logging, to_float, norm_team

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_CSV = os.path.join(BASE_DIR, "all_matches_clean.csv")
OUT_CSV = os.path.join(BASE_DIR, "all_matches_enriched.csv")

_log = setup_logging()

NEW_COLS = ["ps_home", "ps_draw", "ps_away", "mx_home", "av_home",
            "midweek_home_flag", "midweek_away_flag", "xg_home", "xg_away",
            "rolling_xg_diff"]


def _as_date(v):
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v)[:10])
    except (ValueError, TypeError):
        return None


_ETL_NORM = None


def _etl_norm(name):
    """Nama kanonik football_etl.normalize_name.

    Peta xG lokal (features._load_xg_map, dipakai build_xg_map) dikunci
    dengan normalizer INI, sedangkan join di file ini dulu memakai
    utils.norm_team untuk semua peta. Dua ruang nama itu berbeda tepat
    di klub beralias ("manchester united" vs "man united", "bayern
    munich" vs "bayern munchen", dst), jadi xG klub-klub tersebut tidak
    pernah cocok dan kolomnya kosong. Join odds/midweek tetap memakai
    norm_team karena produsernya memang memakai itu.
    """
    global _ETL_NORM
    if _ETL_NORM is None:
        try:
            from football_etl import normalize_name
        except ImportError:
            sys.path.insert(0, BASE_DIR)
            from football_etl import normalize_name
        _ETL_NORM = normalize_name
    return _ETL_NORM(name or "")


def _xg_key(r, d):
    return (r.get("Div"), d.isoformat(),
            _etl_norm(r.get("HomeTeam")), _etl_norm(r.get("AwayTeam")))


def load_rows(csv_path: str) -> list[dict]:
    with open(csv_path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rolling_xg_diffs(rows, xg_map):
    """chronologis, leak-free: mean selisih xG 5 laga terakhir per tim."""
    ordered = sorted((r for r in rows if _as_date(r.get("Date"))),
                     key=lambda r: (_as_date(r["Date"]), r.get("Div", "")))
    deq = defaultdict(lambda: deque(maxlen=5))
    out = {}
    for r in ordered:
        d = _as_date(r["Date"])
        h, a = norm_team(r.get("HomeTeam")), norm_team(r.get("AwayTeam"))
        key = (r.get("Div"), d.isoformat(), h, a)
        xg = xg_map.get(_xg_key(r, d))
        rh = float(sum(deq[h])) / len(deq[h]) if deq[h] else None
        ra = float(sum(deq[a])) / len(deq[a]) if deq[a] else None
        out[(r.get("Div"), d.isoformat(), h, a)] = (
            (rh - ra) if (rh is not None and ra is not None) else None)
        if xg:
            xgh, xga = xg
            deq[h].append(xgh - xga)
            deq[a].append(xga - xgh)
        else:
            # tanpa xG: gunakan selisih gol aktual sbg fallback ringan
            fthg, ftag = to_float(r.get("FTHG")), to_float(r.get("FTAG"))
            if fthg is not None and ftag is not None:
                deq[h].append(fthg - ftag)
                deq[a].append(ftag - fthg)
    return out


def enrich(rows, xg_map, odds_map, midweek_map, roll_map):
    n_odd = n_xg = n_mw = n_roll = 0
    for r in rows:
        d = _as_date(r.get("Date"))
        if d is None:
            continue
        h, a = norm_team(r.get("HomeTeam")), norm_team(r.get("AwayTeam"))
        key = (r.get("Div"), d.isoformat(), h, a)
        o = odds_map.get(key)
        if o:
            ps, mx, av = o["ps"], o["mx"], o["av"]
            r["ps_home"], r["ps_draw"], r["ps_away"] = ps
            r["mx_home"] = mx[0]
            r["av_home"] = av[0]
            n_odd += 1
        else:
            for c in ("ps_home", "ps_draw", "ps_away", "mx_home", "av_home"):
                r[c] = ""
        mw = midweek_map.get(key, (0, 0))
        r["midweek_home_flag"], r["midweek_away_flag"] = mw
        n_mw += (1 if (mw[0] or mw[1]) else 0)
        xg = xg_map.get(_xg_key(r, d))
        if xg:
            r["xg_home"], r["xg_away"] = xg
            n_xg += 1
        else:
            r["xg_home"], r["xg_away"] = "", ""
        rr = roll_map.get(key)
        r["rolling_xg_diff"] = "" if rr is None else round(rr, 4)
        n_roll += 1 if rr is not None else 0
    return {"odds": n_odd, "xg": n_xg, "midweek": n_mw, "roll": n_roll}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Data enrichment pipeline")
    ap.add_argument("--full", action="store_true",
                    help="proses seluruh dataset (default: dry-run EPL 2023/24)")
    ap.add_argument("--out", default=OUT_CSV)
    args = ap.parse_args(argv)

    rows = load_rows(SOURCE_CSV)
    if args.full:
        work = rows
        tag = "FULL"
    else:
        work = [r for r in rows if r.get("Div") == "E0"
                and "2023" in (r.get("Season") or "")]
        tag = "DRY-RUN (EPL 2023/24)"

    xg_map = build_xg_map(fetch_remote=False)
    odds_map = extract_closing_odds(SOURCE_CSV)
    midweek_map = build_midweek_map(rows)
    roll_map = rolling_xg_diffs(rows, xg_map)

    stats = enrich(work, xg_map, odds_map, midweek_map, roll_map)

    cols = list(rows[0].keys()) if rows else []
    for c in NEW_COLS:
        if c not in cols:
            cols.append(c)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(work)

    print("=" * 70)
    print(f"ENRICH PIPELINE — {tag}")
    print("=" * 70)
    print(f"input rows : {len(work)} ({len(rows)} total dataset)")
    print(f"output     : {args.out}")
    print(f"join odds Pinnacle/Max/Avg : {stats['odds']}/{len(work)}")
    print(f"join xG                    : {stats['xg']}/{len(work)}")
    print(f"midweek flag terisi (1)    : {stats['midweek']}/{len(work)}")
    print(f"rolling_xg_diff terisi     : {stats['roll']}/{len(work)}")
    if work:
        r0 = work[0]
        print("contoh baris enriched:")
        print(" ", {k: r0.get(k) for k in
                    ("Date", "HomeTeam", "AwayTeam", "ps_home", "ps_draw",
                     "ps_away", "midweek_home_flag", "midweek_away_flag",
                     "xg_home", "xg_away", "rolling_xg_diff")})
    return 0


if __name__ == "__main__":
    sys.exit(main())
