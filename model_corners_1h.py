"""Model corner BABAK PERTAMA (1H) — produksi (prediksi saja).

Adopsi dari eksperimen C-2 (experiments/half_corners/, audit
2026-11-07 §2C): model rating venue-split untuk corner babak pertama
per tim (resep clone corner/SOT), total didistribusikan Negative
Binomial. Gerbang pra-registrasi LOLOS secara formal — log loss
pooled garis 4.5 di test 2024/25+2025/26 (n=3.503): model 0.6885 vs
base-rate divisi 0.6901 vs baseline naif 0.472 x model corner FT
0.6886, kalibrasi -0.36pp (<= 1pp). CATATAN KEJUJURAN: margin atas
baseline naif hanya 0.0001 — praktis seri; gerbang memang tidak
mensyaratkan margin minimum. Parameter dibekukan dari tuning musim
2023/24 saja (satu-satunya musim tuning yang jujur; label 2022/23
hanya 35,6% sehingga musim itu hanya riwayat trailing):
HL=180 hari, K=24, NB r=43.03.

Label 1H berasal dari gudang respons FotMob (stats Periods.FirstHalf)
dan di-cache inkremental di data_enrichment/labels_1h_corners.csv
(baris baru di-parse dari JSON store; sisanya dibaca dari cache).
Kunci rating memakai nama ternormalisasi (football_etl.normalize_name)
untuk menjembatani nama FotMob (label) dan nama football-data
(fixture); tim tanpa riwayat terdegradasi mulus ke rata-rata liga
oleh konstruksi shrinkage.

Belum ada sumber odds corner babak pertama di sistem — output ini
prediksi probabilitas saja, bukan penilaian value.

Output: predictions_corners_1h_upcoming.csv (file sendiri; tidak
menimpa output model mana pun).
"""
import csv
import json
import math
import os
from collections import defaultdict
from datetime import date, datetime, timezone

try:
    from paths import BASE
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), "football-data")

import model_sot as _msot  # _atomic_text_write bersama
from football_etl import normalize_name


def _load_upcoming():
    """Fixture mendatang dari dump xg_raw (pola sama seperti
    model_sot/model_cards: kickoff UTC masih di masa depan, nama tim
    dipetakan ke ruang nama football-data)."""
    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    name_maps = {}
    for fn in ("map_full.json", "map_ext.json"):
        p = os.path.join(BASE, "xg_raw", fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                name_maps.update(json.load(fh))
    upcoming = []
    for div, slug in FIX_MAP.items():
        p = os.path.join(BASE, "xg_raw", f"{slug}_2026_fixtures.json")
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        for d in data:
            if d.get("isResult"):
                continue
            dtf = datetime.strptime(d["datetime"], "%Y-%m-%d %H:%M:%S")
            if dtf <= now_naive:
                continue
            home = name_maps.get(f"{div}|{d['h']['title']}", d["h"]["title"])
            away = name_maps.get(f"{div}|{d['a']['title']}", d["a"]["title"])
            upcoming.append({"div": div, "date": dtf.date().isoformat(),
                             "home": home, "away": away})
    return upcoming

OUT = os.path.join(BASE, "predictions_corners_1h_upcoming.csv")
INDEX = os.path.join(BASE, "data_enrichment", "fotmob_full_index.csv")
LABELS_CACHE = os.path.join(BASE, "data_enrichment", "labels_1h_corners.csv")
FIX_MAP = _msot.FIX_MAP  # div -> slug dump fixture (sumber sama)

TOP5 = ["E0", "D1", "I1", "SP1", "F1"]
HL = 180.0
K_PRIOR = 24.0
NB_R = 43.03
FALLBACK_1H = (2.7, 2.1)
LINES = [2.5, 3.5, 4.5, 5.5, 6.5]
REC_LINES = [3.5, 4.5, 5.5]   # garis yang lolos verifikasi gerbang
CACHE_COLS = ["div", "season", "date", "home", "away", "fotmob_match_id",
              "corners_1h_h", "corners_1h_a", "corners_1h_total",
              "has_1h_corners"]


# ------------------------------------------------------------------ labels
def _period_corners(period):
    """[home, away] corner dari satu entri Periods, atau None.
    Persis probe audit/eksperimen: cocok pada key/title 'corners'."""
    if not period:
        return None
    for grp in period.get("stats", []) or []:
        for st in grp.get("stats", []) or []:
            name = st.get("key") or st.get("title") or st.get("name")
            if name in ("corners", "Corners"):
                vals = st.get("stats") or []
                if len(vals) >= 2 and vals[0] is not None and vals[1] is not None:
                    return int(vals[0]), int(vals[1])
    return None


def refresh_labels():
    """Cache label 1H inkremental dari indeks gudang FotMob.

    Mengembalikan list laga berlabel (dict) untuk divisi top-5.
    Baris indeks yang sudah ada di cache tidak di-parse ulang.
    """
    cached = {}
    if os.path.exists(LABELS_CACHE):
        with open(LABELS_CACHE, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                cached[r["fotmob_match_id"]] = r
    if not os.path.exists(INDEX):
        print(f"  ! indeks gudang tidak ada: {INDEX}")
        return []
    new_rows = []
    with open(INDEX, newline="", encoding="utf-8") as fh:
        index_rows = list(csv.DictReader(fh))
    for r in index_rows:
        if r["div"] not in TOP5 or r["fotmob_match_id"] in cached:
            continue
        out = {"div": r["div"], "season": r["season"], "date": r["date"],
               "home": r["home"], "away": r["away"],
               "fotmob_match_id": r["fotmob_match_id"],
               "corners_1h_h": "", "corners_1h_a": "",
               "corners_1h_total": "", "has_1h_corners": 0}
        try:
            with open(os.path.join(BASE, r["path"]), encoding="utf-8") as fh:
                doc = json.load(fh)
            periods = ((doc.get("content", {}).get("stats") or {})
                       .get("Periods") or {})
            c1 = _period_corners(periods.get("FirstHalf"))
            if c1 is not None:
                out["corners_1h_h"], out["corners_1h_a"] = c1
                out["corners_1h_total"] = c1[0] + c1[1]
                out["has_1h_corners"] = 1
        except Exception:
            pass
        cached[r["fotmob_match_id"]] = out
        new_rows.append(out)
    if new_rows:
        all_rows = sorted(cached.values(),
                          key=lambda x: (x["date"], x["div"], x["home"]))

        def _write(f):
            w = csv.DictWriter(f, fieldnames=CACHE_COLS)
            w.writeheader()
            w.writerows(all_rows)
        _msot._atomic_text_write(LABELS_CACHE, _write)
        print(f"  label 1H: +{len(new_rows)} baris baru di-parse dari gudang")
    labelled = []
    for r in cached.values():
        if r["div"] in TOP5 and int(r["has_1h_corners"] or 0):
            labelled.append({
                "div": r["div"], "date": r["date"],
                "day": date.fromisoformat(r["date"]).toordinal(),
                "home": normalize_name(r["home"]),
                "away": normalize_name(r["away"]),
                "c1h": int(r["corners_1h_h"]), "c1a": int(r["corners_1h_a"]),
            })
    labelled.sort(key=lambda m: (m["date"], m["div"], m["home"]))
    return labelled


# ------------------------------------------------------- decayed ratings
# Port persis dari experiments/half_corners (Decayed + Ratings).
class Decayed:
    __slots__ = ("s", "w", "last", "hl")

    def __init__(self, hl):
        self.s = 0.0
        self.w = 0.0
        self.last = None
        self.hl = hl

    def _decay(self, day):
        if self.last is not None and day > self.last:
            f = 0.5 ** ((day - self.last) / self.hl)
            self.s *= f
            self.w *= f
        self.last = day

    def value_at(self, day):
        self._decay(day)
        return self.s, self.w

    def add(self, day, x):
        self._decay(day)
        self.s += x
        self.w += 1.0


class Ratings:
    """Rating venue-split corner 1H for/against (resep clone SOT)."""

    def __init__(self, hl, k):
        self.hl, self.k = hl, k
        self.lg_h = defaultdict(lambda: Decayed(hl))
        self.lg_a = defaultdict(lambda: Decayed(hl))
        self.att_h = defaultdict(lambda: Decayed(hl))
        self.def_h = defaultdict(lambda: Decayed(hl))
        self.att_a = defaultdict(lambda: Decayed(hl))
        self.def_a = defaultdict(lambda: Decayed(hl))

    def league_mu(self, div, day):
        s_h, w_h = self.lg_h[div].value_at(day)
        s_a, w_a = self.lg_a[div].value_at(day)
        mu_h = s_h / w_h if w_h > 0 else FALLBACK_1H[0]
        mu_a = s_a / w_a if w_a > 0 else FALLBACK_1H[1]
        return mu_h, mu_a

    def _shrunk(self, obj, day, mu):
        s, w = obj.value_at(day)
        return (s + self.k * mu) / (w + self.k)

    def predict(self, div, home, away, day):
        mu_h, mu_a = self.league_mu(div, day)
        exp_h = mu_h * (self._shrunk(self.att_h[(div, home)], day, mu_h) / mu_h) \
                     * (self._shrunk(self.def_a[(div, away)], day, mu_h) / mu_h)
        exp_a = mu_a * (self._shrunk(self.att_a[(div, away)], day, mu_a) / mu_a) \
                     * (self._shrunk(self.def_h[(div, home)], day, mu_a) / mu_a)
        return exp_h, exp_a

    def update(self, div, home, away, day, v_h, v_a):
        self.att_h[(div, home)].add(day, v_h)
        self.def_h[(div, home)].add(day, v_a)
        self.att_a[(div, away)].add(day, v_a)
        self.def_a[(div, away)].add(day, v_h)
        self.lg_h[div].add(day, v_h)
        self.lg_a[div].add(day, v_a)


def nb_over(lam, r, line):
    """P(X > line), X ~ NegBin(mean=lam, size=r) — port eksperimen."""
    k_max = int(math.floor(line))
    q = lam / (r + lam)
    term = (r / (r + lam)) ** r
    cdf = term
    for k in range(1, k_max + 1):
        term *= (k - 1 + r) / k * q
        cdf += term
    return min(max(1.0 - cdf, 0.0), 1.0)


# -------------------------------------------------------------------- main
def predict_upcoming():
    labelled = refresh_labels()
    if not labelled:
        print("  ! tidak ada label corner 1H — prediksi dilewati")
        return 0
    rt = Ratings(HL, K_PRIOR)
    for m in labelled:
        rt.update(m["div"], m["home"], m["away"], m["day"], m["c1h"], m["c1a"])
    print(f"  state rating dibangun dari {len(labelled):,} laga berlabel 1H")

    upcoming = _load_upcoming()
    if not upcoming:
        print("  ! tidak ada fixture upcoming")
        return 0

    rows = []
    # Kronologis: state Decayed malas & sensitif urutan antar-tanggal.
    for fx in sorted(upcoming, key=lambda x: x["date"]):
        day = date.fromisoformat(fx["date"]).toordinal()
        exp_h, exp_a = rt.predict(fx["div"], normalize_name(fx["home"]),
                                  normalize_name(fx["away"]), day)
        exp_t = exp_h + exp_a
        probs = {ln: nb_over(exp_t, NB_R, ln) for ln in LINES}
        best = None
        for ln in REC_LINES:
            p_over = probs[ln]
            for side, p in (("Over", p_over), ("Under", 1.0 - p_over)):
                if best is None or p > best[2]:
                    best = (ln, side, p)
        rec_line, rec_side, rec_p = best
        rows.append({
            "div": fx["div"], "date": fx["date"], "home": fx["home"],
            "away": fx["away"],
            "exp_corners_1h_home": round(exp_h, 3),
            "exp_corners_1h_away": round(exp_a, 3),
            "exp_corners_1h_total": round(exp_t, 3),
            "rec_line": rec_line, "rec_side": rec_side,
            "recommendation": f"{rec_side} {rec_line}",
            "rec_prob": round(rec_p, 4),
            **{f"p_over_{ln}": round(probs[ln], 4) for ln in LINES},
        })

    cols = ["div", "date", "home", "away", "exp_corners_1h_home",
            "exp_corners_1h_away", "exp_corners_1h_total", "rec_line",
            "rec_side", "recommendation", "rec_prob"] + \
           [f"p_over_{ln}" for ln in LINES]

    def _write(f):
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    _msot._atomic_text_write(OUT, _write)
    print(f"  {len(rows)} upcoming 1H-corner predictions -> {OUT}")
    return len(rows)


if __name__ == "__main__":
    print("=== predict upcoming first-half corner fixtures ===")
    predict_upcoming()
