"""Pecahan babak (1H/2H) dari prediksi corner produksi — pengurangan.

Modul ini BUKAN model baru. Ia menyusun SATU file penyajian corner
per babak dari dua output produksi yang sudah teradopsi:

- Babak 1: output model corner babak pertama yang teradopsi
  (model_corners_1h.py -> predictions_corners_1h_upcoming.csv),
  dipakai ULANG apa adanya — ekspektasi per tim/total dan tangga
  probabilitas 3.5/4.5/5.5 TIDAK dihitung ulang di sini.
- Full-time: mu model corner FT produksi (model_corners_v3.py ->
  predictions_corners_upcoming.csv, kolom mu_shots_cs, SUDAH termasuk
  pengali dominasi teritorial yang teradopsi) beserta rasio
  dispersinya r_cs.
- Babak 2: DITURUNKAN DENGAN PENGURANGAN, bukan model tersendiri:

      exp_2h = max(mu_ft - exp_1h_total, 1.0)

  Lantai 1.0 adalah pengaman semata (pada file berjalan 2026-11-08
  selisih terkecil yang teramati 4.25, jadi lantai tidak pernah
  mengikat; ia ada supaya baris yang rusak di masa depan tidak
  menghasilkan ekspektasi babak 2 yang mustahil). Probabilitas tangga
  babak 2 (4.5/5.5/6.5) dihitung dengan mesin negative binomial yang
  sama persis dengan model FT (pmf_k/k_of dari model_corners_v3)
  pada dispersi FT r_cs dan rata-rata hasil pengurangan itu.

Konsekuensi yang harus dipahami pembaca output:
- Angka babak 2 mewarisi kesalahan KEDUA model induknya; ia tidak
  pernah di-fit dan tidak punya validasi walk-forward sendiri —
  validasinya adalah validasi kedua model induknya.
- Belum ada sumber odds corner per babak di sistem — output ini
  probabilitas penyajian saja, bukan penilaian value.

Mode:
  python model_corners_halves.py
Input:
  predictions_corners_upcoming.csv      # output produksi model FT
  predictions_corners_1h_upcoming.csv   # output produksi model 1H
Output:
  predictions_corners_halves_upcoming.csv
"""
import os
import csv
import sys

# Direktori dari paths (sumber kebenaran tunggal), pola yang sama
# dengan model_sot_halves_share.py.
try:
    from paths import BASE
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), "football-data")

from football_etl import normalize_name
from model_sot import _atomic_text_write
from model_corners_v3 import pmf_k, k_of

FT_IN = os.path.join(BASE, "predictions_corners_upcoming.csv")
H1_IN = os.path.join(BASE, "predictions_corners_1h_upcoming.csv")
HALVES_OUT = os.path.join(BASE, "predictions_corners_halves_upcoming.csv")

FLOOR_2H = 1.0                 # lantai pengaman ekspektasi babak 2
LINES_1H = [3.5, 4.5, 5.5]     # tangga dari file model 1H (dipakai ulang)
LINES_2H = [4.5, 5.5, 6.5]     # tangga babak 2 (NB dispersi FT)


def _key(r):
    return (r["div"], r["date"], normalize_name(r["home"]),
            normalize_name(r["away"]))


def _nb_over(mu, r, line):
    """P(total > line) dengan mesin NB model corner FT produksi."""
    return sum(pmf_k(mu, k_of(r, mu))[int(line) + 1:])


def build_rows():
    """Satu baris per laga yang ada di KEDUA file induk, mengikuti
    urutan file corner FT. Laga yang hilang di salah satu file
    dilewati (dihitung dan dilaporkan pemanggil)."""
    if not os.path.exists(FT_IN):
        print(f"  ! {FT_IN} tidak ada — corner halves dilewati")
        return [], 0
    if not os.path.exists(H1_IN):
        print(f"  ! {H1_IN} tidak ada — corner halves dilewati")
        return [], 0
    with open(H1_IN, newline="", encoding="utf-8") as fh:
        h1 = {_key(r): r for r in csv.DictReader(fh)}
    rows, skipped = [], 0
    with open(FT_IN, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            o = h1.get(_key(r))
            if o is None:
                skipped += 1
                continue
            mu_ft = float(r["mu_shots_cs"])
            r_cs = float(r["r_cs"])
            e1h = float(o["exp_corners_1h_total"])
            e2h = max(mu_ft - e1h, FLOOR_2H)
            row = {
                "date": r["date"], "div": r["div"],
                "home": o["home"], "away": o["away"],
                "exp_corners_1h_home": o["exp_corners_1h_home"],
                "exp_corners_1h_away": o["exp_corners_1h_away"],
                "exp_corners_1h_total": o["exp_corners_1h_total"],
                "exp_corners_2h_total": round(e2h, 3),
                "exp_corners_ft_total": round(mu_ft, 3),
            }
            for L in LINES_1H:
                row[f"p_over_1h_{L}"] = o[f"p_over_{L}"]
            for L in LINES_2H:
                row[f"p_over_2h_{L}"] = round(_nb_over(e2h, r_cs, L), 4)
            rows.append(row)
    return rows, skipped


def predict_upcoming():
    rows, skipped = build_rows()
    if skipped:
        print(f"  ! {skipped} laga corner FT tanpa pasangan 1H — dilewati")
    if not rows:
        return 0
    cols = ["date", "div", "home", "away",
            "exp_corners_1h_home", "exp_corners_1h_away",
            "exp_corners_1h_total", "exp_corners_2h_total",
            "exp_corners_ft_total"] + \
           [f"p_over_1h_{L}" for L in LINES_1H] + \
           [f"p_over_2h_{L}" for L in LINES_2H]

    def write_upcoming(f):
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    _atomic_text_write(HALVES_OUT, write_upcoming)
    print(f"  {len(rows)} upcoming corner halves -> {HALVES_OUT}")
    return len(rows)


if __name__ == "__main__":
    print("=== predict upcoming corner halves (subtraction) ===")
    predict_upcoming()
    sys.exit(0)
