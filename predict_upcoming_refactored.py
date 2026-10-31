#!/usr/bin/env python3
"""predict_upcoming_refactored.py — Refactored upcoming prediction using cached data.

Dapat dipanggil oleh pipeline_orchestrator.py.
Menggunakan:
- MatchCache untuk load historical matches (pickle, ~10x lebih cepat)
- ModelState untuk reuse rating tim (hindari refit penuh tiap kali)
- data_loader.MatchLoader singleton untuk akses terpusat
- football_etl shared utilities (tau, pois, blend functions)
"""

import os
import sys
import csv
import json
import time
import tempfile
from datetime import datetime, date
from collections import defaultdict
from typing import Dict, List, Tuple, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from football_etl import (
    get_config, load_fixtures, load_fd_odds, normalize_name, TOP5
)
from data_loader import get_loader
from model_state import ModelState
from model_v2 import DC, norm3, norm2, blend3, blend2, xg_key  # Reuse existing implementation
from features import build_feature_rows, _load_xg_map
import model_features_1x2 as mf  # shadow T3 (fitur), side-by-side


def generate_predictions(force_refit: bool = False, output_file: str = None) -> dict:
    """Generate predictions for upcoming fixtures.

    Args:
        force_refit: Force model refit even if cached state is fresh
        output_file: Custom output path (default: predictions_upcoming.csv)

    Returns:
        dict with keys: 'predictions', 'n_fixtures', 'n_with_odds', 'errors'
    """
    t0 = time.time()
    loader = get_loader()
    cfg = get_config()
    HL = cfg.get('hl', 270.0)
    W12 = cfg.get('w_1x2', 0.05)
    WOU = cfg.get('w_ou', 0.05)

    output_file = output_file or os.path.join(BASE_DIR, "predictions_upcoming.csv")

    # Load fixtures
    fixtures = load_fixtures("2026")
    if not fixtures:
        # Fallback to direct loading
        fixtures = _load_fixtures_from_raw()

    if not fixtures:
        return {'status': 'error', 'error': 'No upcoming fixtures found', 'predictions': []}

    # Load odds from FD raw
    odds = _load_fd_odds(TODAY := datetime.now().date())

    print(f"  Loaded {len(fixtures)} fixtures, {len(odds)} odds entries")

    # --- T3 (fitur): kolomnya disajikan di predictions_upcoming.csv dan
    # wajib bagi stack meta di make_picks_live. Kegagalannya dulu ditelan
    # diam-diam sehingga status tetap 'success' (audit GPT 2026-10-31, H):
    # sekarang status T3 dilaporkan eksplisit ke pemanggil.
    t3_map = {}
    t3_status = "ok"
    t3_error = None
    try:
        pend = []
        for fx in fixtures:
            d = fx["date"]
            if isinstance(d, str):
                d = datetime.strptime(d[:10], "%Y-%m-%d").date()
            elif hasattr(d, "date") and not isinstance(d, date):
                d = d.date()
            pend.append({"div": fx["div"], "date": d,
                         "home": fx["home"], "away": fx["away"]})
        hist_plus = build_feature_rows(limit=None, pending=pend)
        pen = len(pend)
        hist = hist_plus[:-pen] if pen else hist_plus
        pend_rows = hist_plus[-pen:] if pen else []
        Xh, yh, _ = mf._rows_to_arrays(hist)
        if len(yh) >= 500:
            model3 = mf.FitModel(Xh, yh)
            for fx, pf in zip(pend, pend_rows):
                px = model3.predict_vector(pf)
                ds = fx["date"].isoformat() if isinstance(fx["date"], date) else str(fx["date"])
                t3_map[(fx["div"], ds, fx["home"], fx["away"])] = px
            print(f"  T3 siap untuk {len(t3_map)} fixtures")
        else:
            t3_status = "skipped"
            print("  ! T3 dilewati: data riwayat terlalu sedikit")
    except Exception as e:
        t3_status = "failed"
        t3_error = repr(e)
        print(f"  ! T3 GAGAL (kolom T3 kosong, status dilaporkan): {e}")

    # Process fixtures per division
    out_rows = []
    n_with_odds = 0
    errors = []

    # Group fixtures by (div, year, month) for walk-forward fitting
    groups = defaultdict(list)
    for fx in fixtures:
        d = fx["date"]
        if hasattr(d, 'strftime'):
            # It's a date object
            yy, mm = d.year, d.month
        else:
            # It's a string
            yy, mm = int(d[:4]), int(d[5:7])
        groups[(fx["div"], yy, mm)].append(fx)

    # Map xG + riwayat per divisi dimuat SEKALI di luar loop grup:
    # sebelumnya _load_xg_map() mem-parse ulang ~18k baris CSV untuk
    # setiap grup (divisi x bulan) — ~40x kerja redundan per run.
    xg_map = _load_xg_map()
    _hist_by_div = {}
    for (div, yy, mm), fxs in sorted(groups.items()):
        start_d = min(x["date"] for x in fxs)
        if hasattr(start_d, 'isoformat'):
            start = start_d if isinstance(start_d, date) else start_d.date()
        else:
            start = datetime.strptime(start_d, "%Y-%m-%d").date()

        # Get historical matches for this division before this fixture date
        hist_matches = _hist_by_div.setdefault(
            div, loader.get_matches_by_div(div))
        games = [(m['home'], m['away'], m['yh'], m['ya'],
                  xg_map.get(xg_key(div, m['date'], m['home'], m['away']), (None, None))[0],
                  xg_map.get(xg_key(div, m['date'], m['home'], m['away']), (None, None))[1],
                  m['date'])
                for m in hist_matches
                if m.get('date') and m['date'] < start
                and m.get('yh') is not None and m.get('ya') is not None
                and m.get('ftr') in ('H', 'D', 'A')]

        if not games:
            errors.append(f"{div} {yy}-{mm}: no history")
            continue

        # Get or fit model
        model, state = _get_or_fit_model(loader, div, games, start, HL, force_refit)

        for fx in fxs:
            try:
                # Normalize team names to match training data format
                home_norm = normalize_name(fx["home"])
                away_norm = normalize_name(fx["away"])
                lh, la = model._lam(home_norm, away_norm)
                pr = model.probs(lh, la)

                d = fx["date"]
                date_str = d.isoformat() if hasattr(d, 'isoformat') else str(d)
                o = odds.get((div, date_str, fx["home"], fx["away"])) or {}
                mo, mou = _open1x2(o), _open_ou(o)
                n_with_odds += 1 if mo else 0

                pb = blend3((pr['ph'], pr['pd'], pr['pa']), mo, W12) if mo else None
                pob = blend2(pr['over'], mou, WOU) if mou is not None else None

                oH, oD, oA = o.get('B365H'), o.get('B365D'), o.get('B365A')
                px = t3_map.get((div, date_str, fx["home"], fx["away"]))
                out_rows.append({
                    "div": div, "date": date_str, "time": fx.get('time', ''),
                    "home": fx["home"], "away": fx["away"],
                    "lam_h": round(lh, 3), "lam_a": round(la, 3),
                    "ph_dc": round(pr['ph'], 4), "pd_dc": round(pr['pd'], 4),
                    "pa_dc": round(pr['pa'], 4),
                    "ph_t3": None if px is None else round(px[0], 4),
                    "pd_t3": None if px is None else round(px[1], 4),
                    "pa_t3": None if px is None else round(px[2], 4),
                    "ph_bl": None if pb is None else round(pb[0], 4),
                    "pd_bl": None if pb is None else round(pb[1], 4),
                    "pa_bl": None if pb is None else round(pb[2], 4),
                    "p_over_dc": round(pr['over'], 4),
                    "p_over15_dc": round(pr.get('over15', pr['over']), 4),
                    "p_over35_dc": round(pr.get('over35', pr['over']), 4),
                    "p_over_bl": None if pob is None else round(pob, 4),
                    "p_btts": round(pr.get('btts', 0), 4),
                    "p_dc_1x": round(pr['ph'] + pr['pd'], 4),
                    "p_dc_x2": round(pr['pd'] + pr['pa'], 4),
                    "p_dc_12": round(pr['ph'] + pr['pa'], 4),
                    "b365h": oH, "b365d": oD, "b365a": oA,
                    "b365o25": o.get('B365>2.5'),
                })
            except Exception as e:
                errors.append(f"{div} {fx['home']} vs {fx['away']}: {str(e)}")

    # Write output
    if out_rows:
        # Publish only a complete CSV; API readers can run concurrently with
        # the pipeline.
        out_dir = os.path.dirname(os.path.abspath(output_file))
        fd, tmp_path = tempfile.mkstemp(
            prefix=f".{os.path.basename(output_file)}.", suffix=".tmp",
            dir=out_dir)
        try:
            with os.fdopen(fd, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
                w.writeheader()
                w.writerows(out_rows)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, output_file)
        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

    runtime = time.time() - t0
    # Status jujur: versi lama selalu 'success' walau sebagian fixture
    # gagal diam-diam (errors tidak pernah dibaca pemanggil) dan file
    # output tidak ditimpa bila out_rows kosong, sehingga file basi
    # terkonsumsi sebagai data segar. Run normal menghasilkan 0 errors,
    # jadi 'partial' hanya muncul saat memang ada yang hilang.
    if fixtures and not out_rows:
        status = 'error'
    elif errors:
        status = 'partial'
    else:
        status = 'success'
    return {
        'status': status,
        't3_status': t3_status,
        't3_error': t3_error,
        'predictions': out_rows,
        'n_fixtures': len(fixtures),
        'n_with_odds': n_with_odds,
        'n_output_rows': len(out_rows),
        'errors': errors,
        'runtime_seconds': round(runtime, 2)
    }


def _get_or_fit_model(loader, div: str, games: list, cutoff: date,
                      hl: float, force: bool = False) -> Tuple[DC, ModelState]:
    """Get cached model or fit new one.

    Prioritaskan model state yang sudah ada. Hanya fit ulang jika:
    - Force fit (force=True)
    - State belum pernah di-fit
    - State lebih tua dari 7 hari
    - Ada tim baru yang belum dikenal

    Uses ModelState to store/load model ratings and avoid full refit.
    """
    state = ModelState(div)
    was_loaded = state.load()

    needs_fit = force or not was_loaded or not state._initialized or state.mode_mismatch()
    if was_loaded and state.half_life is not None:
        # State yang di-fit dengan half-life berbeda dari konfigurasi
        # aktif tidak boleh dipakai diam-diam (pola yang sama seperti
        # mode_mismatch untuk DC_FIT_MODE, tapi dulu hanya mode yang
        # diperiksa — audit ulang 2026-10-29).
        try:
            if abs(float(state.half_life) - float(hl)) > 1e-9:
                needs_fit = True
        except (TypeError, ValueError):
            pass

    if was_loaded and state.data_stale():
        # Data gol/xG berubah sejak state di-fit (koreksi skor, xG
        # terisi belakangan): cache tidak boleh dipakai diam-diam
        # (audit GPT 2026-10-31, C).
        needs_fit = True

    if was_loaded and state.last_fit_date and not needs_fit:
        # Check if new games since last fit
        days_since_fit = abs((cutoff - state.last_fit_date).days)
        needs_fit = days_since_fit > 7

        # Check for unknown teams (only check teams in recent fixtures, not all)
        known = state.get_known_teams()
        # Get teams from all games (not just recent)
        all_teams = set(g[0] for g in games) | set(g[1] for g in games)
        unknown = all_teams - known
        # If >20% of teams unknown, refit
        if len(all_teams) > 0 and len(unknown) > len(all_teams) * 0.2:
            needs_fit = True

    if needs_fit:
        print(f"    Fitting model for {div} (cutoff: {cutoff})")
        model = DC()
        model.fit(games[-4000:], cutoff, hl)
        state.update_from_model(model, cutoff, hl)
    else:
        # Reconstruct model from state - use existing cached ratings
        model = _model_from_state(state)
        print(f"    Using cached model for {div} (fit: {state.last_fit_date})")

    return model, state


def _model_from_state(state: ModelState) -> DC:
    """Reconstruct DC model from persisted state."""
    model = DC()
    # defaultdict, BUKAN dict biasa: DC._lam mengindeks dengan [] dan
    # tim yang absen dari state (mis. tim promosi sebelum refit mingguan)
    # dulu melempar KeyError yang tertelan per-fixture sehingga baris
    # prediksinya hilang diam-diam. Rating netral 0.0 adalah semantik
    # yang sama seperti jalur fit segar (DC.a/DC.d memang defaultdict).
    model.a = defaultdict(float, state.attack)
    model.d = defaultdict(float, state.defense)
    model.h = state.home_advantage
    model.rho = state.rho
    return model


def _load_fixtures_from_raw() -> List[Dict]:
    """Load fixtures from xg_raw JSON files (fallback)."""
    FIX_MAP = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
               "I1": "Serie_A", "F1": "Ligue_1"}
    from datetime import timezone as _tz
    TODAY = datetime.now(_tz.utc).date()
    # Samakan disiplin prematch loader utama (audit GPT 2026-10-31, A):
    # fallback tidak boleh menghidupkan lagi laga selesai/sudah kickoff.
    NOW_UTC = datetime.now(_tz.utc).replace(tzinfo=None)

    # Load name mapping
    nmap_path = os.path.join(BASE_DIR, "xg_raw", "map_full.json")
    nmap = {}
    if os.path.exists(nmap_path):
        with open(nmap_path, encoding="utf-8") as f:
            nmap = json.load(f)

    fixtures = []
    for div, slug in FIX_MAP.items():
        p = os.path.join(BASE_DIR, "xg_raw", f"{slug}_2026_fixtures.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            try:
                if d.get("isResult"):
                    continue
                dt = datetime.strptime(d["datetime"], "%Y-%m-%d %H:%M:%S")
                if dt <= NOW_UTC:
                    continue
                if dt.date() < TODAY:
                    continue
                home = nmap.get(f"{div}|{d['h']['title']}")
                away = nmap.get(f"{div}|{d['a']['title']}")
                if not home or not away:
                    continue
                # Samakan dengan jalur utama: nama ternormalisasi.
                # Nilai map mentah ("Man City", "M'gladbach") membuat
                # lookup odds FD meleset total dan kolom B365 kosong
                # diam-diam bila fallback ini aktif (audit ronde 3).
                home, away = normalize_name(home), normalize_name(away)
                fixtures.append(dict(
                    div=div, uid=d["id"], date=dt.date().isoformat(),
                    time=dt.strftime("%H:%M"), home=home, away=away
                ))
            except (ValueError, KeyError):
                continue

    fixtures.sort(key=lambda x: (x["date"], x["div"], x["home"]))
    return fixtures


def _load_fd_odds(today: date) -> Dict[Tuple, Dict]:
    """Load odds from football-data raw CSVs.

    Format output sama dengan load_fd_odds di football_etl.py:
    key = (div, date_iso, home_norm, away_norm)
    value = {
        'b365': (h, d, a),
        'avg': (h, d, a),
        'ou': (over, under),
        'b365_ou': (over, under)
    }
    """
    odds = {}
    for div in TOP5:
        div_odds = load_fd_odds(div, "2627")
        for key, vals in div_odds.items():
            # Filter by date
            dt_str = key[1]
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            # Load all odds - date filtering happens in prediction matching
            # Convert to flat odds format for predict_upcoming compatibility
            flat = {}
            if vals.get('b365'):
                flat['B365H'], flat['B365D'], flat['B365A'] = vals['b365']
            if vals.get('avg'):
                flat['AvgH'], flat['AvgD'], flat['AvgA'] = vals['avg']
            if vals.get('ou'):
                flat['Avg>2.5'], flat['Avg<2.5'] = vals['ou']
            if vals.get('b365_ou'):
                flat['B365>2.5'], flat['B365<2.5'] = vals['b365_ou']
            odds[key] = flat
    return odds


def _open1x2(o: Dict) -> Optional[Tuple]:
    """Extract normalized 1X2 odds."""
    for pre in ("Avg", "B365"):
        h, d, a = o.get(pre + "H"), o.get(pre + "D"), o.get(pre + "A")
        if h and d and a:
            return norm3((h, d, a))
    return None


def _open_ou(o: Dict) -> Optional[Tuple]:
    """Extract normalized O/U odds."""
    for over, under in (("Avg>2.5", "Avg<2.5"), ("B365>2.5", "B365<2.5")):
        ov, un = o.get(over), o.get(under)
        if ov and un:
            return norm2((ov, un))
    return None


if __name__ == "__main__":
    result = generate_predictions()
    print(json.dumps(result, indent=2, default=str))
