"""Model tembakan ke gawang (shots on target / SOT) untuk fixture mendatang.

Resep RAMPING hasil eksperimen experiments/sot_model (keputusan user
2026-11-07): model rating dasar + perbaikan 1 (sinyal total tembakan) +
perbaikan 6 (ensemble 50/50 dengan baseline naif trailing-10). Perbaikan
2 (xG), 3 (negative binomial), 4 (koreksi per divisi) dan 5 (tuning
decay/prior) SENGAJA tidak dipakai — ablasi v2 menunjukkan gabungan
keenamnya (ALL) tidak lebih baik dari resep ramping ini.

Verifikasi resep (run_sot_v3.py, walk-forward 2023/24-2025/26, 21.461
laga, garis utama 9.5, log loss pooled — makin kecil makin baik):
  base 0.6347 | +1 saja 0.6328 | +6 saja 0.6320 | ALL 0.6329 |
  RAMPING (base+1+6) 0.6312, Brier 0.2201, calib err 0.4pp, MAE 2.45.

Mesin rating (disalin persis dari eksperimen agar angka produksi sama
dengan yang terverifikasi):
- Per divisi: rating serang/bertahan SOT per venue (kandang/tandang)
  dari laju ter-decay eksponensial (half-life 365 hari), di-shrink ke
  rata-rata liga ter-decay dengan prior K = 8 match-equivalents;
  exp tim = mu * att * def; total SOT ~ Poisson(exp_home + exp_away).
- Perbaikan 1: sistem rating kedua untuk TOTAL tembakan (HS/AS) dengan
  mesin yang sama, plus rasio on-target trailing ter-shrink per tim per
  venue; exp per tim = 0.5 * exp rating SOT + 0.5 * (exp total tembakan
  x rasio on-target).
- Perbaikan 6: probabilitas Over/Lebih final = 0.5 * P model +
  0.5 * P baseline naif (rata-rata polos 10 laga terakhir per tim).

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

HL = 365.0          # half-life decay rating (hari) — dibekukan dari eksperimen
K_PRIOR = 8.0       # prior shrinkage (match-equivalents)
NAIVE_N = 10        # jendela baseline naif trailing
ENS_W = 0.5         # bobot model rating dalam ensemble (sisanya naif)
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
# Tiga kelas berikut disalin dari experiments/sot_model/run_sot_v2.py
# (yang mereproduksi run_sot_experiment.py) — jangan ubah rumusnya di
# sini tanpa menjalankan ulang verifikasi eksperimennya.
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
    per-laga (SOT atau total tembakan): exp_home = mu_h * att_h(home) *
    def_a(away) dengan rating = laju ter-shrink / mu dan laju
    ter-shrink = (s + K*mu) / (w + K). Dengan track_ratio=True juga
    melacak jumlah SOT ter-decay agar rasio on-target ter-shrink bisa
    dibentuk (dipakai sistem total tembakan)."""

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

    def on_target_ratio(self, div, team, venue, day, mu_shots):
        """Rasio SOT/tembakan trailing ter-shrink tim di satu venue."""
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
        prior_shots = self.k * mu_shots
        return (s_sot + prior_shots * rho) / (s_shots + prior_shots)


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


def poisson_over(lam, line):
    """P(X > line) untuk X ~ Poisson(lam); line berbentuk x.5."""
    k_max = int(math.floor(line))
    term = math.exp(-lam)
    cdf = term
    for k in range(1, k_max + 1):
        term *= lam / k
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
    """Bangun state rating dari seluruh histori (update sesudah laga,
    tanpa prediksi — fixture mendatang semuanya sesudah histori)."""
    sot = Ratings(HL, K_PRIOR, "sot")
    shots = Ratings(HL, K_PRIOR, "shots", track_ratio=True)
    naive = NaiveTracker()
    for m in _load_history():
        day, div = m["day"], m["div"]
        sot.update(div, m["home"], m["away"], day, m["hst"], m["ast"])
        shots.update(div, m["home"], m["away"], day, m["hs"], m["as"],
                     sot_h=m["hst"], sot_a=m["ast"])
        naive.update(div, m["home"], m["away"], m["hst"], m["ast"])
    return sot, shots, naive


def fixture_expectations(sot, shots, naive, div, home, away, day):
    """(exp_h, exp_a, probs) resep ramping untuk satu fixture.

    exp per tim = 0.5 * exp rating SOT + 0.5 * exp tersirat tembakan;
    probs[line] = 0.5 * Poisson_over(exp_total) + 0.5 *
    Poisson_over(total naif) untuk setiap garis di LINES.
    Urutan panggilan state sama dengan pass evaluasi eksperimen."""
    eh, ea = sot.predict(div, home, away, day)
    seh, sea = shots.predict(div, home, away, day)
    mu_sh_h, mu_sh_a, _, _ = shots.league_mu(div, day)
    imp_h = seh * shots.on_target_ratio(div, home, "h", day, mu_sh_h)
    imp_a = sea * shots.on_target_ratio(div, away, "a", day, mu_sh_a)
    exp_h = 0.5 * (eh + imp_h)
    exp_a = 0.5 * (ea + imp_a)
    lam = exp_h + exp_a

    mu_h, mu_a, _, _ = sot.league_mu(div, day)
    nh, na = naive.predict(div, home, away, mu_h, mu_a)
    lam_n = nh + na

    probs = {L: ENS_W * poisson_over(lam, L)
             + (1.0 - ENS_W) * poisson_over(lam_n, L) for L in LINES}
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
    sot, shots, naive = build_state()
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

    # Urut kronologis: panggilan value_at menggerakkan jam decay state,
    # jadi prediksi harus monoton naik tanggalnya.
    rows = []
    for fx in sorted(upcoming, key=lambda x: (x["day"], x["div"], x["home"])):
        exp_h, exp_a, probs = fixture_expectations(
            sot, shots, naive, fx["div"], fx["home"], fx["away"], fx["day"])
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
    # (run_sot_experiment.py, run_sot_v2.py, run_sot_v3.py); modul
    # produksi hanya memprediksi fixture mendatang.
    print("=== predict upcoming SOT fixtures ===")
    predict_upcoming()
