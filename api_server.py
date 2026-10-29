#!/usr/bin/env python3
"""api_server.py - REST API untuk pipeline prediksi sepakbola.

Endpoints:
  GET /api/status      - Pipeline status
  GET /api/predictions - Upcoming match predictions
  GET /api/picks       - Current picks
  GET /api/models      - Model status per league
  GET /api/odds        - Current odds data
  GET /api/corners     - Corner predictions

Usage:
  python api_server.py
  python api_server.py --port 8000
"""

import os
import sys
import json
import csv
from datetime import datetime, date, timezone
from typing import List, Dict, Optional

# Setup path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from football_etl import MatchCache, load_fd_odds, TOP5
from data_loader import get_loader
from model_state import ModelState

app = FastAPI(title="Football Prediction API", version="2.0")
loader = get_loader()
cache = MatchCache()


# --- Models ---
class Prediction(BaseModel):
    div: str
    date: str
    home: str
    away: str
    ph_dc: float
    pd_dc: float
    pa_dc: float
    ph_bl: Optional[float] = None
    pd_bl: Optional[float] = None
    pa_bl: Optional[float] = None
    p_over_dc: float
    p_over15_dc: Optional[float] = None
    p_over35_dc: Optional[float] = None
    p_over_bl: Optional[float] = None
    p_dc_1x: Optional[float] = None
    p_dc_x2: Optional[float] = None
    p_dc_12: Optional[float] = None
    p_btts: Optional[float] = None
    b365h: Optional[float] = None
    b365d: Optional[float] = None
    b365a: Optional[float] = None


class Pick(BaseModel):
    div: str
    date: str
    home: str
    away: str
    market: str
    side: str
    odds_open: float
    edge: float
    status: str


class ModelStatus(BaseModel):
    div: str
    initialized: bool
    last_fit: Optional[str] = None
    n_teams: int
    is_stale: bool


# --- Helper Functions ---
def load_predictions() -> List[Dict]:
    """Load predictions from CSV."""
    pred_file = os.path.join(BASE_DIR, "predictions_upcoming.csv")
    if not os.path.exists(pred_file):
        return []

    with open(pred_file, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def load_picks(status: str = None) -> List[Dict]:
    """Load picks from ledger.

    Status efektif pick berasal dari ledger/grades.jsonl: baris
    picks.jsonl tidak pernah di-status ulang (selamanya 'pending'),
    jadi versi lama membuat ?status=win/loss selalu kosong. Bila pick
    punya grade, statusnya = hasil grade (win/loss/push).
    """
    picks_file = os.path.join(BASE_DIR, "ledger", "picks.jsonl")
    if not os.path.exists(picks_file):
        return []

    with open(picks_file, 'r', encoding='utf-8') as f:
        picks = [json.loads(line) for line in f if line.strip()]

    grades = {}
    grades_file = os.path.join(BASE_DIR, "ledger", "grades.jsonl")
    if os.path.exists(grades_file):
        with open(grades_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    g = json.loads(line)
                    grades[g["pick_id"]] = g

    for p in picks:
        g = grades.get(p.get("pick_id"))
        if g:
            p["status"] = g.get("result", p.get("status", "pending"))
            p["ret_open"] = g.get("ret_open")
        else:
            p["status"] = "pending"

    if status:
        picks = [p for p in picks if p.get('status') == status]

    return picks


def load_corner_predictions() -> List[Dict]:
    """Load corner predictions from CSV (prefer upcoming file)."""
    corner_file = os.path.join(BASE_DIR, "predictions_corners_upcoming.csv")
    if not os.path.exists(corner_file):
        corner_file = os.path.join(BASE_DIR, "predictions_corners.csv")
    if not os.path.exists(corner_file):
        return []

    with open(corner_file, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def _sort_and_filter_upcoming(rows: List[Dict], day_key: str = "date") -> List[Dict]:
    """Urutkan (date, div, home) dan saring hanya yang belum kickoff.

    Tanggal/jam di file prediksi adalah UTC, sedangkan versi lama
    membandingkan tanggal file dengan tanggal LOKAL server (WIB):
    laga yang kickoff 00:00-07:00 WIB (tanggal UTC = kemarin) hilang
    dari API. Sekarang kickoff (date+time, UTC) dibandingkan dengan
    sekarang (UTC); baris tanpa jam jatuh ke perbandingan tanggal UTC.
    """
    now = datetime.now(timezone.utc)
    today_utc = now.date().isoformat()

    def keep(r):
        d = r.get(day_key) or ""
        t = (r.get("time") or "").strip()
        if d and t:
            try:
                hh, mm = t.split(":")[:2]
                ko = datetime.fromisoformat(d).replace(
                    hour=int(hh), minute=int(mm), tzinfo=timezone.utc)
                return ko >= now
            except (ValueError, TypeError):
                pass
        return d >= today_utc

    out = [r for r in rows if keep(r)]
    out.sort(key=lambda r: (r.get(day_key, ""), r.get("div", ""), r.get("home", "")))
    return out


def load_odds_data() -> List[Dict]:
    """Load current odds from FD raw files."""
    odds_data = []
    today = datetime.now().date()

    for div in TOP5:
        odds_map = load_fd_odds(div, "2627")
        for key, vals in odds_map.items():
            # key = (div, date_iso, home, away)
            try:
                dt = datetime.strptime(key[1], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
            if dt < today:
                continue  # hanya odds laga mendatang (variabel today
                # versi lama dihitung tapi tidak pernah dipakai, sehingga
                # endpoint mengembalikan satu musim penuh)

            entry = {
                'div': key[0],
                'date': key[1],
                'home': key[2],
                'away': key[3],
            }

            if vals.get('b365'):
                entry['b365'] = {'h': vals['b365'][0], 'd': vals['b365'][1], 'a': vals['b365'][2]}
            if vals.get('avg'):
                entry['avg'] = {'h': vals['avg'][0], 'd': vals['avg'][1], 'a': vals['avg'][2]}
            if vals.get('ou'):
                entry['over_under'] = {'over': vals['ou'][0], 'under': vals['ou'][1]}

            odds_data.append(entry)

    return odds_data


# --- Endpoints ---

@app.get("/api/status")
async def get_pipeline_status():
    """Get overall pipeline status."""
    # MatchCache segar per panggilan: singleton modul membeku pada
    # keadaan saat import sehingga bagian 'data' tidak pernah berubah
    # setelah server start. Dengan penerimaan cache berbasis stamp,
    # instans baru memakai pickle yang sama bila data belum berubah.
    fresh = MatchCache()
    status = {
        'timestamp': datetime.now().isoformat(),
        'data': {
            'total_matches': len(fresh.matches),
            'divisions': list(fresh.by_div.keys()),
        },
        'models': {},
        'predictions': {
            'exists': os.path.exists(os.path.join(BASE_DIR, 'predictions_upcoming.csv')),
            'file_size_kb': round(os.path.getsize(os.path.join(BASE_DIR, 'predictions_upcoming.csv')) / 1024, 2)
            if os.path.exists(os.path.join(BASE_DIR, 'predictions_upcoming.csv')) else 0
        },
        'picks': {},
        'cache': {}
    }

    # Model status
    for div in TOP5:
        state = ModelState(div)
        state.load()
        status['models'][div] = {
            'initialized': state._initialized,
            'last_fit': state.last_fit_date.isoformat() if state.last_fit_date else None,
            'n_teams': len(state.get_known_teams()),
            'is_stale': state.is_stale(datetime.now().date())
        }

    # Picks count
    picks_file = os.path.join(BASE_DIR, 'ledger', 'picks.jsonl')
    if os.path.exists(picks_file):
        with open(picks_file, 'r') as f:
            picks = [json.loads(line) for line in f if line.strip()]
        # Jumlah ter-grade dibaca dari grades.jsonl (status di
        # picks.jsonl sendiri tidak pernah berubah dari 'pending',
        # jadi hitungan lama selalu graded=0). Hitung ID grade yang
        # BENAR-BENAR ada di picks — menghitung baris mentah rusak
        # diam-diam bila suatu saat ada grade yatim/duplikat.
        pick_ids = {p["pick_id"] for p in picks}
        graded = 0
        grades_file = os.path.join(BASE_DIR, "ledger", "grades.jsonl")
        if os.path.exists(grades_file):
            seen = set()
            with open(grades_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        gid = json.loads(line).get("pick_id")
                        if gid in pick_ids:
                            seen.add(gid)
            graded = len(seen)
        status['picks'] = {'total': len(picks),
                           'pending': len(picks) - graded,
                           'graded': graded}
    else:
        status['picks'] = {'total': 0, 'pending': 0, 'graded': 0}

    return JSONResponse(content=status)


@app.get("/api/predictions", response_model=List[Prediction])
async def get_predictions(
    div: str = None,
    date: str = None,
    limit: int = 100
):
    """Get upcoming match predictions.

    Parameters:
      - div: Filter by division (E0, D1, I1, SP1, F1)
      - date: Filter by date (YYYY-MM-DD)
      - limit: Max results (default: 100)
    """
    rows = load_predictions()

    if div:
        rows = [r for r in rows if r.get('div') == div]

    if date:
        rows = [r for r in rows if r.get('date') == date]
    else:
        rows = _sort_and_filter_upcoming(rows)

    # Convert to proper format
    predictions = []
    for r in rows[:limit]:
        pred = {
            'div': r['div'],
            'date': r['date'],
            'home': r['home'],
            'away': r['away'],
            'ph_dc': float(r['ph_dc']) if r.get('ph_dc') else None,
            'pd_dc': float(r['pd_dc']) if r.get('pd_dc') else None,
            'pa_dc': float(r['pa_dc']) if r.get('pa_dc') else None,
            'ph_bl': float(r['ph_bl']) if r.get('ph_bl') else None,
            'pd_bl': float(r['pd_bl']) if r.get('pd_bl') else None,
            'pa_bl': float(r['pa_bl']) if r.get('pa_bl') else None,
            'p_over_dc': float(r['p_over_dc']) if r.get('p_over_dc') else None,
            'p_over15_dc': float(r['p_over15_dc']) if r.get('p_over15_dc') else None,
            'p_over35_dc': float(r['p_over35_dc']) if r.get('p_over35_dc') else None,
            'p_over_bl': float(r['p_over_bl']) if r.get('p_over_bl') else None,
            'p_dc_1x': float(r['p_dc_1x']) if r.get('p_dc_1x') else None,
            'p_dc_x2': float(r['p_dc_x2']) if r.get('p_dc_x2') else None,
            'p_dc_12': float(r['p_dc_12']) if r.get('p_dc_12') else None,
            'p_btts': float(r['p_btts']) if r.get('p_btts') else None,
            'b365h': float(r['b365h']) if r.get('b365h') else None,
            'b365d': float(r['b365d']) if r.get('b365d') else None,
            'b365a': float(r['b365a']) if r.get('b365a') else None,
        }
        predictions.append(pred)

    return JSONResponse(content=predictions)


@app.get("/api/predictions/{div}/{date_str}")
async def get_prediction_for_match(
    div: str,
    date_str: str,
    home: str,
    away: str
):
    """Get exact match prediction."""
    rows = load_predictions()

    for r in rows:
        if r['div'] == div and str(r['date']) == str(date_str) and r['home'] == home and r['away'] == away:
            return JSONResponse(content={
                'div': r['div'],
                'date': r['date'],
                'home': r['home'],
                'away': r['away'],
                'ph_dc': float(r['ph_dc']) if r['ph_dc'] else None,
                'pd_dc': float(r['pd_dc']) if r['pd_dc'] else None,
                'pa_dc': float(r['pa_dc']) if r['pa_dc'] else None,
                'ph_bl': float(r['ph_bl']) if r['ph_bl'] else None,
                'pd_bl': float(r['pd_bl']) if r['pd_bl'] else None,
                'pa_bl': float(r['pa_bl']) if r['pa_bl'] else None,
                'b365h': float(r['b365h']) if r.get('b365h') else None,
                'b365d': float(r['b365d']) if r.get('b365d') else None,
                'b365a': float(r['b365a']) if r.get('b365a') else None,
            })

    raise HTTPException(status_code=404, detail="Match not found")


@app.get("/api/picks", response_model=List[Pick])
async def get_picks(
    status: str = "pending",
    limit: int = 100
):
    """Get current picks.

    Parameters:
      - status: Filter by status (pending, win, loss, push)
      - limit: Max results
    """
    picks = load_picks(status=status)
    if status == "pending":
        picks = _sort_and_filter_upcoming(picks)
    else:
        # Pick ter-grade menurut definisi bertanggal lampau — filter
        # upcoming akan mengosongkan hasilnya. Tampilkan terbaru dulu.
        picks.sort(key=lambda r: (r.get("date", ""), r.get("div", ""),
                                  r.get("home", "")), reverse=True)

    result = []
    for p in picks[:limit]:
        result.append({
            'div': p['div'],
            'date': p['date'],
            'home': p['home'],
            'away': p['away'],
            'market': p['market'],
            'side': p['side'],
            'odds_open': float(p['odds_open']) if p.get('odds_open') else None,
            'edge': float(p['edge']) if p.get('edge') else None,
            'status': p.get('status', 'pending')
        })

    return JSONResponse(content=result)


@app.get("/api/models")
async def get_models():
    """Get model status for all TOP5 leagues."""
    models = []
    for div in TOP5:
        state = ModelState(div)
        state.load()
        models.append({
            'div': div,
            'initialized': state._initialized,
            'last_fit': state.last_fit_date.isoformat() if state.last_fit_date else None,
            'n_teams': len(state.get_known_teams()),
            'n_matches_trained': state.n_matches_trained,
            'rho': state.rho,
            'home_advantage': round(state.home_advantage, 4) if state.home_advantage else None,
            'is_stale': state.is_stale(datetime.now().date())
        })
    return JSONResponse(content=models)


@app.get("/api/models/{div}/teams")
async def get_model_teams(div: str):
    """Get team ratings for a specific division."""
    if div not in TOP5:
        raise HTTPException(status_code=404, detail=f"Division {div} not in TOP5")

    state = ModelState(div)
    if not state.load():
        raise HTTPException(status_code=404, detail=f"No model state for {div}")

    teams = []
    for team in state.get_known_teams():
        teams.append({
            'team': team,
            'attack': round(state.attack.get(team, 0), 4),
            'defense': round(state.defense.get(team, 0), 4)
        })

    return JSONResponse(content={
        'div': div,
        'n_teams': len(teams),
        'teams': teams
    })


@app.get("/api/odds")
async def get_odds(div: str = None):
    """Get current odds data.

    Parameters:
      - div: Filter by division (optional)
    """
    odds = load_odds_data()
    if div:
        odds = [o for o in odds if o['div'] == div]
    return JSONResponse(content=odds)


def _f(v):
    """Safe float parse; returns None for empty/invalid values."""
    try:
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


@app.get("/api/corners")
async def get_corner_predictions(div: str = None, limit: int = 100):
    """Get upcoming corner predictions.

    Schema (predictions_corners_upcoming.csv):
      div, date, home, away, rec_line, rec_side, recommendation, rec_prob,
      p_gt_6.5 ... p_gt_11.5 (P(total corners > line))
    """
    rows = load_corner_predictions()
    rows = _sort_and_filter_upcoming(rows)

    if div:
        rows = [r for r in rows if r.get('div') == div]

    predictions = []
    for r in rows[:limit]:
        # dynamic over-probabilities: p_gt_9.5 -> prob_over["9.5"]
        prob_over = {
            k[len('p_gt_'):]: v
            for k, v in r.items()
            if k.startswith('p_gt_') and _f(v) is not None
        }
        predictions.append({
            'div': r.get('div', ''),
            'date': r.get('date', ''),
            'home': r.get('home', ''),
            'away': r.get('away', ''),
            'rec_line': _f(r.get('rec_line')),
            'rec_side': r.get('rec_side', ''),
            'recommendation': r.get('recommendation', ''),
            'rec_prob': _f(r.get('rec_prob')),
            'prob_over': prob_over,
        })

    return JSONResponse(content=predictions)


@app.get("/api/health")
async def health_check():
    """Simple health check."""
    return JSONResponse(content={
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


# --- Main ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
