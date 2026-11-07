"""Model kartu kuning (total yellows per laga) untuk fixture mendatang.

Resep hasil eksperimen experiments/cards_model (audit
MODEL_AUDIT_2026-11-07 §3C, keputusan menjalankan semua peluang
2026-11-07): klon resep rating corner/SOT v1 — rating serang/bertahan
kartu per venue yang ter-decay eksponensial, di-shrink ke rata-rata
liga, probabilitas garis dari Negative Binomial. TANPA suku wasit:
audit mengukur kelebihan varians antar-wasit ≈ 0,000 di E0 (satu-satunya
divisi dengan nama wasit di file bersih).

Parameter dibekukan dari jendela tuning SAJA (walk-forward musim
2020/21–2022/23, pemanasan dari 2017/18):
  HL = 270 hari (grid {180, 270, 365} — kurva tuning hampir datar:
  LL@4.5 0.6367 / 0.6366 / 0.6369, jadi pilihan tidak sensitif);
  r NB = 112.39 (method-of-moments dari residual tuning di sekitar
  mean spesifik-laga; estimasi marginal ≈31–38 di audit adalah besaran
  lain — rating menyerap sebagian besar overdispersi marginal, rute
  estimasi yang sama dengan r SOT v5 = 79.94);
  prior shrinkage K = 8 match-equivalents.

Verifikasi resep (run_cards_experiment.py, walk-forward musim uji
2023/24–2025/26, n=5.255, garis utama 4.5, log loss pooled — makin
kecil makin baik):
  model 0.6555 | baseline laju dasar divisi 0.6634 | baseline naif
  trailing-10 0.6623; kalibrasi @4.5 +0.90pp (batas gerbang ≤1pp);
  divisi terburuk vs baseline (a): E0 +0.0001 (batas +0.003).
  Garis konteks: @3.5 model 0.6705, @5.5 model 0.5225 — model juga
  menang di kedua garis itu atas kedua baseline.
Gerbang adopsi (pra-terdaftar di audit §3C): LL@4.5 mengalahkan KEDUA
baseline, |kalibrasi| ≤ 1pp, tidak ada divisi lebih buruk dari
baseline (a) > 0.003 — LOLOS.

Catatan kejujuran yang ikut dari eksperimen: kalibrasi pooled lolos
sempit dan bergantung musim (2023/24 −1.82pp, 2024/25 +2.81pp);
kalibrasi per divisi I1 buruk untuk model DAN baseline (+4.47pp);
E0 nyaris tidak menambah apa-apa atas laju dasar. Tidak ada tambalan
per divisi tanpa backtest terpisah (pelajaran tetap program SOT).
Dan seperti SOT/corner: belum ada odds kartu yang tertangkap sistem,
jadi nilai taruhan model ini belum terbukti — akurasi dulu.

Mode:
  python model_cards.py --predict   # prediksi fixture mendatang
Output:
  predictions_cards_upcoming.csv    # kolom sejajar predictions_sot_upcoming.csv
"""
import os
import csv
import json
import math
import sys
import tempfile
from collections import defaultdict
from datetime import date, datetime, timezone

# Direktori dari paths (sumber kebenaran tunggal), pola yang sama
# dengan model_sot.py / model_corners_v3.py.
try:
    from paths import BASE, DATA_CLEAN as DATA
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), "football-data")
    DATA = os.path.join(BASE, "all_matches_clean.csv")
UPCOMING_OUT = os.path.join(BASE, "predictions_cards_upcoming.csv")
FIX_MAP = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
           "I1": "Serie_A", "F1": "Ligue_1"}
TOP5 = tuple(FIX_MAP)

HL = 270.0          # half-life decay (hari) — disetel 2020/21–2022/23
K_PRIOR = 8.0       # prior shrinkage (match-equivalents)
NB_R = 112.39       # ukuran negative binomial (residual tuning, dibekukan)
LINES = [2.5, 3.5, 4.5, 5.5, 6.5]   # garis terverifikasi: 3.5/4.5/5.5
FB_MU_H, FB_MU_A = 2.15, 1.95       # fallback divisi tanpa histori


def _atomic_text_write(path, writer, newline=""):
    """Tulis artefak teks utuh sebelum diterbitkan ke pembaca
    (pola yang sama dengan model_sot.py)."""
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
class Decayed:
    """(weighted sum, weight) dengan decay eksponensial malas; hl hari.
    Disalin dari experiments/cards_model/run_cards_experiment.py agar
    angka produksi sama dengan yang terverifikasi."""

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


class TeamState:
    __slots__ = ("att_h", "def_h", "att_a", "def_a")

    def __init__(self, hl):
        self.att_h = Decayed(hl)   # kartu diterima saat kandang
        self.def_h = Decayed(hl)   # kartu lawan (diberikan) saat kandang
        self.att_a = Decayed(hl)
        self.def_a = Decayed(hl)


class LeagueState:
    __slots__ = ("mu_h", "mu_a")

    def __init__(self, hl):
        self.mu_h = Decayed(hl)
        self.mu_a = Decayed(hl)


def _shrunk_rate(stat, day, mu):
    s, w = stat.value_at(day)
    return (s + K_PRIOR * mu) / (w + K_PRIOR)


class CardsState:
    """State rating kartu dari seluruh histori bersih (top-5)."""

    def __init__(self):
        self.leagues = defaultdict(lambda: LeagueState(HL))
        self.teams = defaultdict(lambda: TeamState(HL))

    def league_mu(self, div, day):
        lg = self.leagues[div]
        s_h, w_h = lg.mu_h.value_at(day)
        s_a, w_a = lg.mu_a.value_at(day)
        mu_h = s_h / w_h if w_h > 0 else FB_MU_H
        mu_a = s_a / w_a if w_a > 0 else FB_MU_A
        return mu_h, mu_a

    def predict(self, div, home, away, day):
        """(exp_home, exp_away) kartu kuning — rumus eksperimen persis:
        exp_home = mu_h * att_h(home)/mu_h-ter-shrink relatif *
        def_a(away) relatif; cermin untuk tandang."""
        mu_h, mu_a = self.league_mu(div, day)
        th = self.teams[(div, home)]
        ta = self.teams[(div, away)]
        exp_h = mu_h * (_shrunk_rate(th.att_h, day, mu_h) / mu_h) \
                     * (_shrunk_rate(ta.def_a, day, mu_h) / mu_h)
        exp_a = mu_a * (_shrunk_rate(ta.att_a, day, mu_a) / mu_a) \
                     * (_shrunk_rate(th.def_h, day, mu_a) / mu_a)
        return exp_h, exp_a

    def update(self, div, home, away, day, hy, ay):
        th = self.teams[(div, home)]
        ta = self.teams[(div, away)]
        th.att_h.add(day, hy)
        th.def_h.add(day, ay)
        ta.att_a.add(day, ay)
        ta.def_a.add(day, hy)
        lg = self.leagues[div]
        lg.mu_h.add(day, hy)
        lg.mu_a.add(day, ay)


def nb_over(mu, r, line):
    """P(X > line) untuk X ~ NegBin(mean=mu, size=r):
    Var = mu + mu^2/r (sama dengan eksperimen)."""
    k_max = int(math.floor(line))
    q = mu / (r + mu)
    term = (r / (r + mu)) ** r          # P(X = 0)
    cdf = term
    for k in range(1, k_max + 1):
        term *= (k - 1 + r) / k * q
        cdf += term
    return min(max(1.0 - cdf, 0.0), 1.0)


# ------------------------------------------------------------------ state
def _load_history():
    """Seluruh laga bersih top-5 yang punya HY/AY, kronologis — urutan
    dan filter yang sama dengan eksperimen (baris tanpa HY/AY
    dilewati; tepat satu baris seperti itu di data saat adopsi)."""
    rows = []
    with open(DATA, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["Div"] not in TOP5:
                continue
            if r.get("HY") in (None, "") or r.get("AY") in (None, ""):
                continue
            rows.append({
                "div": r["Div"], "date": r["Date"],
                "day": date.fromisoformat(r["Date"]).toordinal(),
                "home": r["HomeTeam"], "away": r["AwayTeam"],
                "hy": int(float(r["HY"])), "ay": int(float(r["AY"])),
            })
    rows.sort(key=lambda m: (m["date"], m["div"], m["home"]))
    return rows


def build_state():
    state = CardsState()
    for m in _load_history():
        state.update(m["div"], m["home"], m["away"], m["day"],
                     m["hy"], m["ay"])
    return state


def _recommendation(probs):
    """Garis/sisi dengan probabilitas paling dekat TAPI di atas 0.50;
    fallback garis/sisi terdekat dari 0.50 (pola model_sot.py)."""
    best = None
    closest = None
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
    """Prediksi probabilitas total kartu kuning untuk fixture mendatang.

    Membaca fixture dari dump musim {slug}_2026_fixtures.json (sumber
    yang sama dengan model_sot.py --predict) dan memetakan nama tim ke
    nama football-data lewat map_full/map_ext.
    """
    state = build_state()
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

    # Urut kronologis: value_at menggerakkan jam decay state secara
    # malas, jadi prediksi harus monoton naik tanggalnya (pola SOT).
    rows = []
    for fx in sorted(upcoming, key=lambda x: (x["day"], x["div"], x["home"])):
        exp_h, exp_a = state.predict(fx["div"], fx["home"], fx["away"],
                                     fx["day"])
        mu = exp_h + exp_a
        probs = {L: nb_over(mu, NB_R, L) for L in LINES}
        rec_line, rec_side, rec_prob = _recommendation(probs)
        row = {
            "div": fx["div"], "date": fx["date"], "time": fx["time"],
            "home": fx["home"], "away": fx["away"],
            "exp_cards_home": round(exp_h, 2),
            "exp_cards_away": round(exp_a, 2),
            "exp_cards_total": round(mu, 2),
            "rec_line": rec_line, "rec_side": rec_side,
            "recommendation": f"{rec_side} {rec_line}",
            "rec_prob": round(rec_prob, 4),
        }
        for L in LINES:
            row[f"p_over_{L}"] = round(probs[L], 4)
        rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["time"], r["div"], r["home"]))

    cols = ["div", "date", "time", "home", "away",
            "exp_cards_home", "exp_cards_away", "exp_cards_total",
            "rec_line", "rec_side", "recommendation", "rec_prob"] + \
           [f"p_over_{L}" for L in LINES]

    def write_upcoming(f):
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    _atomic_text_write(UPCOMING_OUT, write_upcoming)
    print(f"  {len(rows)} upcoming cards predictions -> {UPCOMING_OUT}")
    return len(rows)


if __name__ == "__main__":
    # Validasi/backtest model ini hidup di experiments/cards_model
    # (run_cards_experiment.py); modul produksi hanya memprediksi
    # fixture mendatang.
    print("=== predict upcoming cards fixtures ===")
    predict_upcoming()
