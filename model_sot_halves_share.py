"""Pecahan babak (1H/2H) dari prediksi SOT produksi v5 — porsi konstan.

Modul ini BUKAN model baru. Ia membaca ekspektasi full-time produksi
(model_sot.py resep v5, predictions_sot_upcoming.csv) dan memecahnya
menjadi ekspektasi babak pertama dan babak kedua dengan PORSI LIGA
KONSTAN yang dibekukan:

    exp_1h = exp_ft * S,   exp_2h = exp_ft * (1 - S),   S = 0.4563

dengan S = pangsa SOT babak 1 dari 6.888 laga top-5 berlabel babak
pada 2019/20–2022/23 (era tuning; lihat eksperimen v9).

Kenapa konstan, bukan porsi per laga? Karena porsi yang dimodelkan
per laga (rating per babak + pengali keadaan turun minum, eksperimen
v6/v9) SUDAH diuji secara walk-forward dan KALAH dari porsi konstan
ini pada log loss di kedua babak (+0,0003 babak 1, +0,0012 babak 2;
RESULTS_V9_HALVES_PRODUCT.md). Porsi konstan adalah pemenang validasi
v9, dan pilihan ini disengaja serta terdokumentasi — bukan pembukaan
ulang v9. Jadi: TIDAK ada pemodelan pecahan per laga di sini.

Konsekuensi yang harus dipahami pembaca output:
- Total full-time = produksi v5 apa adanya; angka babak di sini
  hanyalah pecahan indikatif dari total itu.
- Probabilitas Over per babak dihitung dengan mesin negative
  binomial yang sama dengan produksi (nb_over dari model_sot.py)
  pada total babak, dengan ukuran NB beku dari v9:
  r_1H = 86,39 dan r_2H = 1000 (batas estimator momen; residual
  babak 2 era pemanasan praktis berdispersi Poisson).
- Babak secara inheren lebih berisik daripada full-time; jangan
  membaca angka babak setajam angka total v5.

Mode:
  python model_sot_halves_share.py [--predict]
Input:
  predictions_sot_upcoming.csv    # output produksi model_sot.py
Output:
  predictions_sot_halves_upcoming.csv
"""
import os
import csv
import sys

# Direktori dari paths (sumber kebenaran tunggal), pola yang sama
# dengan model_sot.py.
try:
    from paths import BASE
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), "football-data")

from model_sot import _atomic_text_write, nb_over

SOT_IN = os.path.join(BASE, "predictions_sot_upcoming.csv")
HALVES_OUT = os.path.join(BASE, "predictions_sot_halves_upcoming.csv")

SHARE_1H = 0.4563   # porsi babak 1 beku (6.888 laga, 2019/20-2022/23, v9)
R_1H = 86.39        # ukuran NB babak 1 beku (metode momen, v9)
R_2H = 1000.0       # ukuran NB babak 2 beku (batas estimator, ~Poisson, v9)
LINES_1H = [2.5, 3.5, 4.5, 5.5]
LINES_2H = [3.5, 4.5, 5.5, 6.5]


def build_rows():
    """Baris pecahan babak untuk setiap baris predictions_sot_upcoming.

    Urutan baris mengikuti file input (kronologis, sejajar baris
    per baris dengan output produksi v5)."""
    if not os.path.exists(SOT_IN):
        print(f"  ! {SOT_IN} tidak ada — pecahan dilewati")
        return []
    rows = []
    with open(SOT_IN, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            exp_h = float(r["exp_sot_home"])
            exp_a = float(r["exp_sot_away"])
            e1h_h, e1h_a = exp_h * SHARE_1H, exp_a * SHARE_1H
            e2h_h, e2h_a = exp_h * (1.0 - SHARE_1H), exp_a * (1.0 - SHARE_1H)
            tot_1h = e1h_h + e1h_a
            tot_2h = e2h_h + e2h_a
            row = {
                "date": r["date"], "div": r["div"],
                "home": r["home"], "away": r["away"],
                "exp_sot_1h_home": round(e1h_h, 2),
                "exp_sot_1h_away": round(e1h_a, 2),
                "exp_sot_1h_total": round(tot_1h, 2),
                "exp_sot_2h_home": round(e2h_h, 2),
                "exp_sot_2h_away": round(e2h_a, 2),
                "exp_sot_2h_total": round(tot_2h, 2),
            }
            for L in LINES_1H:
                row[f"p_over_1h_{L}"] = round(nb_over(tot_1h, R_1H, L), 4)
            for L in LINES_2H:
                row[f"p_over_2h_{L}"] = round(nb_over(tot_2h, R_2H, L), 4)
            rows.append(row)
    return rows


def predict_upcoming():
    rows = build_rows()
    if not rows:
        return 0
    cols = ["date", "div", "home", "away",
            "exp_sot_1h_home", "exp_sot_1h_away", "exp_sot_1h_total",
            "exp_sot_2h_home", "exp_sot_2h_away", "exp_sot_2h_total"] + \
           [f"p_over_1h_{L}" for L in LINES_1H] + \
           [f"p_over_2h_{L}" for L in LINES_2H]

    def write_upcoming(f):
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    _atomic_text_write(HALVES_OUT, write_upcoming)
    print(f"  {len(rows)} upcoming SOT halves splits -> {HALVES_OUT}")
    return len(rows)


if __name__ == "__main__":
    # Validasi pecahan hidup di experiments/sot_model
    # (run_sot_v9_halves_product.py, RESULTS_V9_HALVES_PRODUCT.md);
    # modul produksi hanya menerapkan porsi beku ke output v5.
    print("=== predict upcoming SOT halves splits (constant share) ===")
    predict_upcoming()
    sys.exit(0)
