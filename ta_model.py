#!/usr/bin/env python3
"""
ta_model.py -- gabungkan prediksi model dengan harga pasar tipsterarea,
pilih "bet terbaik" per laga, lalu nilai hasilnya setelah pertandingan.

Alur:
  python ta_model.py --build   # buat kandidat bet dari prediksi + harga pasar
  python ta_model.py --grade   # isi hasil & untung/rugi dari results.csv
  python ta_model.py --report  # ringkasan performa (hit rate, ROI per pasar)

Baca saja: predictions_upcoming.csv, ta/*.csv, predictions_corners_upcoming.csv
Tulis:    ta/model_markets.csv, ta/best_bets.csv, ta/perf_summary.csv

Matriks skor memakai rumus Dixon-Coles yang sama dengan model_v2 (pois + tau),
lalu dikalibrasi ulang supaya total 1X2-nya persis sama dengan kolom ph/pd/pa
di predictions_upcoming.csv. Jadi pasar lain (DC, DNB, O/U, BTS) konsisten
dengan angka 1X2 yang sudah tayang di situs.
"""
import csv
import os
import re
import sys
import unicodedata
from datetime import datetime, timedelta, timezone

# Dixon-Coles PMF/tau kanonik (lihat football_etl).
from football_etl import pois, tau

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.join(HERE, "ta")
PRED = os.path.join(HERE, "predictions_upcoming.csv")
MAXG = 10
RHO = -0.07

MK_COLS = ["game_id", "date", "home", "away", "market", "line", "selection",
           "p_model", "p_push", "p_market", "odds_best", "book_best", "ev",
           "ev_shrunk", "fair_odds", "tier", "n_books", "captured_at"]
BET_COLS = ["bet_id", "created_at", "game_id", "kickoff_utc", "league",
            "home", "away", "market", "line", "selection", "bookmaker",
            "price", "p_model", "p_market", "ev", "tier", "status",
            "score", "result", "profit", "graded_at"]


# ------------------------------------------------------------ Dixon-Coles
def raw_matrix(lh, la, maxg=MAXG, rho=RHO):
    m = [[pois(i, lh) * pois(j, la) * tau(i, j, lh, la, rho)
          for j in range(maxg + 1)] for i in range(maxg + 1)]
    s = sum(sum(r) for r in m)
    return [[v / s for v in r] for r in m]


def outcomes(m):
    ph = sum(m[i][j] for i in range(len(m)) for j in range(len(m)) if i > j)
    pd = sum(m[i][i] for i in range(len(m)))
    pa = sum(m[i][j] for i in range(len(m)) for j in range(len(m)) if i < j)
    return ph, pd, pa


def calibrate(lh, la, th, td, ta, outer=12, inner=26):
    """Cari lambda yang menghasilkan (ph,pd,pa) = target.

    Dua parameter, dua target: total gol (T) mengatur peluang seri, selisih
    (S) mengatur rasio menang kandang vs tandang. Diselesaikan bergantian
    dengan bisection, jadi bentuk sebaran gol tetap Poisson (versi lama
    men-skala sel diagonal berulang kali sehingga P(Under 1.5) meledak).

    Mengembalikan (matriks, fell_back). Pagar (audit ronde 12, B12-1):
    pada laga favorit kuat, pd hampir datar terhadap total gol sehingga
    pencocokan pd bersifat ill-posed — bisection pernah berakhir di
    total gol 7,81 untuk laga yang lambda DC-nya berjumlah 3,81
    (Barcelona vs Alaves), menggelembungkan turunan (BTS Yes 0,90 vs
    0,55 matriks mentah) padahal matriks mentah di lambda DC sudah
    cocok dengan target dalam 0,003. Bila error 1X2 hasil kalibrasi
    tidak lebih baik dari matriks mentah, matriks mentah dipakai dan
    fell_back=True supaya pemanggil bisa menandai laga itu.
    """
    raw = raw_matrix(lh, la)
    rh, rd, ra = outcomes(raw)
    raw_err = max(abs(rh - th), abs(rd - td), abs(ra - ta))
    T = max(lh + la, 0.12)
    S = max(min(lh - la, T - 0.06), -T + 0.06)
    ratio_t = th / (th + ta) if (th + ta) > 1e-9 else 0.5

    def at(T_, S_):
        a = max(0.03, (T_ + S_) / 2)
        b = max(0.03, (T_ - S_) / 2)
        return outcomes(raw_matrix(a, b))

    for _ in range(outer):
        lo, hi = 0.12, 9.0
        for _ in range(inner):
            mid = (lo + hi) / 2
            _, pd, _ = at(mid, min(S, mid - 0.06))
            if pd > td:
                lo = mid
            else:
                hi = mid
        T = (lo + hi) / 2
        lo, hi = -T + 0.06, T - 0.06
        for _ in range(inner):
            mid = (lo + hi) / 2
            ph, _, pa = at(T, mid)
            r = ph / (ph + pa) if (ph + pa) > 1e-9 else 0.5
            if r < ratio_t:
                lo = mid
            else:
                hi = mid
        S = (lo + hi) / 2
        ph, pd, pa = at(T, S)
        if abs(ph - th) < 2e-3 and abs(pd - td) < 2e-3 and abs(pa - ta) < 2e-3:
            break
    m = raw_matrix(max(0.03, (T + S) / 2), max(0.03, (T - S) / 2))
    fh, fd, fa = outcomes(m)
    fin_err = max(abs(fh - th), abs(fd - td), abs(fa - ta))
    if fin_err > raw_err:
        return raw, True
    return m, False


# ------------------------------------------------------------ pasar
def market_probs(m, market, line=0.0, corner_probs=None):
    """Return dict selection -> (p_win, p_push)."""
    ph, pd, pa = outcomes(m)
    n = len(m)
    if market == "1X2":
        return {"1": (ph, 0.0), "X": (pd, 0.0), "2": (pa, 0.0)}
    if market == "DC":
        return {"1X": (ph + pd, 0.0), "X2": (pd + pa, 0.0), "12": (ph + pa, 0.0)}
    if market == "DNB":
        return {"Dnb1": (ph, pd), "Dnb2": (pa, pd)}
    if market == "OU":
        L = float(line)
        over = sum(m[i][j] for i in range(n) for j in range(n) if i + j > L)
        eq = sum(m[i][j] for i in range(n) for j in range(n) if i + j == L)
        under = sum(m[i][j] for i in range(n) for j in range(n) if i + j < L)
        return {"Under": (under, eq), "Over": (over, eq)}
    if market == "BTS":
        no = sum(m[0][j] for j in range(n)) + sum(m[i][0] for i in range(n)) - m[0][0]
        return {"Yes": (1 - no, 0.0), "No": (no, 0.0)}
    if market == "Corners":
        L = float(line)
        if corner_probs is not None:
            p_over = corner_probs.get(L, corner_probs.get(9.5, 0.5))
            return {"Over": (p_over, 0.0), "Under": (1 - p_over, 0.0)}
        return {}
    return {}


def fair_odds(p_win, p_push):
    """Harga adil untuk pasar yang bisa push (stake kembali)."""
    denom = p_win
    if denom <= 1e-9:
        return 999.0
    return (1 - p_push) / denom


# ------------------------------------------------------------ nama tim
ALIAS = {
    "man city": "manchester city", "man united": "manchester united",
    "man utd": "manchester united", "newcastle": "newcastle united",
    "tottenham": "tottenham hotspur", "wolves": "wolverhampton",
    "west brom": "west bromwich albion", "west ham": "west ham united",
    "qpr": "queens park rangers", "stoke": "stoke city",
    "swansea": "swansea city", "cardiff": "cardiff city",
    "norwich": "norwich city", "hull": "hull city",
    "birmingham": "birmingham city", "derby": "derby county",
    "ipswich": "ipswich town", "leeds": "leeds united",
    "brighton": "brighton and hove albion", "nottm forest": "nottingham forest",
    "sheffield weds": "sheffield wednesday", "sheffield utd": "sheffield united",
    "ath madrid": "atletico madrid", "ath bilbao": "athletic bilbao",
    "ath club": "athletic bilbao", "sociedad": "real sociedad",
    "betis": "real betis", "espanol": "espanyol", "spanyol": "espanyol",
    "dortmund": "borussia dortmund", "bayern munich": "bayern munchen",
    "hamburg": "hamburger", "paris sg": "paris saint germain",
    "paris st germain": "paris saint germain", "psg": "paris saint germain",
    "m gladbach": "monchengladbach", "gladbach": "monchengladbach",
    "ein frankfurt": "eintracht frankfurt", "frankfurt": "eintracht frankfurt",
    "fc koln": "koln", "leverkusen": "bayer leverkusen",
    "wolfsburg": "vfl wolfsburg", "stuttgart": "vfb stuttgart",
    "mainz": "mainz 05", "hoffenheim": "tsg hoffenheim",
    "hertha": "hertha berlin", "schalke": "schalke 04",
    "inter": "internazionale", "milan": "ac milan",
    "roma": "as roma", "lazio": "ss lazio", "napoli": "ssc napoli",
    "juve": "juventus", "verona": "hellas verona",
    "marseille": "olympique marseille", "lyon": "olympique lyonnais",
    "lille": "losc lille", "nice": "ogc nice", "rennes": "stade rennais",
    "saint etienne": "as saint etienne", "le havre": "le havre",
    "nott m forest": "nottingham forest", "nottm forest": "nottingham forest",
    "borussia m gladbach": "monchengladbach", "m gladbach": "monchengladbach",
    "celta": "celta vigo", "santander": "racing santander",
    "vallecano": "rayo vallecano", "sociedad": "real sociedad",
    "club brugge": "brugge", "brugge": "brugge",
}
DROP = {"fc", "cf", "sc", "ac", "as", "ss", "us", "ud", "rc", "afc", "club",
        "bk", "if", "cd", "ca", "sv", "vfl", "vfb", "tsg", "fsv", "de", "the",
        "calcio", "ssc", "acf", "krc", "rsc", "kv", "ogc", "losc"}


def norm(name):
    s = unicodedata.normalize("NFKD", name)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\([^)]*\)", " ", s)
    s = s.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = " ".join(s.split())
    toks = [t for t in s.split() if t not in DROP]
    s = " ".join(toks) if toks else s
    s = ALIAS.get(s, s)
    toks = [t for t in s.split() if t not in DROP]
    return " ".join(toks) if toks else s


def sim(a, b):
    """Kemiripan 0..1: subset token, awalan token, atau rasio string."""
    if a == b:
        return 1.0
    ta, tb = a.split(), b.split()
    if ta and tb:
        sa, sb = set(ta), set(tb)
        if sa <= sb or sb <= sa:
            return 0.95
    # token-level prefix match (hamburg vs hamburger, munich vs munchen)
    score = 0.0
    for t in ta:
        best = 0.0
        for u in tb:
            if t == u:
                best = max(best, 1.0)
            elif len(t) >= 4 and len(u) >= 4 and (t.startswith(u[:4]) or u.startswith(t[:4])):
                best = max(best, 0.85)
            else:
                import difflib
                best = max(best, difflib.SequenceMatcher(None, t, u).ratio() * 0.9)
        score += best
    score = score / max(len(ta), 1) if ta else 0.0
    # token yang terkandung di nama lain: gladbach ~ monchengladbach
    for t in ta:
        for u in tb:
            if len(t) >= 5 and (t in u or u in t):
                score = max(score, 0.88)
    import difflib
    full = difflib.SequenceMatcher(None, a, b).ratio()
    return max(score, full)


# ------------------------------------------------------------ io
def read_csv(path):
    """Read CSV, returning empty list if not found."""
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)


def fnum(x, d=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return d


def to_int(x, d=None):
    try:
        v = float(x)
        return int(v) if v == v else d
    except (TypeError, ValueError):
        return d


def _cap_key(s):
    """Kunci urut captured_at berbasis waktu parsed (perbandingan
    string mentah salah urutan lintas offset +0000/+0700)."""
    try:
        return datetime.strptime(s or "", "%Y-%m-%dT%H:%M:%S%z")
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)


# ------------------------------------------------------------ harga
def price_index():
    """(game_id, market, line, selection) -> list of (odds, bookmaker).

    Hanya kutipan TERBARU per bandar yang disimpan. Versi lama menampung
    semua snapshot sepanjang sejarah dan best_price mengambil maksimum
    lintas waktu, sehingga bet dihargai pada odds yang mungkin sudah
    tidak ditawarkan siapa pun (EV hantu, profit ter-grade terinflasi;
    audit ulang 2026-10-29: 749 dari 19.145 kunci harga punya odds
    terbaru != maksimum historis).

    Dua disiplin audit ronde 3: perbandingan 'terbaru' memakai waktu
    parsed (bukan string — salah urutan lintas offset), dan kutipan
    pada/setelah kickoff fixture dibuang (harga in-play bukan harga
    prematch; build() versi lama bisa menghargai bet dari snapshot
    pasca-kickoff pada run ulang malam hari).
    """
    kickoff = {}
    for fr in read_csv(os.path.join(TA, "fixtures.csv")):
        try:
            kickoff[fr["game_id"]] = datetime.strptime(
                f'{fr["date"]} {fr["time"]}', "%Y-%m-%d %H:%M"
            ).replace(tzinfo=timezone.utc)
        except (KeyError, TypeError, ValueError):
            continue
    latest = {}

    def put(key, bookie, odds, captured_at):
        ck = _cap_key(captured_at)
        ko = kickoff.get(key[0])
        if ko is not None and ck >= ko:
            return  # in-play / pasca-kickoff: bukan harga prematch
        cur = latest.get((key, bookie))
        if cur is None or ck >= cur[0]:
            latest[(key, bookie)] = (ck, odds)

    for r in read_csv(os.path.join(TA, "odds_markets_snapshots.csv")):
        m = r["market"]
        line = r["line"] or ""
        if m == "Over/Under":
            m, line = "OU", line
        elif m == "Standard 1X2":
            m = "1X2"
        elif m == "Double Chance":
            m = "DC"
        elif m == "Draw No Bet":
            m = "DNB"
        elif m in ("BTS", "BTTS", "Both Teams To Score"):
            m = "BTS"
        else:
            continue
        o = fnum(r["odds"])
        if not o or o <= 1.0:
            continue
        put((r["game_id"], m, line, r["selection"]), r["bookmaker"], o,
            r.get("captured_at") or "")
    # 1X2 dari halaman tanggal (harga umum, tanpa nama bandar)
    for r in read_csv(os.path.join(TA, "odds_1x2_snapshots.csv")):
        for sel, col in (("1", "o1"), ("X", "ox"), ("2", "o2")):
            o = fnum(r[col])
            if o and o > 1.0:
                put((r["game_id"], "1X2", "", sel), "market", o,
                    r.get("captured_at") or "")
    idx = {}
    for (key, bookie), (_, o) in latest.items():
        idx.setdefault(key, []).append((o, bookie))
    return idx


def prune_outliers(idx):
    """Buang harga yang jelas salah label.

    Parser kadang menempelkan harga satu pilihan ke pilihan lain (contoh
    bet-at-home: harga X=4.10 tercatat sebagai "1"), sehingga "harga
    terbaik" jadi 4.10 padahal semua bandar lain 1.64-1.71. Harga seperti
    itu membentuk EV palsu. Kalau sebuah pilihan punya >=3 kutipan, kutipan
    yang menyimpang >25% dari median dibuang (selama minimal 2 tersisa).
    """
    groups = {}
    for (gid, m, line, sel), lst in idx.items():
        groups.setdefault((gid, m, line), {})[sel] = lst
    dropped = 0
    for _, sels in groups.items():
        for sel, lst in sels.items():
            if len(lst) < 3:
                continue
            vals = sorted(o for o, _ in lst)
            med = vals[len(vals) // 2]
            keep = [(o, b) for o, b in lst if 0.78 * med <= o <= 1.30 * med]
            if len(keep) >= 2 and len(keep) < len(lst):
                dropped += len(lst) - len(keep)
                lst[:] = keep
    return dropped


def best_price(idx, gid, market, line, sel):
    lst = idx.get((gid, market, str(line), sel), [])
    if not lst:
        return None, None, 0
    o, b = max(lst, key=lambda x: x[0])
    return o, b, len(lst)


def market_implied(idx, gid, market, line, sels):
    """Harga pasar tanpa margin: p per pilihan (2 arah untuk pasar berpasangan)."""
    prices = {}
    for s in sels:
        o, _, _ = best_price(idx, gid, market, line, s)
        if not o:
            return {}
        prices[s] = o
    inv = {s: 1.0 / o for s, o in prices.items()}
    tot = sum(inv.values())
    if tot <= 0:
        return {}
    return {s: v / tot for s, v in inv.items()}


# ------------------------------------------------------------ pilih bet
MARKETS = [("1X2", ""), ("DC", ""), ("DNB", ""), ("OU", "1.5"),
           ("OU", "2.5"), ("OU", "3.5"), ("BTS", ""),
           ("Corners", "8.5"), ("Corners", "9.5"), ("Corners", "10.5")]
SELSET = {"1X2": ["1", "X", "2"], "DC": ["1X", "X2", "12"],
          "DNB": ["Dnb1", "Dnb2"], "OU": ["Under", "Over"], "BTS": ["Yes", "No"],
          "Corners": ["Under", "Over"]}
MIN_EV, MIN_EDGE, MIN_ODDS, MAX_ODDS = 0.03, 0.02, 1.25, 6.0
SHRINK = 0.5


def tier_of(p_cond):
    if p_cond >= 0.70:
        return "aman"
    if p_cond >= 0.50:
        return "seimbang"
    return "agresif"


def _load_corner_probs():
    """Load corner probabilities for upcoming fixtures.
    Returns dict (div, date, home, away) -> {line: p_over}.
    """
    path = os.path.join(HERE, "predictions_corners_upcoming.csv")
    out = {}
    if not os.path.exists(path):
        return out
    for r in read_csv(path):
        # p_gt_8.5 etc are P(total corners > line)
        probs = {}
        for ln in (6.5, 7.5, 8.5, 9.5, 10.5, 11.5):
            v = fnum(r.get(f"p_gt_{ln}"))
            if v is not None:
                probs[ln] = v
        out[(r["div"], r["date"], r["home"], r["away"])] = probs
    return out


def _merge_bets(old, winners, fixtures, captured):
    """Gabungkan kandidat bet terbaik per laga ke baris best_bets lama.

    Bet baru ditambahkan. Bet yang sudah ada dan masih OPEN diperbarui
    harga/probabilitas/EV-nya dari kandidat hari ini (audit ronde 13):
    build dulu melewatkan bet_id yang sudah ada, jadi baris membeku
    dengan harga dan p_model saat pertama dibuat — termasuk baris
    warisan build pra-perbaikan pagar kalibrasi — sementara best_picks
    mengonsumsinya setiap hari. Yang dinilai grade() akhirnya adalah
    nilai pra-kickoff terakhir, konsisten dengan pandangan closing
    file ini. Bet yang sudah settle tidak pernah diubah: itu riwayat.
    Return (baris gabungan, n_baru, n_diperbarui).
    """
    merged = dict(old)
    n_new = n_ref = 0
    for r in sorted(winners, key=lambda x: -x["ev_shrunk"]):
        bid = f'{r["game_id"]}|{r["market"]}|{r["line"]}|{r["selection"]}'
        cur = merged.get(bid)
        if cur is not None and (cur.get("status") or "").upper() != "OPEN":
            continue
        g = fixtures[r["game_id"]]
        row = {
            "bet_id": bid, "created_at": captured, "game_id": r["game_id"],
            "kickoff_utc": f'{r["date"]}T{g["time"]}', "league": g["league"],
            "home": r["home"], "away": r["away"], "market": r["market"],
            "line": r["line"], "selection": r["selection"],
            "bookmaker": r["book_best"], "price": r["odds_best"],
            "p_model": r["p_model"], "p_market": r["p_market"],
            "ev": r["ev_shrunk"], "tier": r["tier"], "status": "OPEN",
            "score": "", "result": "", "profit": "", "graded_at": "",
        }
        if cur is None:
            merged[bid] = row
            n_new += 1
        else:
            for f_ in ("bookmaker", "price", "p_model", "p_market",
                       "ev", "tier", "kickoff_utc"):
                cur[f_] = row[f_]
            n_ref += 1
    return list(merged.values()), n_new, n_ref


def _purge_bogus(rows, issued_ids):
    """Buang baris OPEN yang harga x peluang pasarnya mustahil
    (> 1,02) — sisa data korup/salah label dari build lama.

    Dua pengecualian (audit-diri ronde 13): baris yang diterbitkan
    atau diperbarui build SAAT INI dikecualikan — kandidatnya lolos
    saringan build hari ini, jadi produk di atas ambang di sana
    adalah ketidaksepakatan model-pasar yang sah, bukan korupsi;
    tanpa pengecualian ini purge di build berikutnya membuang baris
    yang build sebelumnya terbitkan sendiri, lalu build yang sama
    menerbitkannya lagi (churn abadi, dan baris bisa lenyap sebelum
    sempat dinilai). Baris settle tidak pernah dibuang: itu riwayat
    grading. Return (baris tersisa, n_dibuang).
    """
    kept, n = [], 0
    for r in rows:
        if (r["bet_id"] not in issued_ids
                and (r.get("status") or "").upper() == "OPEN"
                and fnum(r.get("price")) * fnum(r.get("p_market")) > 1.02):
            n += 1
            continue
        kept.append(r)
    return kept, n


def build():
    preds = read_csv(PRED)
    fixtures = {r["game_id"]: r for r in read_csv(os.path.join(TA, "fixtures.csv"))}
    if not fixtures:
        print("ta/fixtures.csv kosong -- jalankan ta_scrape.py dulu", file=sys.stderr)
        return 1

    # indeks laga tipsterarea per tanggal, supaya pencocokan nama tidak liar
    by_date = {}
    for g in fixtures.values():
        by_date.setdefault(g["date"], []).append(g)
    dates = sorted(by_date)

    idx = price_index()
    n_drop = prune_outliers(idx)
    print(f"harga dibuang (salah label): {n_drop}")
    captured = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    corner_probs = _load_corner_probs()

    mk_rows = []
    matched = 0
    unmatched = []
    calib_fallbacks = []
    for p in preds:
        k = (norm(p["home"]), norm(p["away"]))
        # kandidat: laga di tanggal sama atau sehari sebelum/sesudah
        try:
            d0 = datetime.strptime(p["date"], "%Y-%m-%d").date()
        except ValueError:
            continue
        pool = []
        for dd in (-1, 0, 1):
            ds = (d0 + timedelta(days=dd)).isoformat()
            pool.extend(by_date.get(ds, []))
        if not pool:
            unmatched.append(f'{p["date"]} {p["home"]} v {p["away"]}')
            continue
        g = None
        for c in pool:
            if (norm(c["home"]), norm(c["away"])) == k:
                g = c
                break
        if g is None:
            best, bs = None, 0.0
            for c in pool:
                sc = sim(k[0], norm(c["home"])) * sim(k[1], norm(c["away"]))
                if sc > bs:
                    bs, best = sc, c
            if bs < 0.90 or best is None:
                unmatched.append(f'{p["date"]} {p["home"]} v {p["away"]}')
                continue
            g = best
        gid = g["game_id"]
        # Disiplin kickoff: jangan buat bet untuk laga yang sudah
        # mulai (mis. run ulang malam hari) — bet semacam itu
        # terkontaminasi look-ahead di catatan performa ta_model.
        try:
            ko = datetime.strptime(f'{g["date"]} {g["time"]}',
                                   "%Y-%m-%d %H:%M").replace(
                                       tzinfo=timezone.utc)
            if ko <= datetime.now(timezone.utc):
                continue
        except (KeyError, TypeError, ValueError):
            pass
        matched += 1

        lh, la = fnum(p["lam_h"]), fnum(p["lam_a"])
        th, td, ta = fnum(p["ph_dc"]), fnum(p["pd_dc"]), fnum(p["pa_dc"])
        if not all((lh, la, th, td, ta)):
            continue
        m, fell_back = calibrate(lh, la, th, td, ta)
        if fell_back:
            calib_fallbacks.append(f'{p["date"]} {p["home"]} v {p["away"]}')

        cp = None
        if (p.get("div", ""), p["date"], p["home"], p["away"]) in corner_probs:
            cp = corner_probs[(p.get("div", ""), p["date"], p["home"], p["away"])]
        for market, line in MARKETS:
            sels = SELSET[market]
            mp = market_implied(idx, gid, market, line, sels)
            probs = market_probs(m, market, line or 0.0, cp)
            for sel in sels:
                o, book, nbooks = best_price(idx, gid, market, line, sel)
                if not o:
                    continue
                p_win, p_push = probs[sel]
                ev = p_win * (o - 1.0) - (1.0 - p_win - p_push)
                p_cond = p_win / (1 - p_push) if (1 - p_push) > 1e-9 else p_win
                p_mkt = mp.get(sel)
                if p_mkt is None:
                    continue
                # pasar berpasangan: p_mkt dinormalkan, samakan basisnya
                p_shrunk = (1 - SHRINK) * p_cond + SHRINK * p_mkt
                ev_sh = p_shrunk * o - 1.0
                mk_rows.append({
                    "game_id": gid, "date": p["date"], "home": p["home"],
                    "away": p["away"], "market": market, "line": line,
                    "selection": sel,
                    "p_model": round(p_win, 4), "p_push": round(p_push, 4),
                    "p_market": round(p_mkt, 4), "odds_best": o,
                    "book_best": book, "ev": round(ev, 4),
                    "ev_shrunk": round(ev_sh, 4),
                    "fair_odds": round(fair_odds(p_win, p_push), 2),
                    "tier": tier_of(p_cond), "n_books": nbooks,
                    "captured_at": captured,
                })

    if calib_fallbacks:
        print(f"  ! kalibrasi kalah dari matriks mentah di "
              f"{len(calib_fallbacks)} laga; matriks DC mentah dipakai: "
              + "; ".join(calib_fallbacks))
    write_csv(os.path.join(TA, "model_markets.csv"), MK_COLS, mk_rows)

    # satu bet terbaik per laga: EV setelah penyusutan, harus lolos semua saringan
    per_game = {}
    for r in mk_rows:
        o = r["odds_best"]
        if not (MIN_ODDS <= o <= MAX_ODDS):
            continue
        if r["ev_shrunk"] < MIN_EV:
            continue
        if r["p_model"] - r["p_market"] < MIN_EDGE:
            continue
        cur = per_game.get(r["game_id"])
        if cur is None or r["ev_shrunk"] > cur["ev_shrunk"]:
            per_game[r["game_id"]] = r

    old = {r["bet_id"]: r for r in read_csv(os.path.join(TA, "best_bets.csv"))}
    rows, n_new, n_ref = _merge_bets(old, per_game.values(), fixtures,
                                     captured)
    # Buang bet lama yang harganya mustahil (harga x peluang pasar
    # > 1) SETELAH penggabungan, dengan pengecualian untuk bet yang
    # build ini terbitkan/perbarui (_purge_bogus).
    issued = {f'{r["game_id"]}|{r["market"]}|{r["line"]}|{r["selection"]}'
              for r in per_game.values()}
    rows, bogus = _purge_bogus(rows, issued)
    if bogus:
        print(f"bet mustahil dibuang: {bogus}")
    if n_new or n_ref or bogus:
        write_csv(os.path.join(TA, "best_bets.csv"), BET_COLS, rows)
    elif not os.path.exists(os.path.join(TA, "best_bets.csv")):
        write_csv(os.path.join(TA, "best_bets.csv"), BET_COLS, [])

    print(f"laga cocok: {matched}/{len(preds)} | baris pasar: {len(mk_rows)} | "
          f"bet baru: {n_new} | bet diperbarui: {n_ref} | "
          f"tak cocok: {len(unmatched)}")
    if unmatched and "--verbose" in sys.argv:
        for u in unmatched[:15]:
            print("   tak cocok:", u)
    return 0


# ------------------------------------------------------------ nilai hasil
def settle(bet, sh, sa):
    """Return 'win'/'lose'/'push'."""
    i, j = int(sh), int(sa)
    m, sel = bet["market"], bet["selection"]
    L = fnum(bet["line"], 0.0) or 0.0
    if m == "1X2":
        out = "1" if i > j else ("X" if i == j else "2")
        return "win" if sel == out else "lose"
    if m == "DC":
        ok = {"1X": i >= j, "X2": i <= j, "12": i != j}[sel]
        return "win" if ok else "lose"
    if m == "DNB":
        if i == j:
            return "push"
        win = (i > j) if sel == "Dnb1" else (i < j)
        return "win" if win else "lose"
    if m == "OU":
        tot = i + j
        if tot == L:
            return "push"
        over = tot > L
        return "win" if (over == (sel == "Over")) else "lose"
    if m == "BTS":
        both = i > 0 and j > 0
        return "win" if (both == (sel == "Yes")) else "lose"
    if m == "Corners":
        # i=total home corners, j=total away corners — set via settle_corners
        tot = i + j
        over = tot > L
        if tot == L:
            return "push"
        return "win" if (over == (sel == "Over")) else "lose"
    return "?"


def _fd_date(s):
    """Tanggal football-data (DD/MM/YYYY) -> ISO; None bila tak dikenal."""
    s = (s or "").strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _load_corner_counts():
    """Load actual corner counts from FD raw CSVs.
    Returns dict (iso_date, norm(home), norm(away)) -> (hc, ac).

    Kunci harus sama persis dengan sisi bet di grade() (tanggal ISO +
    nama ternormalisasi). Versi lama memakai tanggal mentah DD/MM/YYYY
    dan nama mentah CSV, sehingga lookup tidak pernah cocok dan bet
    corner dinilai dari skor gol.
    """
    out = {}
    raw_dir = os.path.join(HERE, "raw")
    for div in ("E0", "D1", "I1", "SP1", "F1"):
        path = os.path.join(raw_dir, f"{div}_2627.csv")
        if not os.path.exists(path):
            continue
        for r in read_csv(path):
            d = _fd_date(r.get("Date", ""))
            hc = to_int(r.get("HC"))
            ac = to_int(r.get("AC"))
            if d is None or hc is None or ac is None:
                continue
            out[(d, norm(r.get("HomeTeam") or ""),
                 norm(r.get("AwayTeam") or ""))] = (hc, ac)
    return out


def grade():
    bets = read_csv(os.path.join(TA, "best_bets.csv"))
    res = {r["game_id"]: r for r in read_csv(os.path.join(TA, "results.csv"))}
    corner_counts = _load_corner_counts()
    changed = 0
    skipped_corners = 0
    now = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    for b in bets:
        if b["status"] != "OPEN":
            continue
        r = res.get(b["game_id"])
        if not r or r["score_h"] == "":
            continue
        sh, sa = r["score_h"], r["score_a"]
        # For Corner market, use actual corner counts instead of scores
        if b["market"] == "Corners":
            dt = (b.get("kickoff_utc") or "")[:10]
            # kickoff_utc dibangun dari tanggal PREDIKSI + jam fixture,
            # sedangkan fixture yang cocok di build() boleh bergeser
            # ±1 hari — cari di tiga tanggal (audit ulang: K2-G1).
            cand_dates = {dt}
            try:
                d0 = datetime.strptime(dt, "%Y-%m-%d").date()
                cand_dates |= {(d0 + timedelta(days=k)).isoformat()
                               for k in (-1, 1)}
            except ValueError:
                pass
            counts = None
            for cd in sorted(cand_dates):
                counts = corner_counts.get(
                    (cd, norm(b["home"]), norm(b["away"])))
                if counts is not None:
                    break
            if counts is None:
                # Fallback fuzzy di tanggal kandidat (ambang produk sim
                # 0.90, sama seperti pencocokan fixture di build()),
                # plus margin di atas kandidat kedua supaya dua laga
                # bernama mirip di tanggal berdekatan tidak tertukar.
                best, bs, second = None, 0.0, 0.0
                for (cd, ch, ca), cc in corner_counts.items():
                    if cd not in cand_dates:
                        continue
                    sc = sim(norm(b["home"]), ch) * sim(norm(b["away"]), ca)
                    if sc > bs:
                        second, bs, best = bs, sc, cc
                    elif sc > second:
                        second = sc
                if bs >= 0.90 and bs - second >= 0.02:
                    counts = best
            if counts is None:
                # Tidak ada data corner aktual: biarkan OPEN. Menilai bet
                # corner dari skor gol (perilaku lama) menghasilkan grade
                # yang salah secara diam-diam.
                skipped_corners += 1
                continue
            sh, sa = counts
        out = settle(b, sh, sa)
        price = fnum(b["price"], 1.0)
        if out == "win":
            profit = price - 1.0
        elif out == "push":
            profit = 0.0
        else:
            profit = -1.0
        b["status"] = "SETTLED"
        if b["market"] == "Corners":
            b["score"] = f'{sh}-{sa}'
        else:
            b["score"] = f'{r["score_h"]}-{r["score_a"]}'
        b["result"] = out
        b["profit"] = f"{profit:+.3f}"
        b["graded_at"] = now
        changed += 1
    write_csv(os.path.join(TA, "best_bets.csv"), BET_COLS, bets)
    print(f"dinilai: {changed} bet | sisa OPEN: "
          f"{sum(1 for b in bets if b['status'] == 'OPEN')}"
          + (f" | corner dilewati (tak ada data aktual): {skipped_corners}"
             if skipped_corners else ""))
    return 0


def report():
    bets = [b for b in read_csv(os.path.join(TA, "best_bets.csv"))
            if b["status"] == "SETTLED"]
    if not bets:
        print("belum ada bet yang selesai.")
        return 0
    rows = []
    for key in ("ALL", "1X2", "DC", "DNB", "OU", "BTS", "Corners"):
        sub = bets if key == "ALL" else [b for b in bets if b["market"] == key]
        if not sub:
            continue
        n = len(sub)
        w = sum(1 for b in sub if b["result"] == "win")
        p = sum(1 for b in sub if b["result"] == "push")
        l = n - w - p
        pl = sum(fnum(b["profit"], 0) for b in sub)
        avg_odds = sum(fnum(b["price"], 0) for b in sub) / n
        rows.append({"group": key, "n": n, "win": w, "push": p, "lose": l,
                     "hit_rate": round(w / (n - p), 4) if n > p else 0,
                     "profit_units": round(pl, 3),
                     "roi": round(pl / n, 4), "avg_odds": round(avg_odds, 3)})
    write_csv(os.path.join(TA, "perf_summary.csv"),
              ["group", "n", "win", "push", "lose", "hit_rate", "profit_units",
               "roi", "avg_odds"], rows)
    print(f"{'pasar':6} {'n':>4} {'menang':>7} {'seri':>5} {'kalah':>6} "
          f"{'hit%':>7} {'unit':>8} {'ROI%':>7} {'harga':>6}")
    for r in rows:
        print(f"{r['group']:6} {r['n']:>4} {r['win']:>7} {r['push']:>5} "
              f"{r['lose']:>6} {r['hit_rate']*100:>6.1f}% "
              f"{r['profit_units']:>+8.2f} {r['roi']*100:>+6.1f}% "
              f"{r['avg_odds']:>6.2f}")
    return 0


if __name__ == "__main__":
    if "--build" in sys.argv:
        sys.exit(build())
    if "--grade" in sys.argv:
        sys.exit(grade())
    if "--report" in sys.argv:
        sys.exit(report())
    print(__doc__)
