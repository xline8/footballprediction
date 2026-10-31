#!/usr/bin/env python3
"""features.py — lapisan fitur sepakbola berbasis data historis (anti-leakage).

Fitur dihitung HANYA dari match yang tanggalnya < match yang diprediksi
(state tim diperbarui setelah match, sehingga tidak pernah bocor ke depan).
Fitur yang disediakan:
- Elo strength (per tim) + selisih Elo
- Form points (5 laga terakhir, weighted)
- Rata-rata selisih gol (rolling)
- Rata-rata xG for/against (rolling, jika xG tersedia)
- Hari istirahat sejak laga terakhir (fatigue / schedule density)

Komponen produksi: build_feature_rows dipakai jalur serving
(predict_upcoming_refactored) untuk menghitung baris fitur fixture
mendatang, yang diprediksi model T3 dan diteruskan ke stack meta.
Lihat feature_analysis.py untuk perbandingan.
"""

import csv
import os
from collections import defaultdict, deque
from datetime import date

from football_etl import normalize_name, parse_date
from paths import DATA_CLEAN, XGRAW

NORM_POINTS = {"H": 3, "D": 1, "A": 0}
MAXG = 10
TOP5 = {"E0", "D1", "I1", "SP1", "F1"}
_XG_MAP_CACHE = {}


# ------------------------------------------------------------------ Elo ----
class Elo:
    """Elo sederhana dengan keuntungan kandang tetap."""

    K = 20.0
    HOME_ADV = 60.0
    START = 1500.0

    def __init__(self):
        self.rating = defaultdict(lambda: self.START)
        self.played = defaultdict(int)

    def expected(self, ra, rb):
        return 1.0 / (1.0 + 10.0 ** ((rb - ra) / 400.0))

    def update(self, home, away, hg, ag):
        ra, rb = self.rating[home], self.rating[away]
        eh = self.expected(ra + self.HOME_ADV, rb)
        # Ekspektasi tandang = komplemen kandang (dengan keunggulan
        # kandang yang sama). Rumus lama menghitungnya dari
        # ra - HOME_ADV sehingga eh + ea != 1 dan total rating
        # terdeflasi K*(1 - eh - ea) di SETIAP laga (audit ronde 3).
        ea = 1.0 - eh
        sh = 1.0 if hg > ag else (0.5 if hg == ag else 0.0)
        sa = 1.0 - sh
        self.rating[home] = ra + self.K * (sh - eh)
        self.rating[away] = rb + self.K * (sa - ea)
        self.played[home] += 1
        self.played[away] += 1


# ------------------------------------------------------------- muat xG ---
def _load_xg_maps():
    """Load xG values and their provenance.

    ``FOOTBALL_XG_SOURCE`` controls precedence:
    ``understat`` (default), ``native`` (football-data HxG/AxG only), or
    ``native_priority`` (native values override Understat, with Understat as
    fallback).  Keeping the default unchanged makes the experiment opt-in.
    """
    source_mode = os.environ.get("FOOTBALL_XG_SOURCE", "understat").lower()
    if source_mode not in {"understat", "native", "native_priority"}:
        raise ValueError(
            "FOOTBALL_XG_SOURCE must be understat, native, or native_priority")

    def stamp(path):
        try:
            st = os.stat(path)
            return (st.st_mtime_ns, st.st_size)
        except OSError:
            return (0, 0)

    cache_key = (source_mode, tuple(stamp(p) for p in (
        DATA_CLEAN if source_mode in {"native", "native_priority"} else "",
        os.path.join(XGRAW, "xg_matches.csv"),
        os.path.join(XGRAW, "map_full.json"),
        os.path.join(XGRAW, "map_ext.json"),
    )))
    if cache_key in _XG_MAP_CACHE:
        return _XG_MAP_CACHE[cache_key]

    nmap = {}
    for fn in ("map_full.json", "map_ext.json"):
        p = os.path.join(XGRAW, fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                nmap.update(json_load(f))
    understat = {}
    p = os.path.join(XGRAW, "xg_matches.csv")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                d = parse_date(r.get("datetime"))
                if d is None:
                    continue
                home = nmap.get(f"{r.get('div')}|{r.get('home')}")
                away = nmap.get(f"{r.get('div')}|{r.get('away')}")
                if not home or not away:
                    continue
                xgh = to_float(r.get("xgh"))
                xga = to_float(r.get("xga"))
                if xgh is None or xga is None:
                    continue
                understat[(r.get("div"), d.isoformat(),
                           normalize_name(home), normalize_name(away))] = (xgh, xga)

    native = {}
    if source_mode in {"native", "native_priority"} and os.path.exists(DATA_CLEAN):
        with open(DATA_CLEAN, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                if r.get("Div") not in TOP5 or not r.get("Date"):
                    continue
                xgh = to_float(r.get("HxG"))
                xga = to_float(r.get("AxG"))
                home = normalize_name(r.get("HomeTeam"))
                away = normalize_name(r.get("AwayTeam"))
                if xgh is None or xga is None or not home or not away:
                    continue
                native[(r["Div"], r["Date"], home, away)] = (xgh, xga)

    if source_mode == "native":
        out = dict(native)
        sources = {k: "native" for k in out}
    elif source_mode == "native_priority":
        out = dict(understat)
        sources = {k: "understat" for k in out}
        out.update(native)
        sources.update({k: "native" for k in native})
    else:
        out = dict(understat)
        sources = {k: "understat" for k in out}
    _XG_MAP_CACHE[cache_key] = (out, sources)
    return out, sources


def _load_xg_map():
    """(div, date_iso, home_norm, away_norm) -> (xgh, xga)."""
    return _load_xg_maps()[0]


def _load_xg_source_map():
    """Return xG provenance using the same source-selection policy."""
    return _load_xg_maps()[1]


def json_load(f):
    import json
    return json.load(f)


def to_float(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


# ----------------------------------------------------------------- fitur ----
def _rest_days(last_date, d):
    return (d - last_date).days if last_date else None


def build_feature_rows(limit=None, pending=None):
    """Bangun baris fitur untuk semua match (terurut tanggal), anti-leakage.

    Args:
        limit: batasi jumlah match terakhir (untuk eksperimen kecil).
        pending: list dict {div, date, home, away} untuk laga mendatang;
            baris fiturnya dihitung dari state SETELAH seluruh riwayat
            (bukan bocor, karena hasilnya belum ada) dan ditambahkan di akhir.
    Returns:
        list of dict: fitur pra-match + hasil (yh, ya, ftr) untuk match,
        dan tanpa hasil untuk laga pending.
    """
    xg, xg_sources = _load_xg_maps()
    from football_etl import MatchCache
    cache = MatchCache()
    matches = sorted(
        (m for m in cache.matches
         if m.get("date") and m.get("ftr") in ("H", "D", "A")),
        key=lambda m: (m["date"], m.get("div", ""), m.get("home", "")),
    )
    if limit:
        matches = matches[-limit:]

    elo = Elo()
    form = defaultdict(lambda: deque(maxlen=5))
    xg_form = defaultdict(lambda: deque(maxlen=5))  # (xgh, xga) per team
    xg_missing = defaultdict(lambda: deque(maxlen=5))
    xg_source_form = defaultdict(lambda: deque(maxlen=5))
    goals_form = defaultdict(lambda: deque(maxlen=5))  # (gf, ga) per team
    last_date = {}

    rows = []
    for m in matches:
        d = m["date"]
        home, away = m["home"], m["away"]
        yh, ya, ftr = m["yh"], m["ya"], m["ftr"]

        def _feats(team):
            f = form[team]
            g = goals_form[team]
            x = xg_form[team]
            return {
                "form_pts": (sum(pt for pt, _ in f) / len(f)) if f else None,
                "form_n": len(f),
                "goals_diff_avg": (sum(dd for _, dd in g) / len(g)) if g else None,
                "xg_diff_avg": (sum(xd for _, xd in x) / len(x)) if x else None,
                "xg_missing": (sum(xg_missing[team]) / len(xg_missing[team]))
                if xg_missing[team] else 1.0,
                "xg_source": next((s for s in reversed(xg_source_form[team])
                                    if s != "missing"), "missing"),
                "rest_days": _rest_days(last_date.get(team), d),
                "elo": elo.rating[team],
                "n_played": elo.played[team],
            }

        fh, fa = _feats(home), _feats(away)
        rows.append({
            "div": m.get("div"), "date": d.isoformat(),
            "season": m.get("season"), "home": home, "away": away,
            "yh": yh, "ya": ya, "ftr": ftr,
            "elo_h": fh["elo"], "elo_a": fa["elo"],
            "elo_diff": fh["elo"] - fa["elo"],
            "form_pts_h": fh["form_pts"], "form_pts_a": fa["form_pts"],
            "goals_diff_h": fh["goals_diff_avg"],
            "goals_diff_a": fa["goals_diff_avg"],
            "xg_diff_h": fh["xg_diff_avg"], "xg_diff_a": fa["xg_diff_avg"],
            "xg_missing_h": fh["xg_missing"], "xg_missing_a": fa["xg_missing"],
            "xg_source_h": fh["xg_source"], "xg_source_a": fa["xg_source"],
            "rest_h": fh["rest_days"], "rest_a": fa["rest_days"],
            "n_played_h": fh["n_played"], "n_played_a": fa["n_played"],
        })

        # update state SETELAH match (anti-leakage)
        elo.update(home, away, yh, ya)
        form[home].append((NORM_POINTS[ftr], 1))
        form[away].append((NORM_POINTS["H" if ftr == "A" else ("A" if ftr == "H" else "D")], 1))
        goals_form[home].append((yh, yh - ya))
        goals_form[away].append((ya, ya - yh))
        xk = (m.get("div"), d.isoformat(), home, away)
        if xk in xg:
            xgh, xga = xg[xk]
            xg_form[home].append((xgh, xgh - xga))
            xg_form[away].append((xga, xga - xgh))
            source = xg_sources.get(xk, "unknown")
            xg_missing[home].append(0.0)
            xg_missing[away].append(0.0)
            xg_source_form[home].append(source)
            xg_source_form[away].append(source)
        else:
            xg_missing[home].append(1.0)
            xg_missing[away].append(1.0)
            xg_source_form[home].append("missing")
            xg_source_form[away].append("missing")
        last_date[home] = d
        last_date[away] = d

    # Laga pending (mendatang): fitur dihitung dari state riwayat terkini.
    if pending:
        for p in pending:
            d = p["date"]
            if not isinstance(d, date):
                d = parse_date(d)
            if d is None:
                continue
            home, away = p["home"], p["away"]
            fh, fa = _feats(home), _feats(away)
            rows.append({
                "div": p.get("div"), "date": d.isoformat(),
                "season": p.get("season"), "home": home, "away": away,
                "yh": None, "ya": None, "ftr": None,
                "elo_h": fh["elo"], "elo_a": fa["elo"],
                "elo_diff": fh["elo"] - fa["elo"],
                "form_pts_h": fh["form_pts"], "form_pts_a": fa["form_pts"],
                "goals_diff_h": fh["goals_diff_avg"],
                "goals_diff_a": fa["goals_diff_avg"],
                "xg_diff_h": fh["xg_diff_avg"], "xg_diff_a": fa["xg_diff_avg"],
                "xg_missing_h": fh["xg_missing"], "xg_missing_a": fa["xg_missing"],
                "xg_source_h": fh["xg_source"], "xg_source_a": fa["xg_source"],
                "rest_h": fh["rest_days"], "rest_a": fa["rest_days"],
                "n_played_h": fh["n_played"], "n_played_a": fa["n_played"],
            })

    return rows


if __name__ == "__main__":
    import sys
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    rows = build_feature_rows(limit=limit)
    print(f"baris fitur: {len(rows)}")
    if rows:
        r = rows[-1]
        print("contoh baris terakhir:", {k: r[k] for k in
              ("date", "home", "away", "ftr", "elo_diff", "form_pts_h", "rest_h")})
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "features_history.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            w.writeheader()
            w.writerows(rows)
    print("tersimpan:", out)
