"""Eksperimen: benchmark historis melawan probabilitas 538 SPI.

Pertanyaan (audit ronde 11): di pertandingan yang sama, seberapa baik
probabilitas 1X2 walk-forward kita (meta stack, kini tersimpan di
records skema v2 sebagai ph_meta) dibandingkan probabilitas Soccer
Power Index milik FiveThirtyEight — model eksternal yang dihentikan
pada 2023 dan tidak memakai odds pasar sebagai input utamanya?

Metode:
- SPI: arsip Wayback snapshot 2023-06-25 dari spi_matches.csv
  (endpoint asli projects.fivethirtyeight.com sudah mati). Kolom
  prob1/probtie/prob2 adalah probabilitas pra-pertandingan SPI.
- Kita: records_cache.jsonl skema v2, divisi TOP5, hanya record
  ber-ph_meta (walk-forward bulanan, fit < bulan uji).
- Join pada tanggal + divisi + pasangan nama: SPI memakai nama
  panjang (Leicester City, Chievo Verona, Athletic Club) dan
  football-data nama pendek, jadi nama dinormalisasi dengan
  football_etl.normalize_name, dilipat aksennya (Alavés -> alaves),
  lalu dicocokkan per himpunan token (satu sisi boleh subset dari
  sisi lain); satu alias eksplisit untuk Stade Rennes/Rennais.
  Setiap kandidat wajib lolos verifikasi skor: score1/score2 SPI
  harus sama dengan fthg/ftag record, sehingga join yang lolos
  pasti pertandingan yang sama. Hanya baris SPI yang sudah
  dimainkan (score terisi).
- Skor proper yang sama untuk keduanya pada set pertandingan yang
  identik: Brier multikelas, log loss, RPS; plus bias per kelas dan
  pita reliabilitas probabilitas kandang. ph_dc ikut ditampilkan
  sebagai referensi komponen.

Keterbatasan yang dinyatakan di muka: ini benchmark historis
(2018-01 s/d 2023-06 pada irisan datanya), bukan sumber live; SPI
tidak pernah tersedia untuk divisi di luar cakupannya dan tidak bisa
dipakai untuk keputusan produksi hari ini. Nilainya adalah jangkar
eksternal: apakah stack kita sekelas model publik yang dihormati,
atau tertinggal.

Verdict (run pertama, records skema v2): join 100% pada jendela
SPI — 9.946 dari 9.946 records ber-meta bertanggal <= 2023-06-04
ter-join dan lolos verifikasi skor; semua yang tak ter-join adalah
records setelah SPI berhenti (2023-08+). Pada pertandingan yang
identik itu, stack kita mengungguli SPI di ketiga skor proper,
pooled maupun di kelima divisi: Brier 0,5784 vs 0,5843, log loss
0,9740 vs 0,9821, RPS 0,1969 vs 0,1994 (per divisi RPS kita
0,1897-0,2015 vs SPI 0,1933-0,2039; keunggulan terbesar di I1).
Kaveat yang wajib menyertai angka ini: meta stack kita memakai
probabilitas implied pasar pembuka sebagai 3 dari 9 fiturnya,
sementara SPI adalah model independen-pasar — jadi sebagian
keunggulan mencerminkan informasi pasar yang tidak dipakai SPI,
bukan keunggulan pemodelan murni. Nilai benchmark-nya adalah
jangkar eksternal: probabilitas yang kita sajikan sekelas atau di
atas model publik yang dihormati, pada pertandingan yang sama,
dengan bias per kelas lebih kecil (draw -0,003 vs -0,007).

Data: file CSV SPI dicari di $SPI_CSV, lalu
<repo>/../football-analytics-data/spi_matches_wayback.csv, lalu
<repo>/spi_matches_wayback.csv. Unduh ulang bila hilang:
https://web.archive.org/web/2023/https://projects.fivethirtyeight.com/soccer-api/club/spi_matches.csv

Run: .venv/bin/python experiments/experiment_spi_benchmark.py
"""
import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest_picks import load_records  # noqa: E402
from football_etl import TOP5, normalize_name  # noqa: E402

SPI_LEAGUES = {
    "Barclays Premier League": "E0",
    "German Bundesliga": "D1",
    "Italy Serie A": "I1",
    "Spanish Primera Division": "SP1",
    "French Ligue 1": "F1",
}


def _find_spi_csv():
    cands = [os.environ.get("SPI_CSV"),
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "..", "football-analytics-data",
                          "spi_matches_wayback.csv"),
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "..", "spi_matches_wayback.csv")]
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None


def _brier3(p, y):
    return float(np.mean([sum((p[i][k] - (1.0 if y[i] == k else 0.0)) ** 2
                              for k in range(3))
                          for i in range(len(y))]))


def _logloss3(p, y):
    return float(np.mean([-np.log(max(p[i][y[i]], 1e-12))
                          for i in range(len(y))]))


def _rps(p, y):
    tot = 0.0
    for i in range(len(y)):
        cum_p = np.cumsum(p[i])[:2]
        cum_y = np.array([1.0 if y[i] == 0 else 0.0,
                          1.0 if y[i] <= 1 else 0.0])
        tot += float(np.sum((cum_p - cum_y) ** 2)) / 2.0
    return tot / len(y)


def main():
    path = _find_spi_csv()
    if not path:
        print("file SPI tidak ditemukan; lihat docstring untuk lokasi "
              "dan URL unduh ulangnya")
        return 1
    # Indeks SPI per (tanggal, divisi): nama SPI bentuk panjang,
    # football-data bentuk pendek, jadi pencocokan memakai himpunan
    # token ternormalisasi (subset diperbolehkan) + verifikasi skor.
    import unicodedata
    from collections import defaultdict

    _ALIAS = {"cologne": "koln", "nottingham": "nott"}

    def _tokens(name):
        # Aksen dilipat SEBELUM normalize_name: normalizer project
        # mengganti karakter non-ASCII dengan spasi ("Alavés" menjadi
        # "alav s"), jadi pelipatan sesudahnya tidak menolong.
        n = unicodedata.normalize("NFKD", name)
        n = "".join(c for c in n if not unicodedata.combining(c))
        n = normalize_name(n)
        toks = frozenset(t for tok in n.split()
                         for t in tok.split("-"))
        toks = frozenset(_ALIAS.get(t, t) for t in toks)
        # Alias yang tidak tertangkap subset/aksen: FD "Stade
        # Rennais" vs SPI "Stade Rennes".
        if toks == frozenset({"stade", "rennes"}):
            toks = frozenset({"stade", "rennais"})
        return toks

    spi_by_day = defaultdict(list)
    n_spi_top5 = 0
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            div = SPI_LEAGUES.get(row["league"])
            if div is None or not row["score1"] or not row["score2"]:
                continue
            n_spi_top5 += 1
            spi_by_day[(row["date"], div)].append((
                _tokens(row["team1"]), _tokens(row["team2"]),
                (float(row["prob1"]), float(row["probtie"]),
                 float(row["prob2"])),
                int(row["score1"]), int(row["score2"])))
    print(f"baris SPI TOP5 yang sudah dimainkan: {n_spi_top5:,}")

    def _name_match(a, b):
        return a == b or a < b or b < a

    recs = [r for r in load_records()
            if r["div"] in TOP5 and r.get("ph_meta")]
    ours, theirs, ys, divs = [], [], [], []
    unmatched = []
    for r in recs:
        ht = _tokens(r["home"])
        at = _tokens(r["away"])
        cands = [s for s in spi_by_day.get((r["date"], r["div"]), [])
                 if _name_match(ht, s[0]) and _name_match(at, s[1])
                 and s[3] == r["fthg"] and s[4] == r["ftag"]]
        if len(cands) != 1:
            unmatched.append((r["date"], r["home"], r["away"],
                              len(cands)))
            continue
        ours.append((r["ph_meta"], r["pd_meta"], r["pa_meta"]))
        theirs.append(cands[0][2])
        ys.append(r["yi"])
        divs.append(r["div"])
    # SPI berhenti di akhir musim 2022/23; cakupan join yang jujur
    # dihitung hanya pada records di dalam jendela SPI.
    in_window = [r for r in recs if r["date"] <= "2023-06-04"]
    joined_in_window = len(in_window) - sum(
        1 for u in unmatched if u[0] <= "2023-06-04")
    print(f"records ber-meta: {len(recs):,}; ter-join ke SPI: "
          f"{len(ys):,} ({len(ys) / max(len(recs), 1):.1%})")
    print(f"di dalam jendela SPI (<= 2023-06-04): {len(in_window):,} "
          f"records, ter-join {joined_in_window:,} "
          f"({joined_in_window / max(len(in_window), 1):.1%})")
    if unmatched[:5]:
        print("contoh tak ter-join:", unmatched[:5])
    if not ys:
        return 1

    y = np.array(ys)
    for label, P in (("meta kita", np.array(ours)),
                     ("SPI 538", np.array(theirs))):
        print(f"\n{label} (n={len(y):,}):")
        print(f"  Brier={_brier3(P, y):.4f} LogLoss={_logloss3(P, y):.4f} "
              f"RPS={_rps(P, y):.4f}")
        for k, nm in enumerate(("H", "D", "A")):
            print(f"  bias {nm}: mean_p={P[:, k].mean():.4f} "
                  f"freq={(y == k).mean():.4f} "
                  f"selisih={P[:, k].mean() - (y == k).mean():+.4f}")
    P = np.array(ours)
    print("\nper divisi (RPS kita vs SPI):")
    for div in TOP5:
        idx = [i for i, d in enumerate(divs) if d == div]
        if idx:
            print(f"  {div}: n={len(idx):,} kita={_rps(P[idx], y[idx]):.4f} "
                  f"spi={_rps(np.array(theirs)[idx], y[idx]):.4f}")
    print("\npita reliabilitas probabilitas kandang (kita | SPI):")
    S = np.array(theirs)
    for lo in np.arange(0.0, 1.0, 0.1):
        m = (P[:, 0] >= lo) & (P[:, 0] < lo + 0.1)
        m2 = (S[:, 0] >= lo) & (S[:, 0] < lo + 0.1)
        a = (f"n={int(m.sum()):,} pred={P[m, 0].mean():.3f} "
             f"freq={(y[m] == 0).mean():.3f}") if m.sum() >= 30 else "-"
        b = (f"n={int(m2.sum()):,} pred={S[m2, 0].mean():.3f} "
             f"freq={(y[m2] == 0).mean():.3f}") if m2.sum() >= 30 else "-"
        print(f"  {lo:.1f}-{lo + 0.1:.1f}: {a} | {b}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
