#!/usr/bin/env python3
"""predict_cups.py — prediksi piala (EFL Cup + DFB Pokal), termasuk corner.

Sumber data: scrape tipsterarea (ta/fixtures.csv, ta/odds_1x2_snapshots.csv)
— TANPA API-Football. Hasil piala TIDAK masuk data latih model liga dan
baris piala TIDAK dicampur ke predictions_upcoming.csv (liga murni).

Aturan:
  - Hanya laga antar-tim yang terpetakan ke data liga (E0/E1/E2/E3,
    D1/D2) yang diprediksi; lainnya dicatat skipped.
  - Model gol: model_v2.DC di-fit per divisi dari all_matches_clean.csv.
    Laga lintas divisi: lambda home memakai attack home dari fit divisi tim
    kandang vs defense away dari fit divisi tim tandang, sebaliknya untuk
    away. Total lambda di-anchor: default ke rata-rata total gol kedua
    divisi; untuk piala, di-blend dengan laju gol piala terukur dari
    ta/results.csv (bobot ramp linear n/100, penuh bila n FT >= 100). Rasio lambda
    home:away dipertahankan. Ini adalah
    penyederhanaan yang disadari: kalibrasi lintas divisi tidak dimodelkan
    (grading terpisah akan menunjukkan kualitasnya).
  - Corner: rolling shots 5 laga liga terakhir per tim (divisi asal) +
    base-rate liga divisi tim kandang. Jika salah satu tim punya < 3 laga
    liga terakhir dgn data shots, corner dilewati (gol tetap jalan).

Output:
  predictions_cups_upcoming.csv      — prediksi gol/1X2/DC/O-U/BTTS
  predictions_corners_cups.csv       — prediksi corner
"""
import os
import sys
import csv
import json
import math
from collections import defaultdict, deque
from datetime import datetime, date, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from football_etl import normalize_name
from model_v2 import DC, xg_key
from features import _load_xg_map

CUP_LEAGUES = {"England - EFL Cup": "EFL Cup", "Germany - Cup Germany": "DFB Pokal"}
DIVS = ("E0", "E1", "E2", "E3", "D1", "D2")
DIV_ORDER = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "D1": 0, "D2": 1}
# Alias nama cup -> nama liga (normalize_name), untuk penyimpangan ejaan.
CUP_ALIAS = {
    "dynamo dresden": "dresden",
    "borussia m gladbach": "monchengladbach",
    "karlsruher": "karlsruhe",
    "fleetwood": "fleetwood town",
    "peterborough": "peterboro",
}

DATA = os.path.join(BASE_DIR, "all_matches_clean.csv")
FIX = os.path.join(BASE_DIR, "ta", "fixtures.csv")
ODDS1x2 = os.path.join(BASE_DIR, "ta", "odds_1x2_snapshots.csv")
PARAMS = os.path.join(BASE_DIR, "ta", "corner_params.json")
RESULTS = os.path.join(BASE_DIR, "ta", "results.csv")
OUT_GOL = os.path.join(BASE_DIR, "predictions_cups_upcoming.csv")
OUT_CORNER = os.path.join(BASE_DIR, "predictions_corners_cups.csv")

HALF_LIFE = 270.0
MAX_TRAIN = 4000
LINES = (6.5, 7.5, 8.5, 9.5, 10.5, 11.5)
CORNER_BAND = (8.5, 9.5, 10.5)

# Konfigurasi anchor total gol piala (P3). Total lambda laga di-anchor ke
# perpaduan total rating (rata-rata total gol kedua divisi) dengan laju gol
# piala terukur dari ta/results.csv. Ketika n FT >= MIN_N_FULL, pakai laju
# piala penuh; di bawahnya blend 50/50. Rasio lambda home:away tidak berubah
# (kedua lambda diskalakan oleh faktor yang sama).
CUP_CONF = {"min_n_full": 100}


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _norm(x):
    a = CUP_ALIAS.get(x.lower())
    return normalize_name(a if a else x)


# --- pemuatan all_matches (semua divisi yang dibutuhkan) ---
def _load_matches():
    matches = []
    xg_map = _load_xg_map()
    with open(DATA, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["Div"] not in DIVS or not r["Date"] or r["FTR"] not in ("H", "D", "A"):
                continue
            yh, ya = _num(r["FTHG"]), _num(r["FTAG"])
            hs, as_ = _num(r["HS"]), _num(r["AS"])
            hc, ac = _num(r["HC"]), _num(r["AC"])
            if yh is None or ya is None:
                continue
            xgh, xga = xg_map.get(xg_key(r["Div"], r["Date"],
                                         _norm(r["HomeTeam"]), _norm(r["AwayTeam"])),
                                  (None, None))
            matches.append({
                "div": r["Div"],
                "date": datetime.strptime(r["Date"], "%Y-%m-%d").date(),
                "season": r["Season"],
                "home": _norm(r["HomeTeam"]), "away": _norm(r["AwayTeam"]),
                "yh": int(yh), "ya": int(ya), "xgh": xgh, "xga": xga,
                "hs": int(hs) if hs is not None else None,
                "as": int(as_) if as_ is not None else None,
                "hc": int(hc) if hc is not None else None,
                "ac": int(ac) if ac is not None else None,
            })
    matches.sort(key=lambda m: m["date"])
    return matches


def _team_div_map(matches):
    """tim (normalized) -> divisi asal (divisi terbaru, preferensi tier tinggi)."""
    best = {}
    for m in matches:
        key = (m["home"], m["div"])
        if key not in best or m["season"] > best[key]:
            best[key] = m["season"]
    teamdiv = defaultdict(list)
    for (t, d), s in best.items():
        teamdiv[t].append((d, s))
    out = {}
    for t, opts in teamdiv.items():
        maxs = max(s for d, s in opts)
        divs = sorted([d for d, s in opts if s == maxs], key=lambda d: DIV_ORDER[d])
        out[t] = divs[0]
    return out


def _division_games(matches, div):
    return [(m["home"], m["away"], m["yh"], m["ya"],
             m["xgh"], m["xga"], m["date"])
            for m in matches if m["div"] == div]


def _avg_total(matches, div):
    g = [m for m in matches if m["div"] == div]
    if not g:
        return 2.7
    return sum(m["yh"] + m["ya"] for m in g) / len(g)


_cup_rate_cache = None


def _cup_goal_rate():
    """Laju gol piala terukur per kompetisi dari ta/results.csv.

    Return {comp: (avg_total_goals, n_ft)} untuk kompetisi yang punya
    hasil FT. Di-cache per run.
    """
    global _cup_rate_cache
    if _cup_rate_cache is None:
        agg = {}
        with open(RESULTS, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                comp = CUP_LEAGUES.get(r.get("league", ""))
                if not comp or r.get("status") != "FT":
                    continue
                try:
                    sh, sa = int(r["score_h"]), int(r["score_a"])
                except (TypeError, ValueError):
                    continue
                agg.setdefault(comp, []).append(sh + sa)
        _cup_rate_cache = {c: (sum(v) / len(v), len(v))
                           for c, v in agg.items()}
    return _cup_rate_cache


# --- model gol per divisi (cache per run) ---
_model_cache = {}
_avg_cache = {}


def _get_model(matches, div, cutoff):
    if div in _model_cache:
        return _model_cache[div]
    games = _division_games(matches, div)
    dc = DC()
    if len(games) >= 50:
        dc.fit(games[-MAX_TRAIN:], cutoff, HALF_LIFE)
    _model_cache[div] = dc
    _avg_cache[div] = _avg_total(matches, div)
    return dc


def cross_lambdas(matches, dh, da, home, away, cutoff, cup_comp=None):
    """lambda lintas divisi, diskalakan ke anchor total gol.

    Anchor default = rata-rata total gol dua divisi. Jika cup_comp diberikan
    (piala), anchor di-blend dengan laju gol piala terukur (lihat CUP_CONF).
    Rasio lambda home:away dipertahankan (kedua lambda diskalakan oleh
    faktor s yang sama).
    """
    mh = _get_model(matches, dh, cutoff)
    ma = _get_model(matches, da, cutoff)
    # rho hasil fit kedua divisi ikut dikembalikan: pemanggil dulu
    # membuangnya dan menghitung probabilitas dengan DC() baru
    # (rho default -0.07) apa pun hasil fit per divisinya.
    rho = (mh.rho + ma.rho) / 2.0
    avg_h = _avg_cache[dh]
    avg_a = _avg_cache[da]
    lh_raw = math.exp(mh.a.get(home, 0.0) + ma.d.get(away, 0.0) + mh.h)
    la_raw = math.exp(ma.a.get(away, 0.0) + mh.d.get(home, 0.0))
    tot = lh_raw + la_raw
    rating_total = (avg_h + avg_a) / 2.0
    target = rating_total
    if cup_comp:
        rate, n = _cup_goal_rate().get(cup_comp, (None, 0))
        if rate is not None:
            # Bobot ramp linear w = n/min_n_full (penuh di n >= 100).
            # Versi lama punya cliff di n=100: w melompat 0.5 -> 1.0
            # dalam semalam dan menggeser semua lambda kompetisi itu.
            w = min(1.0, n / CUP_CONF["min_n_full"])
            target = w * rate + (1.0 - w) * rating_total
    if tot <= 0:
        s = 1.0
    else:
        s = target / tot
    return lh_raw * s, la_raw * s, rho


# --- corner (kode setara model_corners_v3, dibaca dari all_matches) ---
def _rolling_shots(matches, team, cutoff):
    """5 laga liga terakhir tim sebelum cutoff, dari sudut pandang tim itu:
    daftar (shots_tim_ini, shots_lawan). Laga tanpa data shots dilewati."""
    out = []
    for m in reversed(matches):
        if m["date"] >= cutoff:
            continue
        if m["home"] == team:
            own, opp = m["hs"], m["as"]
        elif m["away"] == team:
            own, opp = m["as"], m["hs"]
        else:
            continue
        if own is None or opp is None:
            continue
        out.append((own, opp))
        if len(out) >= 5:
            break
    return out


def _stats_window(matches, div, cutoff):
    """Base-rate corner divisi (HC/AC) + L (rata-rata shots per tim per laga),
    setara stats_window model_corners_v3."""
    gh = ga = gsum = nry = dmu = 0.0
    ws = wsum_shots = 0.0
    for m in matches:
        if m["div"] != div or m["date"] >= cutoff:
            continue
        hc = m["hc"] if m["hc"] is not None else 0
        ac = m["ac"] if m["ac"] is not None else 0
        w = 0.5 ** ((cutoff - m["date"]).days / HALF_LIFE)
        gh += w * hc
        ga += w * ac
        gsum += 2 * w
        nry += w * (hc + ac) ** 2
        if m["hs"] is not None and m["as"] is not None:
            ws += w * (m["hs"] + m["as"])
            wsum_shots += 2 * w
    # Sama seperti model_corners_v3: dmu adalah total corner terbobot
    # final, bukan akumulasi jumlah kumulatif berjalan (order-dependent).
    dmu = gh + ga
    if gsum <= 0 or dmu <= 0:
        return 5.0, 5.0, 10.0, 1.18, 12.0
    base_h = gh * 2 / gsum
    base_a = ga * 2 / gsum
    r_base = nry / dmu
    L = ws / wsum_shots if wsum_shots > 0 else 12.0
    return base_h, base_a, base_h + base_a, r_base, L


REL_LO, REL_HI = 0.6, 1.7


def _rel_factor(shots, idx, L):
    """Faktor relatif satu arah (setara rel_factors model_corners_v3):
    idx 0 = shots yang dibuat tim itu, idx 1 = shots yang dibiarkan,
    dinormalisasi ke L = rata-rata shots per tim per laga di divisi acuan."""
    if not shots or L is None or L <= 0:
        return 1.0
    vals = [x[idx] for x in shots if x[0] is not None and x[1] is not None]
    if not vals:
        return 1.0
    avg = sum(vals) / len(vals)
    return _clamp(avg / L, REL_LO, REL_HI)


def corner_mu(matches, home, away, dh, da, cutoff):
    """mu corner laga (setara mu_cs model_corners_v3): base-rate divisi kandang
    dikalikan faktor relatif shots kedua tim; L dari data divisi kandang."""
    bh, ba, bmu, r_base, L = _stats_window(matches, dh, cutoff)
    shots_h = _rolling_shots(matches, home, cutoff)
    shots_a = _rolling_shots(matches, away, cutoff)
    fhp = _rel_factor(shots_h, 0, L)
    fhc = _rel_factor(shots_h, 1, L)
    fap = _rel_factor(shots_a, 0, L)
    fac = _rel_factor(shots_a, 1, L)
    gamma = _corner_gamma()
    return (bh * (fhp * fac) ** gamma + ba * (fap * fhc) ** gamma)


_gamma_cache = None


def _corner_gamma():
    global _gamma_cache
    if _gamma_cache is None:
        try:
            with open(PARAMS) as f:
                _gamma_cache = json.load(f).get("gamma", 0.15)
        except Exception:
            _gamma_cache = 0.15
    return _gamma_cache


_r_star_cache = None


def _corner_r_star():
    """Dispersi corner dari corner_params.json (kunci 'r').

    Dulu main() memakai konstanta 1.1868 yang ter-hardcode — nilai
    params saat konstanta itu ditulis — sehingga refit params tidak
    pernah mengubah probabilitas corner piala.
    """
    global _r_star_cache
    if _r_star_cache is None:
        try:
            with open(PARAMS) as f:
                _r_star_cache = json.load(f).get("r", 1.1868)
        except Exception:
            _r_star_cache = 1.1868
    return _r_star_cache


# --- output ---
GOL_COLS = ["div", "date", "time", "home", "away", "game_id", "competition",
            "div_home", "div_away", "lam_h", "lam_a",
            "ph_dc", "pd_dc", "pa_dc",
            "p_over_dc", "p_over15_dc", "p_over35_dc", "p_btts",
            "p_dc_1x", "p_dc_x2", "p_dc_12",
            "p_adv_h", "p_adv_a",
            "b365h", "b365d", "b365a"]

CORNER_COLS = ["div", "date", "home", "away", "game_id", "competition", "div_home", "div_away",
               "mu_shots_cs", "r_cs", "rec_line", "rec_side", "recommendation",
               "rec_prob"] + [f"p_gt_{ln}" for ln in LINES]


def pmf_k(mu, k):
    tot = []
    for x in range(51):
        logc = math.lgamma(x + k) - math.lgamma(k) - math.lgamma(x + 1)
        tot.append(math.exp(logc + k * math.log(k / (k + mu)) + x * math.log(mu / (k + mu))))
    s = sum(tot)
    return [p / s for p in tot]


def p_gt_frame(mu, r, ln):
    k = mu / (r - 1.0) if r > 1.02 else 1e9
    pmf = pmf_k(mu, k)
    return sum(pmf[int(ln) + 1:])


def p_adv(ph, pd, pa, lh, la, rho=None):
    """Probabilitas lolos (advance) tie SATU leg dari probs 90 menit.

    - ph/pd/pa = probabilitas 90 menit saat ini (kandang/seri/tandang).
    - q_h = peluang kandang lolos bila 90 menit seri:
        λ_ET = λ × 30/90, distribusi DC/Poisson sama; bila ET seri, adu
        penalti berbobot kekuatan q_pens_h = ph/(ph+pa) (fallback 0.5).
    - p_adv_h = ph + pd·q_h ; p_adv_a = pa + pd·(1−q_h).
    Hanya bermakna untuk format satu leg (EFL Cup & DFB Pokal kini begitu);
    format dua leg/replay -> kolom dikosongkan, bukan dipaksakan.
    """
    if lh <= 0 or la <= 0:
        return None, None
    dc = DC()
    if rho is not None:
        dc.rho = rho
    et = dc.probs(lh / 3.0, la / 3.0)
    et_ph, et_pd = et["ph"], et["pd"]
    denom = ph + pa
    q_pens = ph / denom if denom > 0 else 0.5
    q_h = et_ph + et_pd * q_pens
    return ph + pd * q_h, pa + pd * (1.0 - q_h)


def main():
    matches = _load_matches()
    teamdiv = _team_div_map(matches)
    today = date.today()

    # muat fixtures piala
    fixtures = []
    with open(FIX, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            league = r.get("league", "")
            if league not in CUP_LEAGUES or r.get("status") != "NS":
                continue
            d = datetime.strptime(r["date"], "%Y-%m-%d").date()
            if d < today:
                continue
            fixtures.append({
                "league": league, "comp": CUP_LEAGUES[league],
                "date": d, "time": r.get("time", ""),
                "home": r["home"].strip(), "away": r["away"].strip(),
                "game_id": r["game_id"],
            })
    fixtures.sort(key=lambda x: (x["date"], x["home"]))

    # odds 1X2 TERBARU per game_id — file bersifat append-only dan
    # versi lama mengambil baris PERTAMA per game (snapshot tertua).
    # Perbandingan memakai waktu parsed: string mentah salah urutan
    # lintas offset (28 laga memilih baris basi — audit ronde 3).
    def _capdt(s):
        try:
            return datetime.strptime(s or "", "%Y-%m-%dT%H:%M:%S%z")
        except (ValueError, TypeError):
            return datetime.min.replace(tzinfo=timezone.utc)

    odds = {}
    odds_cap = {}
    with open(ODDS1x2, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            gid = r["game_id"]
            cap = _capdt(r.get("captured_at"))
            if gid not in odds or cap >= odds_cap[gid]:
                odds[gid] = (r.get("o1"), r.get("ox"), r.get("o2"))
                odds_cap[gid] = cap

    gol_rows, corner_rows, skipped = [], [], []
    for fx in fixtures:
        hd = teamdiv.get(_norm(fx["home"]))
        ad = teamdiv.get(_norm(fx["away"]))
        if hd is None or ad is None:
            skipped.append((fx["comp"], fx["date"].isoformat(), fx["home"], fx["away"],
                            f"tim tidak terpetakan ke liga ({fx['home']}->{hd}, {fx['away']}->{ad})"))
            continue

        # gol
        try:
            lh, la, rho = cross_lambdas(matches, hd, ad, _norm(fx["home"]), _norm(fx["away"]),
                                        today, fx["comp"])
        except Exception as e:
            skipped.append((fx["comp"], fx["date"].isoformat(), fx["home"], fx["away"],
                            f"model gagal: {e}"))
            continue
        m = DC()
        m.rho = rho
        pr = {"ph": 0.0, "pd": 0.0, "pa": 0.0, "over": 0.0,
              "over15": 0.0, "over35": 0.0, "btts": 0.0}
        if lh > 0 and la > 0:
            pr = m.probs(lh, la)
        go = odds.get(fx["game_id"], (None, None, None))
        padv_h, padv_a = p_adv(pr["ph"], pr["pd"], pr["pa"], lh, la, rho=rho)
        gol_rows.append({
            "div": hd if hd == ad else f"{hd}/{ad}",
            "date": fx["date"].isoformat(), "time": fx["time"],
            "home": fx["home"], "away": fx["away"], "game_id": fx["game_id"],
            "competition": fx["comp"],
            "div_home": hd, "div_away": ad,
            "lam_h": round(lh, 3), "lam_a": round(la, 3),
            "ph_dc": round(pr["ph"], 4), "pd_dc": round(pr["pd"], 4),
            "pa_dc": round(pr["pa"], 4),
            "p_over_dc": round(pr["over"], 4),
            "p_over15_dc": round(pr["over15"], 4),
            "p_over35_dc": round(pr["over35"], 4),
            "p_btts": round(pr["btts"], 4),
            "p_dc_1x": round(pr["ph"] + pr["pd"], 4),
            "p_dc_x2": round(pr["pd"] + pr["pa"], 4),
            "p_dc_12": round(pr["ph"] + pr["pa"], 4),
            "p_adv_h": round(padv_h, 4) if padv_h is not None else "",
            "p_adv_a": round(padv_a, 4) if padv_a is not None else "",
            "b365h": go[0], "b365d": go[1], "b365a": go[2],
        })

        # corner
        shots_h = _rolling_shots(matches, _norm(fx["home"]), today)
        shots_a = _rolling_shots(matches, _norm(fx["away"]), today)
        if len(shots_h) < 3 or len(shots_a) < 3:
            skipped.append((fx["comp"], fx["date"].isoformat(), fx["home"], fx["away"],
                            "data corner kurang (<3 laga liga terakhir)"))
            continue
        mu = corner_mu(matches, _norm(fx["home"]), _norm(fx["away"]), hd, ad, today)
        r_star = _corner_r_star()
        rec_line = min(CORNER_BAND, key=lambda L: abs((L + 0.5) - mu))
        p_l = p_gt_frame(mu, r_star, rec_line)
        rec_side = "Over" if p_l >= 0.5 else "Under"
        rec_prob = p_l if rec_side == "Over" else 1.0 - p_l
        row = {
            "div": hd if hd == ad else f"{hd}/{ad}",
            "date": fx["date"].isoformat(), "home": fx["home"], "away": fx["away"],
            "game_id": fx["game_id"],
            "competition": fx["comp"], "div_home": hd, "div_away": ad,
            "mu_shots_cs": round(mu, 2), "r_cs": round(r_star, 3),
            "rec_line": rec_line, "rec_side": rec_side,
            "recommendation": f"{rec_side} {rec_line}", "rec_prob": round(rec_prob, 4),
        }
        for ln in LINES:
            row[f"p_gt_{ln}"] = round(p_gt_frame(mu, r_star, ln), 4)
        corner_rows.append(row)

    def write(path, rows, cols):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    write(OUT_GOL, gol_rows, GOL_COLS)
    write(OUT_CORNER, corner_rows, CORNER_COLS)

    print(f"prediksi gol piala: {len(gol_rows)} -> {OUT_GOL}")
    print(f"prediksi corner piala: {len(corner_rows)} -> {OUT_CORNER}")
    print(f"skipped: {len(skipped)}")
    for s in skipped:
        print("   -", s[0], s[1], f"{s[2]} v {s[3]}", "|", s[4])
    # Status jujur untuk rantai harian: fixture piala ADA tapi nol
    # prediksi gol = anomali (semua tie gagal dipetakan), bukan hari
    # tanpa piala. Hari tanpa fixture piala tetap 'success'.
    status = "failed" if (fixtures and not gol_rows) else "success"
    return {"n_gol": len(gol_rows), "n_corner": len(corner_rows),
            "skipped": skipped, "n_fixtures": len(fixtures),
            "status": status}


if __name__ == "__main__":
    main()
