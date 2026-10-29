#!/usr/bin/env python3
"""market_orchestration.py — orkestrasi markets tipsterarea (prompt orkestrasi).

Pekerjaan:
  1. model_fixture_ids(days): game_id fixture model (liga + piala) dalam jendela
     tanggal — dipakai fase markets di run_daily_shadow.py (sync_dates
     with_markets=True, market_ids ini). Throttle market_needs_refresh diurus
     sync_dates; kegagalan jaringan ditangani pemanggil (warning, bukan gagal).
  2. build_market_compare(): join odds pasar per fixture model upcoming ->
     market_compare.csv. Per pasar/garis/pilihan: odds 1xbet + median antar
     bandar + prob implied ternormalisasi (proporsional, konvensi ta_model).
     Snapshot lenkap -> kolom kosong, tidak difabrikasi.
  3. archive_snapshots(date): salin output harian ke archive/<date>/ (idempoten).
  4. sync_cup_picks_to_ledger(): rutekan pick piala (best_picks_today,
     ber-label kompetisi) ke ledger/picks.jsonl dgn competition=EFL Cup/DFB
     Pokal, odds_open = snapshot ta terakhir sebelum kickoff. Hanya pasar yang
     bisa di-settle score_ledger (1X2/OU) yang dimasukkan.
"""
import csv
import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.join(HERE, "ta")
LEDGER = os.path.join(HERE, "ledger")
PICKS = os.path.join(LEDGER, "picks.jsonl")
ARCHIVE = os.path.join(HERE, "archive")

from ta_model import norm, sim

# ----- label pasar di snapshot vs kanonik -----
MARKET_CANON = {
    "Standard 1X2": "1X2", "Double Chance": "DC", "Draw No Bet": "DNB",
    "Over/Under": "OU", "BTS": "BTS", "BTTS": "BTS",
    "Both Teams To Score": "BTS",
}
# grid pasar yang dilaporkan: market -> [(line, (pilihan,...))]
MARKET_GRID = {
    "1X2": [("", ("1", "X", "2"))],
    "DC": [("", ("1X", "12", "X2"))],
    "DNB": [("", ("Dnb1", "Dnb2"))],
    "OU": [("1.5", ("Over", "Under")), ("2.5", ("Over", "Under")),
           ("3.5", ("Over", "Under"))],
    "BTS": [("", ("Yes", "No"))],
}

CUP_LEAGUE = {"EFL Cup": "England - EFL Cup", "DFB Pokal": "Germany - Cup Germany"}
DIV_LEAGUE = {"E0": "Premier League", "D1": "Bundesliga", "I1": "Serie A",
              "SP1": "La Liga", "F1": "Ligue 1", "D2": "2. Bundesliga"}


def _read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def _fnum(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def _iso(d):
    return d.isoformat() if hasattr(d, "isoformat") else str(d)


def _parsedate(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- fixtures
def _load_fixtures():
    """Balik (by_id, idx) idx: (norm_home, norm_away) -> list fixture."""
    rows = _read_csv(os.path.join(TA, "fixtures.csv"))
    by_id = {}
    idx = {}
    for r in rows:
        gid = r.get("game_id")
        if not gid:
            continue
        by_id[gid] = r
        key = (norm(r.get("home") or ""), norm(r.get("away") or ""))
        idx.setdefault(key, []).append(r)
    return by_id, idx


def _match_game_id(home, away, date_iso, league_hint=None):
    """Cocokkan fixture di tanggal sama; fallback ±1 hari + kemiripan nama."""
    _, idx = _load_fixtures()
    key = (norm(home), norm(away))
    cands = idx.get(key, [])
    same = [c for c in cands if c.get("date") == date_iso]
    pool = same or [c for c in cands if _parsedate(c.get("date")) and
                    abs((_parsedate(c["date"]) - _parsedate(date_iso)).days) <= 1]
    if league_hint:
        hinted = [c for c in pool if league_hint.lower() in (c.get("league") or "").lower()]
        if hinted:
            pool = hinted
    if not pool:
        return None
    if len(pool) == 1:
        return pool[0]["game_id"]
    # multi-kandidat: pilih paling mirip (tanggal + nama)
    best, bs = None, -1.0
    d0 = _parsedate(date_iso)
    for c in pool:
        ds = abs((_parsedate(c.get("date")) - d0).days) if d0 else 0
        sc = sim(key[0], norm(c.get("home") or "")) * sim(key[1], norm(c.get("away") or ""))
        score = sc - 0.1 * ds
        if score > bs:
            bs, best = score, c
    return best["game_id"] if best else None


def _fixture_league_hint(div, competition):
    if competition:
        return CUP_LEAGUE.get(competition)
    return DIV_LEAGUE.get(div)


def model_fixture_ids(days, date_from=None):
    """game_id semua fixture model (liga + piala) dalam jendela [min,max] hari.

    Diurutkan menurut kickoff (tanggal, jam) naik — depan = kickoff terdekat.
    """
    lo, hi = min(days), max(days)
    ids = []
    seen = set()
    sources = [
        ("predictions_upcoming.csv", None),
        ("predictions_cups_upcoming.csv", None),
    ]
    for fn, _ in sources:
        for r in _read_csv(os.path.join(HERE, fn)):
            d = _parsedate(r.get("date"))
            if not d or not (lo <= d <= hi):
                continue
            hint = _fixture_league_hint(r.get("div", ""), r.get("competition", ""))
            gid = _match_game_id(r.get("home", ""), r.get("away", ""),
                                 r.get("date", ""), hint)
            if gid and gid not in seen:
                seen.add(gid)
                ids.append(gid)
    if not ids:
        return ids
    by_id, _ = _load_fixtures()
    def kickoff(gid):
        f = by_id.get(gid) or {}
        return (f.get("date") or "", f.get("time") or "")
    return sorted(ids, key=kickoff)


# ---------------------------------------------------------------- snapshots
def _prematch_state(game_id):
    """Keadaan pra-laga paling segar per bandar utk game_id.

    Merangkum SEMUA snapshot sebelum kickoff: utk tiap (bookmaker, pasar,
    garis, pilihan) diambil odds TERAKHIR. Jadi satu snapshot parsial (hanya
    sebagian bandar) tidak menghilangkan harga bandar lain yang lebih lengkap.
    Return (latest_captured_at, state) dgn state[(market,line,selection)] ->
    [(odds, bookmaker), ...] (satu baris per bookmaker).
    """
    rows = [r for r in _read_csv(os.path.join(TA, "odds_markets_snapshots.csv"))
            if r.get("game_id") == game_id]
    if not rows:
        return None, {}
    latest = {}
    for r in rows:
        market = MARKET_CANON.get(r.get("market") or "")
        if not market:
            continue
        sel = r.get("selection") or ""
        if market == "OU" and sel not in ("Over", "Under"):
            continue  # baris 'Goals' dst = noise
        o = _fnum(r.get("odds"))
        if not o or o <= 1.0:
            continue
        key = (market, str(r.get("line") or ""), sel, r.get("bookmaker") or "")
        cap = r.get("captured_at") or ""
        cur = latest.get(key)
        if cur is None or cap > cur[0]:
            latest[key] = (cap, o)
    state = {}
    for (market, line, sel, bk), (cap, o) in latest.items():
        state.setdefault((market, line, sel), []).append((o, bk))
    cap = max(r.get("captured_at") or "" for r in rows)
    return cap, state


def _state_prices(state, market, line, selection):
    return state.get((market, str(line), selection), [])


def _median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


def _implied_median(state, market, line, selection):
    """Prob implied proporsional (median odds antar bandar) per sisi pasar."""
    group = None
    for ln, sels in MARKET_GRID.get(market, []):
        if str(ln) == str(line) and selection in sels:
            group = (ln, sels)
            break
    if group is None:
        return None
    _, sels = group
    med = {}
    for s in sels:
        pr = _state_prices(state, market, line, s)
        m = _median([o for o, _ in pr])
        if m is None:
            return None
        med[s] = m
    inv = {s: 1.0 / m for s, m in med.items()}
    tot = sum(inv.values())
    if tot <= 0:
        return None
    return inv[selection] / tot


# ---------------------------------------------------------------- market_compare
MARKET_COMPARE_COLS = ["div", "date", "home", "away", "game_id", "competition",
                       "market", "line", "selection", "o_1xbet", "o_median",
                       "p_implied", "n_bookies", "captured_at"]


def build_market_compare(date_from=None, n_days=5):
    """Tulis market_compare.csv utk fixture model upcoming (window dekat)."""
    today = date_from or date.today()
    lo = today
    hi = today + timedelta(days=n_days - 1)
    out = []
    sources = [
        ("predictions_upcoming.csv", "", "div"),
        ("predictions_cups_upcoming.csv", "competition", "div"),
    ]
    n_fix = 0
    for fn, comp_col, div_col in sources:
        for r in _read_csv(os.path.join(HERE, fn)):
            d = _parsedate(r.get("date"))
            if not d or not (lo <= d <= hi):
                continue
            comp = r.get(comp_col) if comp_col else ""
            hint = _fixture_league_hint(r.get("div", ""), comp)
            gid = _match_game_id(r.get("home", ""), r.get("away", ""),
                                 r.get("date", ""), hint)
            if not gid:
                continue
            n_fix += 1
            cap, state = _prematch_state(gid)
            for market, grid in MARKET_GRID.items():
                for line, sels in grid:
                    for sel in sels:
                        pr = _state_prices(state, market, line, sel)
                        o1 = next((o for o, b in pr if b == "1xbet"), None)
                        omed = _median([o for o, _ in pr])
                        pim = _implied_median(state, market, line, sel) if state else None
                        out.append({
                            "div": r.get("div", ""), "date": r.get("date", ""),
                            "home": r.get("home", ""), "away": r.get("away", ""),
                            "game_id": gid, "competition": comp,
                            "market": market, "line": line, "selection": sel,
                            "o_1xbet": o1 if o1 else "",
                            "o_median": round(omed, 3) if omed else "",
                            "p_implied": round(pim, 4) if pim is not None else "",
                            "n_bookies": len(pr),
                            "captured_at": cap or "",
                        })
    _write_csv(os.path.join(HERE, "market_compare.csv"),
               MARKET_COMPARE_COLS, out)
    return {"fixtures": n_fix, "rows": len(out)}


# ---------------------------------------------------------------- archive
ARCHIVE_FILES = ["predictions_upcoming.csv", "predictions_corners_upcoming.csv",
                 "predictions_cups_upcoming.csv", "predictions_corners_cups.csv",
                 "best_picks_today.csv", "market_compare.csv",
                 "recommended_slip.csv"]


def archive_snapshots(target_date=None):
    """Salin output harian ke archive/<date>/. Idempoten per tanggal."""
    d = target_date or date.today()
    dest = os.path.join(ARCHIVE, d.isoformat())
    os.makedirs(dest, exist_ok=True)
    copied = []
    for fn in ARCHIVE_FILES:
        src = os.path.join(HERE, fn)
        if os.path.exists(src):
            out = os.path.join(dest, fn)
            with open(src, "rb") as fi, open(out, "wb") as fo:
                fo.write(fi.read())
            copied.append(fn)
    return {"date": d.isoformat(), "archived": copied}


# ---------------------------------------------------------------- cup picks -> ledger
def _cup_pick_file_sources():
    """best_picks_today.csv kini + arsip (ber-label kompetisi)."""
    paths = [os.path.join(HERE, "best_picks_today.csv")]
    if os.path.isdir(ARCHIVE):
        for d in sorted(os.listdir(ARCHIVE)):
            p = os.path.join(ARCHIVE, d, "best_picks_today.csv")
            if os.path.exists(p):
                paths.append(p)
    return paths


def sync_cup_picks_to_ledger():
    """Masukkan pick piala ke picks.jsonl (competition=EFL Cup/DFB Pokal)."""
    existing = set()
    if os.path.exists(PICKS):
        with open(PICKS, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    existing.add(json.loads(line)["pick_id"])
    os.makedirs(LEDGER, exist_ok=True)
    new = []
    for p in _cup_pick_file_sources():
        for r in _read_csv(p):
            comp = r.get("competition") or ""
            if comp not in CUP_LEAGUE:
                continue
            market = r.get("market") or ""
            if market not in ("1X2", "OU"):
                continue  # settle score_ledger hanya 1X2/OU
            side = r.get("side") or ""
            line = r.get("line") or ""
            d = r.get("date") or ""
            home, away = r.get("home") or "", r.get("away") or ""
            if not (d and home and away and side):
                continue
            pid = hashlib.md5(
                f"{comp}|{d}|{home}|{away}|{market}|{line}|{side}".encode()
            ).hexdigest()[:16]
            if pid in existing:
                continue
            gid = _match_game_id(home, away, d, CUP_LEAGUE[comp])
            cap, state = _prematch_state(gid) if gid else (None, {})
            pr = _state_prices(state, market, line, side) if state else []
            odds = _median([o for o, _ in pr])
            if not odds:
                continue  # tanpa harga tak bisa settle — lewati
            pm = _fnum(r.get("prob"))
            if pm is None:
                continue
            new.append({
                "pick_id": pid, "ts_created": datetime.utcnow().isoformat() + "Z",
                "model": "cup-proxy", "thr": 0.0, "status": "pending",
                "market": market, "side": side, "line": line,
                "p_model": round(pm, 4), "odds_open": round(odds, 4),
                "p_imp_open": round(1.0 / odds, 4),
                "edge": round(pm - 1.0 / odds, 4),
                "competition": comp, "div": r.get("div") or "", "date": d,
                "home": home, "away": away,
            })
            existing.add(pid)
    if new:
        with open(PICKS, "a", encoding="utf-8") as f:
            for rec in new:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return len(new)


def main(argv):
    if "--market-compare" in argv:
        r = build_market_compare()
        print(f"market_compare: {r['fixtures']} fixture, {r['rows']} baris")
        return 0
    if "--archive" in argv:
        r = archive_snapshots()
        print(f"archive {r['date']}: {r['archived']}")
        return 0
    if "--cup-ledger" in argv:
        n = sync_cup_picks_to_ledger()
        print(f"cup picks -> ledger: {n} baru")
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
