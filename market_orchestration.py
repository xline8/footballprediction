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
  3. archive_snapshots(date): salin output harian ke archive/<date>/ (write-once per file).
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
from datetime import date, datetime, timedelta, timezone

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


def _capdt(s):
    """Parse captured_at untuk perbandingan 'terbaru' (string mentah
    salah urutan lintas offset +0000/+0700)."""
    try:
        return datetime.strptime(s or "", "%Y-%m-%dT%H:%M:%S%z")
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)


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
        # Jendela ±2 hari, HANYA untuk kunci nama eksak di kedua sisi
        # (idx dibangun dari pasangan nama ternormalisasi yang sama —
        # jangkar terkuat) dan hanya bila kandidatnya unik setelah
        # filter hint liga. Kasus nyata: Lorient vs Brest — model
        # 31 Okt (dump Understat) vs TA 2 Nov — selisih 2 hari sehingga
        # tak pernah terjodohkan dan laga kehilangan data pasarnya
        # (audit ronde 8). Penyelamatan fuzzy di bawah tetap ±1 hari:
        # varian nama pada jarak 2 hari terlalu berisiko wrong-twin.
        wide = [c for c in cands if _parsedate(c.get("date")) and
                abs((_parsedate(c["date"]) - _parsedate(date_iso)).days) <= 2]
        if league_hint:
            hinted_w = [c for c in wide
                        if league_hint.lower() in (c.get("league") or "").lower()]
            if hinted_w:
                wide = hinted_w
        if len(wide) == 1:
            return wide[0]["game_id"]
    if not pool:
        # Penyelamatan fuzzy: kunci eksak melewatkan varian nama
        # (Nottm Forest vs Nottingham, Internazionale vs Inter Milan)
        # — fixture-nya ADA di TA tapi tak pernah masuk pool, sehingga
        # laga kehilangan data pasar + kelayakan slip (audit ronde 5:
        # 5 dari 10 prediksi unmatched adalah kasus ini). Syarat ketat
        # agar tidak menciptakan wrong-twin baru: satu sisi harus sama
        # persis setelah norm (jangkar), sisi lain sim >= 0.85, dan
        # skor gabungan (formula yang sama, penalti 0.1/hari) >= 0.80.
        # Kandidat ber-hint liga didahulukan bila ada yang lolos.
        by_id, _ = _load_fixtures()
        d0 = _parsedate(date_iso)
        if d0 is None:
            return None
        nh, na = norm(home), norm(away)
        winners = []
        for c in by_id.values():
            cd = _parsedate(c.get("date"))
            if cd is None or abs((cd - d0).days) > 1:
                continue
            ch, ca = norm(c.get("home") or ""), norm(c.get("away") or "")
            if nh == ch:
                other = sim(na, ca)
            elif na == ca:
                other = sim(nh, ch)
            else:
                continue
            if other < 0.85:
                continue
            sc = sim(nh, ch) * sim(na, ca) - 0.1 * abs((cd - d0).days)
            if sc >= 0.80:
                winners.append((sc, c))
        if not winners:
            return None
        if league_hint:
            hinted = [(s, c) for s, c in winners
                      if league_hint.lower() in (c.get("league") or "").lower()]
            if hinted:
                winners = hinted
        winners.sort(key=lambda t: t[0], reverse=True)
        return winners[0][1]["game_id"]
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
            # Baris piala membawa game_id TA-nya sendiri (predict_cups):
            # dahulukan id tersimpan, fuzzy hanya untuk baris liga.
            gid = (r.get("game_id") or "").strip() or _match_game_id(
                r.get("home", ""), r.get("away", ""), r.get("date", ""), hint)
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
    # Filter pra-kickoff (audit ulang 2026-10-29): docstring fungsi ini
    # selalu mengklaim "snapshot sebelum kickoff", tapi versi lama tidak
    # pernah membandingkan captured_at dengan kickoff — ~39% baris
    # snapshot tertangkap setelah kickoff (harga live) dan bisa menjadi
    # "odds prematch" di market_compare maupun odds_open pick piala di
    # ledger. Tanggal/jam fixture di ta/fixtures.csv adalah UTC;
    # captured_at membawa offset eksplisit, jadi keduanya bisa
    # dibandingkan sebagai datetime aware. Bila kickoff tak bisa
    # ditentukan, perilaku lama dipertahankan untuk laga itu.
    by_id, _ = _load_fixtures()
    fx = by_id.get(game_id) or {}
    kickoff = None
    try:
        kd = _parsedate(fx.get("date"))
        kt = (fx.get("time") or "").strip()
        if kd and kt:
            hh, mnt = kt.split(":")[:2]
            kickoff = datetime(kd.year, kd.month, kd.day, int(hh),
                               int(mnt), tzinfo=timezone.utc)
    except (ValueError, AttributeError):
        kickoff = None
    if kickoff is not None:
        def _pre(cap_str):
            try:
                return datetime.strptime(
                    cap_str, "%Y-%m-%dT%H:%M:%S%z") < kickoff
            except (ValueError, TypeError):
                return True
        rows = [r for r in rows if _pre(r.get("captured_at") or "")]
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
        if cur is None or _capdt(cap) > _capdt(cur[0]):
            latest[key] = (cap, o)
    state = {}
    for (market, line, sel, bk), (cap, o) in latest.items():
        state.setdefault((market, line, sel), []).append((o, bk))
    cap = max((r.get("captured_at") or "" for r in rows),
              key=_capdt, default="")
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
    today = date_from or datetime.now(timezone.utc).date()
    lo = today
    hi = today + timedelta(days=n_days - 1)
    out = []
    sources = [
        ("predictions_upcoming.csv", "", "div"),
        ("predictions_cups_upcoming.csv", "competition", "div"),
    ]
    n_fix = 0
    n_unmatched = 0
    for fn, comp_col, div_col in sources:
        for r in _read_csv(os.path.join(HERE, fn)):
            d = _parsedate(r.get("date"))
            if not d or not (lo <= d <= hi):
                continue
            comp = r.get(comp_col) if comp_col else ""
            hint = _fixture_league_hint(r.get("div", ""), comp)
            gid = (r.get("game_id") or "").strip() or _match_game_id(
                r.get("home", ""), r.get("away", ""), r.get("date", ""), hint)
            if not gid:
                # Prediksi tanpa fixture TA (mis. jadwal belum terbit
                # di TipsterArea): dulu hilang diam-diam; kini terhitung
                # dan dilaporkan rantai harian.
                n_unmatched += 1
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
    return {"fixtures": n_fix, "rows": len(out), "unmatched": n_unmatched}


# ---------------------------------------------------------------- archive
ARCHIVE_FILES = ["predictions_upcoming.csv", "predictions_corners_upcoming.csv",
                 "predictions_cups_upcoming.csv", "predictions_corners_cups.csv",
                 "best_picks_today.csv", "market_compare.csv",
                 "recommended_single.csv", "recommended_slip.csv",
                 "recommended_slip10.csv"]


def _has_data_rows(path):
    """True bila file punya >= 2 baris (header + minimal satu baris
    data). Baca dibatasi dua baris pertama."""
    try:
        with open(path, "rb") as f:
            return sum(1 for _ in zip(range(2), f)) >= 2
    except OSError:
        return False


def archive_snapshots(target_date=None):
    """Salin output harian ke archive/<date>/, write-once per file.

    Arsip adalah snapshot pra-kickoff hari itu — bahan grading
    rekomendasi. Rerun di hari yang sama SETELAH kickoff dulu
    menimpa snapshot pagi dengan output pasca-kickoff yang tak lagi
    memuat laga yang sudah main; leg rekomendasi laga itu lalu tak
    pernah ter-generate ulang oleh grader dan akhirnya ter-pangkas
    sebagai yatim tanpa pernah dinilai (audit ronde 14, C14-1:
    3 leg Le Havre–PSG). Kini file yang sudah ada di arsip tidak
    ditimpa; hanya file yang hilang yang disalin, jadi run pertama
    yang parsial tetap bisa dilengkapi run berikutnya.

    Satu pengecualian (audit-diri ronde 14, L-2): file arsip yang
    hanya berisi header — hasil run pertama yang terdegradasi
    (rantai pasar gagal -> file produk kosong) — boleh ditimpa oleh
    sumber yang punya baris data. Tanpa ini write-once membekukan
    snapshot kosong dan run sehat berikutnya tak bisa memperbaikinya;
    snapshot asli selalu punya baris data, jadi provenans pra-kickoff
    tidak terancam oleh pengecualian ini.
    """
    d = target_date or datetime.now(timezone.utc).date()
    dest = os.path.join(ARCHIVE, d.isoformat())
    os.makedirs(dest, exist_ok=True)
    copied, kept = [], []
    for fn in ARCHIVE_FILES:
        src = os.path.join(HERE, fn)
        if os.path.exists(src):
            out = os.path.join(dest, fn)
            if os.path.exists(out) and not (
                    not _has_data_rows(out) and _has_data_rows(src)):
                kept.append(fn)
                continue
            # Salin atomik (tmp + replace) — grading membaca arsip ini;
            # salinan terpotong karena crash akan terbaca diam-diam.
            tmp = out + ".tmp"
            with open(src, "rb") as fi, open(tmp, "wb") as fo:
                fo.write(fi.read())
            os.replace(tmp, out)
            copied.append(fn)
    return {"date": d.isoformat(), "archived": copied, "kept": kept}


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
    """Masukkan pick piala ke picks.jsonl (competition=EFL Cup/DFB Pokal).

    Tiga disiplin yang ditambahkan audit ronde 3 (2026-10-29):
    - Side 1X2 diterjemahkan dari kosakata best_picks ("1"/"X"/"2") ke
      kosakata ledger ("H"/"D"/"A") SEBELUM disimpan — settle() dan
      _clv() score_ledger hanya mengenal H/D/A, jadi pick 1X2 piala
      dulu akan ter-grade kalah otomatis apa pun hasilnya. Penentuan
      harga tetap memakai side asli (state pasar TA memakai "1" dst).
    - Lantai edge: pick dengan edge < 0 tidak masuk ledger UANG
      (tetap ter-grade kalibrasinya lewat arsip best_picks). Dulu
      edge dihitung tapi tidak pernah diuji (pick Everton masuk
      dengan edge -0.0362).
    - Dedup per LAGA+pasar+garis, bukan per seleksi: satu stake per
      tie per pasar — seleksi teraman yang berubah antar-run tidak
      lagi menggandakan stake untuk laga yang sama.
    """
    existing = set()
    existing_matches = set()
    if os.path.exists(PICKS):
        with open(PICKS, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    existing.add(rec["pick_id"])
                    existing_matches.add((
                        rec.get("competition") or "", rec.get("date") or "",
                        rec.get("home") or "", rec.get("away") or "",
                        rec.get("market") or "", rec.get("line") or ""))
    os.makedirs(LEDGER, exist_ok=True)
    new = []
    edge_keys = set()
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
            side_t = {"1": "H", "X": "D", "2": "A"}.get(side, side) \
                if market == "1X2" else side
            mkey = (comp, d, home, away, market, line)
            if mkey in existing_matches:
                continue  # laga+pasar ini sudah punya stake di ledger
            pid = hashlib.md5(
                f"{comp}|{d}|{home}|{away}|{market}|{line}|{side_t}".encode()
            ).hexdigest()[:16]
            if pid in existing:
                continue
            # game_id tersimpan (predict_cups -> best_picks) didahulukan:
            # tebakan fuzzy _match_game_id bisa tertukar ke laga kembar.
            # File arsip lama tidak punya kolomnya -> fallback fuzzy.
            gid = (r.get("game_id") or "").strip() or \
                _match_game_id(home, away, d, CUP_LEAGUE[comp])
            cap, state = _prematch_state(gid) if gid else (None, {})
            pr = _state_prices(state, market, line, side) if state else []
            odds = _median([o for o, _ in pr])
            if not odds:
                continue  # tanpa harga tak bisa settle — lewati
            pm = _fnum(r.get("prob"))
            if pm is None:
                continue
            edge = pm - 1.0 / odds
            if edge < 0:
                # Hitung per laga+pasar unik: tie yang sama muncul di
                # file hari ini + salinan arsip, jadi penghitung per
                # pertemuan menggelembungkan angka cetak.
                edge_keys.add((d, home, away, market, line))
                continue  # di bawah harga pasar — bukan pick uang
            new.append({
                "pick_id": pid, "ts_created": datetime.utcnow().isoformat() + "Z",
                "model": "cup-proxy", "thr": 0.0, "status": "pending",
                "market": market, "side": side_t, "line": line,
                "p_model": round(pm, 4), "odds_open": round(odds, 4),
                "p_imp_open": round(1.0 / odds, 4),
                "edge": round(edge, 4),
                "competition": comp, "div": r.get("div") or "", "date": d,
                "home": home, "away": away,
            })
            existing.add(pid)
            existing_matches.add(mkey)
    if edge_keys:
        print(f"  cup picks dilewati (edge < 0): {len(edge_keys)}")
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
        print(f"archive {r['date']}: {r['archived']} "
              f"(+{len(r['kept'])} sudah ada, write-once)")
        return 0
    if "--cup-ledger" in argv:
        n = sync_cup_picks_to_ledger()
        print(f"cup picks -> ledger: {n} baru")
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
