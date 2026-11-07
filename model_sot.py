"""Model tembakan ke gawang (shots on target / SOT) untuk fixture mendatang.

Resep hasil eksperimen experiments/sot_model v5 (keputusan user
2026-11-07): resep ramping v3 (rating + sinyal total tembakan +
ensemble naif 50/50) ditambah tiga perbaikan dari proposal eksternal
yang lolos gerbang adopsi v5:

  R  — rating SOT diganti regresi Poisson log-linear GABUNGAN per
       divisi: log(mu_kandang) = beta_kandang + A[home] + D[away],
       log(mu_tandang) = beta_tandang + A[away] + D[home], dengan
       ridge (lambda/2) * sum(A^2 + D^2), lambda = 100 (disetel HANYA
       dari musim 2022/23). Refit malas per divisi: permintaan prediksi
       pertama pada/setelah hari refit terjadwal me-refit divisi itu
       dari laga-laga STRICTLY sebelum tanggal permintaan, bobot
       sampel decay eksponensial 365 hari; refit berikutnya 7 hari
       kemudian. Fallback rata-rata liga untuk baseline naif diambil
       dari exp(beta) regresi ini.
  BB — rasio on-target komponen total tembakan dihaluskan ala
       Beta-Binomial: ratio = (S_sot + P * rho) / (S_shots + P),
       P = 200 tembakan pseudo untuk kedua venue (disetel HANYA dari
       2022/23), menggantikan prior lama K * mu_shots yang bergantung
       venue (~104 kandang / ~88 tandang). Target shrink rho (rasio
       liga ter-decay per venue) tidak berubah.
  NB — probabilitas garis dihitung dari negative binomial dengan
       ukuran r = 79.94 (estimasi method-of-moments dari residual
       walk-forward model ramping musim 2019/20-2022/23), bukan
       Poisson, untuk kedua total anggota ensemble.

Verifikasi resep (run_sot_v5.py, walk-forward 2023/24-2025/26, 21.461
laga, garis utama 9.5, log loss pooled — makin kecil makin baik):
  ramping 0.6312 | +R 0.6307 | +NB 0.6309 | +BB 0.6311 |
  GABUNGAN (R+NB+BB) 0.6304, Brier 0.2198, calib err 0.2pp, MAE 2.44.
Gerbang adopsi: gabungan mengalahkan ramping, kalibrasi tidak
memburuk > 1.5pp, tidak ada divisi top-5 memburuk > 0.003.

Mesin-mesin pendukung (disalin dari eksperimen agar angka produksi
sama dengan yang terverifikasi):
- Komponen total tembakan: rating serang/bertahan TOTAL tembakan
  (HS/AS) per venue dari laju ter-decay eksponensial (half-life 365
  hari), di-shrink ke rata-rata liga ter-decay dengan prior K = 8
  match-equivalents; exp tembakan tersirat SOT per tim = exp total
  tembakan x rasio on-target (BB di atas); exp per tim final =
  0.5 * exp regresi SOT + 0.5 * exp tersirat tembakan.
- Ensemble: probabilitas final = 0.5 * P NB total model +
  0.5 * P NB total baseline naif (rata-rata polos 10 laga terakhir
  per tim).

Mode:
  python model_sot.py --predict   # prediksi fixture mendatang
Output:
  predictions_sot_upcoming.csv    # kolom sejajar predictions_corners_upcoming.csv
"""
import os
import csv
import json
import math
import sys
import tempfile
from collections import defaultdict, deque
from datetime import date, datetime, timezone

import numpy as np

# Direktori dari paths (sumber kebenaran tunggal), pola yang sama
# dengan model_corners_v3.py.
try:
    from paths import BASE, DATA_CLEAN as DATA
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), "football-data")
    DATA = os.path.join(BASE, "all_matches_clean.csv")
UPCOMING_OUT = os.path.join(BASE, "predictions_sot_upcoming.csv")
FIX_MAP = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
           "I1": "Serie_A", "F1": "Ligue_1"}

HL = 365.0          # half-life decay (hari) — sistem tembakan + bobot regresi
K_PRIOR = 8.0       # prior shrinkage sistem tembakan (match-equivalents)
NAIVE_N = 10        # jendela baseline naif trailing
ENS_W = 0.5         # bobot model dalam ensemble (sisanya naif)
RIDGE_LAM = 100.0   # ridge regresi gabungan (disetel 2022/23, eksperimen v5)
BB_PRIOR = 200.0    # prior Beta-Binomial rasio on-target, tembakan pseudo (v5)
NB_R = 79.94        # ukuran negative binomial (residual 2019/20-2022/23, v5)
REFIT_DAYS = 7      # kadens refit regresi per divisi (hari tanggal laga)
ETA_LO, ETA_HI = -6.0, 4.0   # penjaga exp() regresi, sama di fit & prediksi
LINES = [6.5, 7.5, 8.5, 9.5, 10.5, 11.5]

# fallback divisi tanpa histori statistik (hanya laga-laga pertama)
FALLBACK = {"sot": (4.5, 3.5), "shots": (13.0, 11.0)}


def _atomic_text_write(path, writer, newline=""):
    """Tulis artefak teks utuh sebelum diterbitkan ke pembaca
    (pola yang sama dengan model_corners_v3.py)."""
    out_dir = os.path.dirname(os.path.abspath(path))
    os.makedirs(out_dir, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{os.path.basename(path)}.", suffix=".tmp", dir=out_dir)
    try:
        try:
            f = os.fdopen(fd, "w", newline=newline, encoding="utf-8")
        except Exception:
            os.close(fd)
            raise
        with f:
            writer(f)
            f.flush()
            os.fsync(f.fileno())
        try:
            os.chmod(tmp_path, os.stat(path).st_mode & 0o777)
        except OSError:
            os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# ------------------------------------------------------- decayed ratings
# Kelas Decayed/Ratings disalin dari experiments/sot_model/run_sot_v2.py
# (yang mereproduksi run_sot_experiment.py) — jangan ubah rumusnya di
# sini tanpa menjalankan ulang verifikasi eksperimennya. Satu-satunya
# perubahan yang disengaja: on_target_ratio memakai penghalusan
# Beta-Binomial eksperimen v5 (lihat BB_PRIOR).
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
    """Rating serang/bertahan terpisah venue untuk satu statistik
    per-laga (di produksi hanya dipakai untuk TOTAL tembakan):
    exp_home = mu_h * att_h(home) * def_a(away) dengan rating =
    laju ter-shrink / mu dan laju ter-shrink = (s + K*mu) / (w + K).
    Dengan track_ratio=True juga melacak jumlah SOT ter-decay agar
    rasio on-target bisa dibentuk (dipakai sistem total tembakan)."""

    def __init__(self, hl, k, stat, track_ratio=False):
        self.hl, self.k, self.stat = hl, k, stat
        self.fb_h, self.fb_a = FALLBACK[stat]
        self.lg_h = defaultdict(lambda: Decayed(hl))   # div -> Decayed
        self.lg_a = defaultdict(lambda: Decayed(hl))
        self.att_h = defaultdict(lambda: Decayed(hl))  # (div, team)
        self.def_h = defaultdict(lambda: Decayed(hl))
        self.att_a = defaultdict(lambda: Decayed(hl))
        self.def_a = defaultdict(lambda: Decayed(hl))
        self.track_ratio = track_ratio
        if track_ratio:
            self.sot_h = defaultdict(lambda: Decayed(hl))      # SOT tim, kandang
            self.sot_a = defaultdict(lambda: Decayed(hl))      # SOT tim, tandang
            self.lg_sot_h = defaultdict(lambda: Decayed(hl))   # SOT liga, kandang
            self.lg_sot_a = defaultdict(lambda: Decayed(hl))   # SOT liga, tandang

    def league_mu(self, div, day):
        """(mu_h, mu_a, w_h, w_a): rata-rata liga ter-decay + bobotnya."""
        s_h, w_h = self.lg_h[div].value_at(day)
        s_a, w_a = self.lg_a[div].value_at(day)
        mu_h = s_h / w_h if w_h > 0 else self.fb_h
        mu_a = s_a / w_a if w_a > 0 else self.fb_a
        return mu_h, mu_a, w_h, w_a

    def _shrunk(self, stat_obj, day, mu):
        s, w = stat_obj.value_at(day)
        return (s + self.k * mu) / (w + self.k)

    def predict(self, div, home, away, day):
        mu_h, mu_a, _, _ = self.league_mu(div, day)
        exp_h = mu_h * (self._shrunk(self.att_h[(div, home)], day, mu_h) / mu_h) \
                     * (self._shrunk(self.def_a[(div, away)], day, mu_h) / mu_h)
        exp_a = mu_a * (self._shrunk(self.att_a[(div, away)], day, mu_a) / mu_a) \
                     * (self._shrunk(self.def_h[(div, home)], day, mu_a) / mu_a)
        return exp_h, exp_a

    def update(self, div, home, away, day, v_h, v_a, sot_h=None, sot_a=None):
        if v_h is not None:
            self.att_h[(div, home)].add(day, v_h)
            self.def_h[(div, home)].add(day, v_a)
            self.att_a[(div, away)].add(day, v_a)
            self.def_a[(div, away)].add(day, v_h)
            self.lg_h[div].add(day, v_h)
            self.lg_a[div].add(day, v_a)
        if self.track_ratio and sot_h is not None:
            self.sot_h[(div, home)].add(day, sot_h)
            self.sot_a[(div, away)].add(day, sot_a)
            self.lg_sot_h[div].add(day, sot_h)
            self.lg_sot_a[div].add(day, sot_a)

    def on_target_ratio(self, div, team, venue, day):
        """Rasio SOT/tembakan trailing tim di satu venue, dihaluskan
        ala Beta-Binomial (eksperimen v5): (S_sot + P * rho) /
        (S_shots + P) dengan P = BB_PRIOR tembakan pseudo untuk
        kedua venue; rho = rasio SOT/tembakan liga ter-decay di
        venue itu."""
        if venue == "h":
            shots_stat = self.att_h[(div, team)]
            sot_stat = self.sot_h[(div, team)]
            lg_shot_s, _ = self.lg_h[div].value_at(day)
            lg_sot_s, _ = self.lg_sot_h[div].value_at(day)
            fb_ratio = FALLBACK["sot"][0] / FALLBACK["shots"][0]
        else:
            shots_stat = self.att_a[(div, team)]
            sot_stat = self.sot_a[(div, team)]
            lg_shot_s, _ = self.lg_a[div].value_at(day)
            lg_sot_s, _ = self.lg_sot_a[div].value_at(day)
            fb_ratio = FALLBACK["sot"][1] / FALLBACK["shots"][1]
        rho = lg_sot_s / lg_shot_s if lg_shot_s > 0 else fb_ratio
        s_shots, _ = shots_stat.value_at(day)
        s_sot, _ = sot_stat.value_at(day)
        return (s_sot + BB_PRIOR * rho) / (s_shots + BB_PRIOR)


# ------------------------------------------------- joint regression ratings
# Disalin dari experiments/sot_model/run_sot_v5.py (RegressionStore)
# dengan lambda tunggal RIDGE_LAM — jangan ubah tanpa verifikasi ulang.
class RegressionStore:
    """Rating SOT regresi Poisson log-linear gabungan per divisi.

    Fit untuk refit di hari D: laga-laga divisi dengan day < D, bobot
    sampel 0.5 ** ((D - day) / HL). Parameter per divisi:
    theta = [beta_h, beta_a, A_1..A_T, D_1..D_T] atas indeks tim tetap
    dari seluruh laga divisi di data (hanya pengindeksan — tim tanpa
    laga sebelum D mempertahankan A = D = 0 lewat ridge). Refit malas:
    permintaan prediksi pertama pada/setelah hari refit terjadwal
    me-refit divisi itu dan menjadwalkan refit REFIT_DAYS hari
    kemudian. Warm start membawa theta antar refit.
    """

    def __init__(self, matches, lambdas):
        self.lambdas = list(lambdas)
        self.divs = {}
        by_div = {}
        for m in matches:
            by_div.setdefault(m["div"], []).append(m)
        for div, ms in by_div.items():
            teams = sorted({m["home"] for m in ms}
                           | {m["away"] for m in ms})
            tidx = {t: i for i, t in enumerate(teams)}
            self.divs[div] = {
                "teams": teams, "tidx": tidx, "T": len(teams),
                "day": np.array([m["day"] for m in ms], dtype=float),
                "hi": np.array([tidx[m["home"]] for m in ms]),
                "ai": np.array([tidx[m["away"]] for m in ms]),
                "yh": np.array([m["hst"] for m in ms], dtype=float),
                "ya": np.array([m["ast"] for m in ms], dtype=float),
                "theta": {}, "next_refit": None,
            }

    def _fit(self, dst, lam, refit_day):
        day, hi, ai = dst["day"], dst["hi"], dst["ai"]
        yh, ya, T = dst["yh"], dst["ya"], dst["T"]
        cut = int(np.searchsorted(day, refit_day, side="left"))
        P = 2 + 2 * T
        theta = dst["theta"].get(lam)
        if theta is None:
            theta = np.zeros(P)
            if cut > 0:
                wm0 = 0.5 ** ((refit_day - day[:cut]) / HL)
                theta[0] = math.log(max(np.average(yh[:cut], weights=wm0),
                                        1e-3))
                theta[1] = math.log(max(np.average(ya[:cut], weights=wm0),
                                        1e-3))
            else:
                theta[0], theta[1] = math.log(4.5), math.log(3.5)
            dst["theta"][lam] = theta
        if cut == 0:
            return
        wm = 0.5 ** ((refit_day - day[:cut]) / HL)
        y = np.concatenate([yh[:cut], ya[:cut]])
        bcol = np.concatenate([np.zeros(cut, dtype=int),
                               np.ones(cut, dtype=int)])
        acol = np.concatenate([hi[:cut], ai[:cut]]) + 2
        dcol = np.concatenate([ai[:cut], hi[:cut]]) + 2 + T
        w = np.concatenate([wm, wm])
        diag = np.arange(P)

        def pll(th):
            eta = np.clip(th[bcol] + th[acol] + th[dcol], ETA_LO, ETA_HI)
            return float(np.sum(w * (y * eta - np.exp(eta)))
                         - 0.5 * lam * np.sum(th[2:] ** 2))

        cur = pll(theta)
        for _ in range(60):
            eta = np.clip(theta[bcol] + theta[acol] + theta[dcol],
                          ETA_LO, ETA_HI)
            mu = np.exp(eta)
            r = w * (y - mu)
            g = np.zeros(P)
            np.add.at(g, bcol, r)
            np.add.at(g, acol, r)
            np.add.at(g, dcol, r)
            g[2:] -= lam * theta[2:]
            W = w * mu
            H = np.zeros((P, P))
            for cc, dd in ((bcol, bcol), (bcol, acol), (bcol, dcol),
                           (acol, bcol), (acol, acol), (acol, dcol),
                           (dcol, bcol), (dcol, acol), (dcol, dcol)):
                np.add.at(H, (cc, dd), W)
            H[diag[2:], diag[2:]] += lam
            H[diag, diag] += 1e-10
            try:
                step = np.linalg.solve(H, g)
            except np.linalg.LinAlgError:
                break
            t, improved = 1.0, False
            for _ in range(25):
                cand = theta + t * step
                v = pll(cand)
                if v >= cur - 1e-12:
                    theta, cur = cand, v
                    improved = True
                    break
                t *= 0.5
            if not improved or np.max(np.abs(t * step)) < 1e-6:
                break
        dst["theta"][lam] = theta

    def _ensure(self, div, day):
        dst = self.divs.get(div)
        if dst is None:
            return None
        if dst["next_refit"] is None or day >= dst["next_refit"]:
            for lam in self.lambdas:
                self._fit(dst, lam, day)
            dst["next_refit"] = day + REFIT_DAYS
        return dst

    def predict(self, div, home, away, day, lam):
        dst = self._ensure(div, day)
        th = dst["theta"][lam]
        T, tidx = dst["T"], dst["tidx"]
        ih, ia = tidx.get(home), tidx.get(away)
        a_h = th[2 + ih] if ih is not None else 0.0
        d_h = th[2 + T + ih] if ih is not None else 0.0
        a_a = th[2 + ia] if ia is not None else 0.0
        d_a = th[2 + T + ia] if ia is not None else 0.0
        eh = math.exp(min(max(th[0] + a_h + d_a, ETA_LO), ETA_HI))
        ea = math.exp(min(max(th[1] + a_a + d_h, ETA_LO), ETA_HI))
        return eh, ea

    def league_mu(self, div, day, lam):
        dst = self._ensure(div, day)
        th = dst["theta"][lam]
        return math.exp(th[0]), math.exp(th[1])


class NaiveTracker:
    """Baseline naif: rata-rata polos trailing-10 laga per tim."""

    def __init__(self):
        self.hist = defaultdict(lambda: deque(maxlen=NAIVE_N))

    def predict(self, div, home, away, mu_h, mu_a):
        hh = self.hist[(div, home)]
        ha = self.hist[(div, away)]
        if hh and ha:
            h_for = sum(x[0] for x in hh) / len(hh)
            h_ag = sum(x[1] for x in hh) / len(hh)
            a_for = sum(x[0] for x in ha) / len(ha)
            a_ag = sum(x[1] for x in ha) / len(ha)
            return (h_for + a_ag) / 2.0, (a_for + h_ag) / 2.0
        return mu_h, mu_a

    def update(self, div, home, away, hst, ast):
        self.hist[(div, home)].append((hst, ast))
        self.hist[(div, away)].append((ast, hst))


def nb_over(lam, r, line):
    """P(X > line) untuk X ~ NegBin(mean=lam, size=r):
    Var = lam + lam^2/r (disalin dari run_sot_v2.py)."""
    k_max = int(math.floor(line))
    q = lam / (r + lam)
    term = (r / (r + lam)) ** r          # P(X = 0)
    cdf = term
    for k in range(1, k_max + 1):
        term *= (k - 1 + r) / k * q
        cdf += term
    return min(max(1.0 - cdf, 0.0), 1.0)


# ------------------------------------------------------------------ state
def _load_history():
    """Seluruh laga bersih yang punya statistik tembakan, kronologis —
    urutan dan filter yang sama dengan eksperimen (baris tanpa HST/AST
    dilewati)."""
    rows = []
    with open(DATA, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r.get("HST") in (None, "") or r.get("AST") in (None, "") \
                    or r.get("HS") in (None, "") or r.get("AS") in (None, ""):
                continue
            rows.append({
                "div": r["Div"], "date": r["Date"],
                "day": date.fromisoformat(r["Date"]).toordinal(),
                "home": r["HomeTeam"], "away": r["AwayTeam"],
                "hs": int(float(r["HS"])), "as": int(float(r["AS"])),
                "hst": int(float(r["HST"])), "ast": int(float(r["AST"])),
            })
    rows.sort(key=lambda m: (m["date"], m["div"], m["home"]))
    return rows


def build_state():
    """Bangun state dari seluruh histori: sistem total tembakan +
    baseline naif diperbarui per laga (update sesudah laga, tanpa
    prediksi); RegressionStore menyimpan array mentah per divisi dan
    me-fit secara malas saat prediksi diminta."""
    rows = _load_history()
    shots = Ratings(HL, K_PRIOR, "shots", track_ratio=True)
    naive = NaiveTracker()
    for m in rows:
        day, div = m["day"], m["div"]
        shots.update(div, m["home"], m["away"], day, m["hs"], m["as"],
                     sot_h=m["hst"], sot_a=m["ast"])
        naive.update(div, m["home"], m["away"], m["hst"], m["ast"])
    reg = RegressionStore(rows, [RIDGE_LAM])
    return reg, shots, naive


def fixture_expectations(reg, shots, naive, div, home, away, day):
    """(exp_h, exp_a, probs) resep v5 untuk satu fixture.

    exp per tim = 0.5 * exp regresi SOT + 0.5 * exp tersirat tembakan;
    probs[line] = 0.5 * NB_over(exp_total) + 0.5 * NB_over(total naif)
    dengan ukuran NB_R yang dibekukan."""
    reh, rea = reg.predict(div, home, away, day, RIDGE_LAM)
    seh, sea = shots.predict(div, home, away, day)
    imp_h = seh * shots.on_target_ratio(div, home, "h", day)
    imp_a = sea * shots.on_target_ratio(div, away, "a", day)
    exp_h = 0.5 * (reh + imp_h)
    exp_a = 0.5 * (rea + imp_a)
    lam = exp_h + exp_a

    mu_h, mu_a = reg.league_mu(div, day, RIDGE_LAM)
    nh, na = naive.predict(div, home, away, mu_h, mu_a)
    lam_n = nh + na

    probs = {L: ENS_W * nb_over(lam, NB_R, L)
             + (1.0 - ENS_W) * nb_over(lam_n, NB_R, L) for L in LINES}
    return exp_h, exp_a, probs


def _recommendation(probs):
    """Garis/sisi dengan probabilitas paling dekat TAPI di atas 0.50
    (garis paling fair yang masih favorit); fallback garis/sisi
    terdekat dari 0.50 bila tidak ada yang di atasnya."""
    best = None        # (jarak, line, side, prob) untuk prob > 0.50
    closest = None     # fallback: jarak terkecil apa pun sisinya
    for L in LINES:
        for side, p in (("Over", probs[L]), ("Under", 1.0 - probs[L])):
            d = abs(p - 0.50)
            if closest is None or d < closest[0]:
                closest = (d, L, side, p)
            if p > 0.50 and (best is None or d < best[0]):
                best = (d, L, side, p)
    _, line, side, p = best if best is not None else closest
    return line, side, p


def _kickoff_in_future(dtf, now_naive):
    """True bila datetime fixture (UTC naif) masih di masa depan —
    pola yang sama dengan model_corners_v3."""
    return dtf > now_naive


def _load_name_map():
    nmap = {}
    for fn in ("map_full.json", "map_ext.json"):
        p = os.path.join(BASE, "xg_raw", fn)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                nmap.update(json.load(f))
    return nmap


def predict_upcoming():
    """Prediksi probabilitas SOT untuk fixture mendatang.

    Membaca fixture dari dump musim {slug}_2026_fixtures.json (sumber
    yang sama dengan model_corners_v3 --predict) dan memetakan nama tim
    ke nama football-data lewat map_full/map_ext.
    """
    reg, shots, naive = build_state()
    nmap = _load_name_map()

    now_naive = datetime.now(timezone.utc).replace(tzinfo=None)
    upcoming = []
    for div, slug in FIX_MAP.items():
        p = os.path.join(BASE, "xg_raw", f"{slug}_2026_fixtures.json")
        if not os.path.exists(p):
            print(f"  ! {p} tidak ada")
            continue
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            if d.get("isResult"):
                continue
            dtf = datetime.strptime(d["datetime"], "%Y-%m-%d %H:%M:%S")
            if not _kickoff_in_future(dtf, now_naive):
                continue
            home = nmap.get(f"{div}|{d['h']['title']}") or d["h"]["title"]
            away = nmap.get(f"{div}|{d['a']['title']}") or d["a"]["title"]
            upcoming.append(dict(div=div, date=dtf.date().isoformat(),
                                 time=dtf.strftime("%H:%M"),
                                 day=dtf.date().toordinal(),
                                 home=home, away=away))

    if not upcoming:
        print("  ! tidak ada fixture upcoming")
        return 0

    # Urut kronologis: panggilan value_at menggerakkan jam decay state
    # dan refit regresi terjadwal per tanggal, jadi prediksi harus
    # monoton naik tanggalnya.
    rows = []
    for fx in sorted(upcoming, key=lambda x: (x["day"], x["div"], x["home"])):
        exp_h, exp_a, probs = fixture_expectations(
            reg, shots, naive, fx["div"], fx["home"], fx["away"], fx["day"])
        rec_line, rec_side, rec_prob = _recommendation(probs)
        row = {
            "div": fx["div"], "date": fx["date"], "time": fx["time"],
            "home": fx["home"], "away": fx["away"],
            "exp_sot_home": round(exp_h, 2), "exp_sot_away": round(exp_a, 2),
            "exp_sot_total": round(exp_h + exp_a, 2),
            "rec_line": rec_line, "rec_side": rec_side,
            "recommendation": f"{rec_side} {rec_line}",
            "rec_prob": round(rec_prob, 4),
        }
        for L in LINES:
            row[f"p_over_{L}"] = round(probs[L], 4)
        rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["time"], r["div"], r["home"]))

    cols = ["div", "date", "time", "home", "away",
            "exp_sot_home", "exp_sot_away", "exp_sot_total",
            "rec_line", "rec_side", "recommendation", "rec_prob"] + \
           [f"p_over_{L}" for L in LINES]

    def write_upcoming(f):
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    _atomic_text_write(UPCOMING_OUT, write_upcoming)
    print(f"  {len(rows)} upcoming SOT predictions -> {UPCOMING_OUT}")
    return len(rows)


if __name__ == "__main__":
    # Validasi/backtest model ini hidup di experiments/sot_model
    # (run_sot_experiment.py, run_sot_v2.py, run_sot_v3.py,
    # run_sot_v5.py); modul produksi hanya memprediksi fixture
    # mendatang.
    print("=== predict upcoming SOT fixtures ===")
    predict_upcoming()
