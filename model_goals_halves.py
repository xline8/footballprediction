"""Pecahan babak (1H/2H) dari prediksi GOL produksi — porsi konstan.

Modul ini BUKAN model baru dan BUKAN model per babak. Ia membaca
lambda full-time produksi (predictions_upcoming.csv, kolom lam_h /
lam_a dari model gol produksi) dan memecah ekspektasi tiap tim
menjadi babak pertama dan babak kedua dengan PORSI KONSTAN yang
dibekukan, per sisi:

    exp_1h_home = lam_h * 0.4419    exp_2h_home = lam_h * (1 - 0.4419)
    exp_1h_away = lam_a * 0.4440    exp_2h_away = lam_a * (1 - 0.4440)

Probabilitas Over tangga 0.5/1.5/2.5 per babak dihitung Poisson murni
pada total babak (jumlah dua Poisson independen adalah Poisson).

Kenapa polos begini — tanpa koreksi, tanpa pemodelan per laga?
- Fit Dixon-Coles per babak KALAH dari pecahan porsi konstan ini
  (eksperimen halves pertama, 2026-11-08).
- Koreksi kalibrasi (skala per babak / rho per babak / NB) diuji dua
  kali: di eksperimen 2 koreksinya mengejar bias fit statis yang
  ternyata artefak harness; di eksperimen 3 — di bawah harness refit
  yang setia ke produksi (refit bulanan, mesin blend produksi persis)
  — kandidat terpilih dari jendela tuning GAGAL validasi di babak 1
  (RESULTS_HALVES_GOALS_V3.md). Koreksi rho/NB yang ter-fit pun
  praktis Poisson (rho 0,00/+0,02; r = 1200).
- Produk yang tayang adalah desain nol (null) yang sudah ada sejak
  studi pertama: parameternya (porsi beku di atas) TIDAK pernah
  di-fit pada jendela validasi. Di bawah harness setia-produksi,
  angka validasinya pada 2023/24–2025/26 (top-5, n = 5.255) adalah:
  kalibrasi Over 1.5 babak 1 +0,22pp, babak 2 −0,71pp — di dalam
  gerbang ±1pp yang sama dengan eksperimen-eksperimen itu.
- Keputusan tayang diambil user 2026-11-08 (pola yang sama dengan
  SOT v9: varian yang dimodelkan kalah, produk porsi konstan yang
  tayang). Konfirmasi pada musim 2026/27 — jendela yang belum pernah
  dipakai memilih apa pun — masih MENUNGGU (berarti sekitar
  n ≈ 1.500, kurang-lebih Februari 2027); bila di sana produk ini
  memburuk, ia ditarik. Catatan keputusan lengkap: addendum di
  RESULTS_HALVES_GOALS_V3.md.

Konsekuensi yang harus dipahami pembaca output:
- Angka babak hanyalah pecahan indikatif dari total full-time
  produksi; TIDAK ada pemodelan babak per laga di sini, dan babak
  secara inheren lebih berisik daripada full-time.
- Belum ada sumber odds gol per babak di sistem — output ini
  probabilitas penyajian saja, bukan penilaian value.

Mode:
  python model_goals_halves.py
Input:
  predictions_upcoming.csv    # output produksi model gol (lam_h/lam_a)
Output:
  predictions_goals_halves_upcoming.csv
"""
import os
import csv
import sys
import math

# Direktori dari paths (sumber kebenaran tunggal), pola yang sama
# dengan model_sot_halves_share.py.
try:
    from paths import BASE
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), "football-data")

from model_sot import _atomic_text_write

GOALS_IN = os.path.join(BASE, "predictions_upcoming.csv")
HALVES_OUT = os.path.join(BASE, "predictions_goals_halves_upcoming.csv")

SHARE_1H_HOME = 0.4419   # porsi babak 1 gol kandang, beku (studi halves 1)
SHARE_1H_AWAY = 0.4440   # porsi babak 1 gol tandang, beku (studi halves 1)
LINES = [0.5, 1.5, 2.5]  # tangga O/U per babak


def pois_over(mu, line):
    """P(X > line) untuk X ~ Poisson(mu): 1 - CDF(lantai(line))."""
    k_max = int(line)
    term = math.exp(-mu)
    total = term
    for k in range(1, k_max + 1):
        term *= mu / k
        total += term
    return 1.0 - total


def build_rows():
    """Baris pecahan babak untuk setiap baris predictions_upcoming
    yang lambda-nya terbaca. Mengembalikan (rows, skipped): baris
    tanpa lam_h/lam_a numerik dilewati dan dihitung.

    Urutan baris mengikuti file input."""
    if not os.path.exists(GOALS_IN):
        print(f"  ! {GOALS_IN} tidak ada — pecahan dilewati")
        return [], 0
    rows, skipped = [], 0
    with open(GOALS_IN, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                lam_h = float(r["lam_h"])
                lam_a = float(r["lam_a"])
            except (KeyError, TypeError, ValueError):
                skipped += 1
                continue
            e1h_h = lam_h * SHARE_1H_HOME
            e1h_a = lam_a * SHARE_1H_AWAY
            e2h_h = lam_h * (1.0 - SHARE_1H_HOME)
            e2h_a = lam_a * (1.0 - SHARE_1H_AWAY)
            tot_1h = e1h_h + e1h_a
            tot_2h = e2h_h + e2h_a
            row = {
                "date": r["date"], "div": r["div"],
                "home": r["home"], "away": r["away"],
                "exp_goals_1h_home": round(e1h_h, 3),
                "exp_goals_1h_away": round(e1h_a, 3),
                "exp_goals_1h_total": round(tot_1h, 3),
                "exp_goals_2h_home": round(e2h_h, 3),
                "exp_goals_2h_away": round(e2h_a, 3),
                "exp_goals_2h_total": round(tot_2h, 3),
            }
            for L in LINES:
                row[f"p_over_1h_{L}"] = round(pois_over(tot_1h, L), 4)
                row[f"p_over_2h_{L}"] = round(pois_over(tot_2h, L), 4)
            rows.append(row)
    return rows, skipped


def predict_upcoming():
    rows, skipped = build_rows()
    if skipped:
        print(f"  ! {skipped} baris tanpa lambda terbaca — dilewati")
    if not rows:
        return 0
    cols = ["date", "div", "home", "away",
            "exp_goals_1h_home", "exp_goals_1h_away", "exp_goals_1h_total",
            "exp_goals_2h_home", "exp_goals_2h_away", "exp_goals_2h_total"] + \
           [f"p_over_1h_{L}" for L in LINES] + \
           [f"p_over_2h_{L}" for L in LINES]

    def write_upcoming(f):
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    _atomic_text_write(HALVES_OUT, write_upcoming)
    print(f"  {len(rows)} upcoming goal halves splits -> {HALVES_OUT}")
    return len(rows)


if __name__ == "__main__":
    # Validasi pecahan hidup di experiments/halves
    # (run_halves_goals_v3.py, RESULTS_HALVES_GOALS_V3.md);
    # modul produksi hanya menerapkan porsi beku ke output produksi.
    print("=== predict upcoming goal halves splits (constant share) ===")
    predict_upcoming()
    sys.exit(0)
