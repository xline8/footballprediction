#!/usr/bin/env python3
"""grade_new_markets.py — grading produksi untuk pasar baru.

Menilai rekomendasi tiga produk yang sebelumnya hanya menulis prediksi
tanpa histori kalibrasi produksi (audit Codex 2026-11-08, Minor 6):

  sot        predictions_sot_upcoming.csv       total SOT (HST+AST)
  cards      predictions_cards_upcoming.csv     total kartu kuning (HY+AY)
  corners_1h predictions_corners_1h_upcoming.csv total corner babak 1

Sumber prediksi: snapshot arsip harian (archive/<tanggal>/, write-once).
Satu baris nilai per (produk, laga): snapshot yang dipakai adalah yang
TERAKHIR terarsip pada atau sebelum tanggal laga — prediksi pra-kickoff
paling segar untuk laga itu. Baris yang sama tidak pernah dinilai dua
kali dari dua tanggal arsip.

Sumber aktual:
  - SOT dan kartu: all_matches_clean.csv (football-data), kolom HST/AST
    dan HY/AY. Bukan API-Football (hasil tidak pernah dari sana).
  - Corner babak 1: data_enrichment/labels_1h_corners.csv — cache label
    gudang FotMob yang sama dengan yang dipakai model_corners_1h
    (stats Periods.FirstHalf), hanya liga top-5.

Pencocokan nama tim memakai normalisasi + alias yang sama resepnya
dengan fotmob_fixtures (_clean/_token_match/ALIAS_GROUPS) ditambah
alias empiris spine<->FotMob dari data_enrichment/fill_halves_gaps.py
('Ath Bilbao' vs 'Athletic Club', dst.).

Keluaran ADITIF — file sendiri, tidak menyentuh ledger rekomendasi
atau calibration_summary.json yang sudah ada:
  ledger/new_market_grades.jsonl   satu baris per (produk, laga)
  ledger/new_market_summary.json   ringkasan per produk

Status per baris: hit / lose / push (sudah dinilai), pending (laga
belum dimainkan), unmatched (laga sudah lewat tapi aktual belum
ketemu — dinilai ulang otomatis pada run berikutnya karena seluruh
store dihitung ulang dari arsip setiap run).

Dijalankan sebagai langkah non-kritis [22/22] di run_daily_shadow.py,
atau standalone: .venv/bin/python grade_new_markets.py
"""

import csv
import json
import os
import sys
import unicodedata
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

ARCHIVE_DIR = os.path.join(HERE, "archive")
SPINE_CSV = os.path.join(HERE, "all_matches_clean.csv")
LABELS_1H_CSV = os.path.join(HERE, "data_enrichment",
                             "labels_1h_corners.csv")
LEDGER_DIR = os.path.join(HERE, "ledger")
GRADES_OUT = os.path.join(LEDGER_DIR, "new_market_grades.jsonl")
SUMMARY_OUT = os.path.join(LEDGER_DIR, "new_market_summary.json")

from grade_recommendations import settle_ou  # noqa: E402

PRODUCTS = {
    "sot": "predictions_sot_upcoming.csv",
    "cards": "predictions_cards_upcoming.csv",
    "corners_1h": "predictions_corners_1h_upcoming.csv",
}


# ------------------------------------------------------------ nama tim
def _clean(name):
    """Normalisasi nama tim: ascii-lower, token (resep fotmob_fixtures)."""
    s = unicodedata.normalize("NFKD", name or "").encode(
        "ascii", "ignore")
    s = s.decode("ascii").lower()
    s = "".join(" " if not ch.isalnum() else ch for ch in s)
    return " ".join(s.split())


# Grup alias satu klub: gabungan ALIAS_GROUPS fotmob_fixtures dan alias
# empiris spine<->FotMob dari fill_halves_gaps.py. Kunci kanonik = nama
# spine (football-data) bila ada.
_ALIAS_GROUPS = [
    {"fc koln", "fc cologne", "1 fc koln", "koln", "cologne"},
    {"rb leipzig", "rasenballsport leipzig"},
    {"ath bilbao", "athletic bilbao", "athletic club"},
    {"ath madrid", "atletico madrid", "atletico de madrid"},
    {"la coruna", "deportivo a coruna", "deportivo la coruna"},
    {"m gladbach", "borussia monchengladbach", "borussia m gladbach"},
    {"hamburg", "hamburger sv"},
    {"west brom", "west bromwich albion"},
    {"paris sg", "paris saint germain", "psg"},
]
_CLUB_KEY = {}
for _grp in _ALIAS_GROUPS:
    _canon = sorted(_grp)[0]
    for _name in _grp:
        _CLUB_KEY[_name] = _canon


def _club_key(clean_name):
    return _CLUB_KEY.get(clean_name, clean_name)


def _token_match(a, b):
    """Satu set token menjadi superset yang lain dengan irisan tak
    kosong (resep fotmob_fixtures._token_match)."""
    if not a or not b:
        return False
    if a == b:
        return True
    ta, tb = set(a.split()), set(b.split())
    if not (ta & tb):
        return False
    return ta <= tb or tb <= ta


def _names_match(pred_name, actual_name):
    cp, ca = _clean(pred_name), _clean(actual_name)
    if _club_key(cp) == _club_key(ca):
        return True
    return _token_match(cp, ca)


def _find_actual(index, date_iso, div, home, away):
    """Cari aktual untuk satu laga di indeks (date, div) -> [entry].

    Urutan: kunci klub kanonik persis kedua sisi; lalu token-match
    kedua sisi yang unik. None bila tidak ketemu / ambigu."""
    cands = index.get((date_iso, div), [])
    if not cands:
        return None
    kh, ka = _club_key(_clean(home)), _club_key(_clean(away))
    for e in cands:
        if e["kh"] == kh and e["ka"] == ka:
            return e
    hits = [e for e in cands
            if _names_match(home, e["home"]) and _names_match(away, e["away"])]
    if len(hits) == 1:
        return hits[0]
    return None


# ------------------------------------------------------------ indeks aktual
def _iso_date(s):
    s = (s or "").strip()
    if "/" in s:  # dd/mm/yyyy -> ISO
        dd, mm, yyyy = s.split("/")
        return f"{yyyy}-{mm}-{dd}"
    return s[:10]


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _spine_index():
    """(date, div) -> [{home, away, kh, ka, sot, cards}] dari file bersih."""
    idx = {}
    if not os.path.exists(SPINE_CSV):
        return idx
    with open(SPINE_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            hst, ast = _num(r.get("HST")), _num(r.get("AST"))
            hy, ay = _num(r.get("HY")), _num(r.get("AY"))
            e = {
                "home": r.get("HomeTeam", ""), "away": r.get("AwayTeam", ""),
                "kh": _club_key(_clean(r.get("HomeTeam", ""))),
                "ka": _club_key(_clean(r.get("AwayTeam", ""))),
                "sot": (hst + ast) if hst is not None and ast is not None
                       else None,
                "cards": (hy + ay) if hy is not None and ay is not None
                         else None,
            }
            idx.setdefault((_iso_date(r.get("Date", "")), r.get("Div", "")),
                           []).append(e)
    return idx


def _labels_1h_index():
    """(date, div) -> [{home, away, kh, ka, total}] corner babak 1."""
    idx = {}
    if not os.path.exists(LABELS_1H_CSV):
        return idx
    with open(LABELS_1H_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if str(r.get("has_1h_corners", "")).strip() not in (
                    "1", "True", "true"):
                continue
            tot = _num(r.get("corners_1h_total"))
            if tot is None:
                continue
            e = {
                "home": r.get("home", ""), "away": r.get("away", ""),
                "kh": _club_key(_clean(r.get("home", ""))),
                "ka": _club_key(_clean(r.get("away", ""))),
                "total": tot,
            }
            idx.setdefault((_iso_date(r.get("date", "")), r.get("div", "")),
                           []).append(e)
    return idx


# ------------------------------------------------------------ grading
def _collect_predictions():
    """Baca semua snapshot arsip -> {(product, date, div, home, away):
    row} dengan snapshot terakhir pada/sebelum tanggal laga."""
    chosen = {}
    if not os.path.isdir(ARCHIVE_DIR):
        return chosen
    for arch_date in sorted(os.listdir(ARCHIVE_DIR)):
        dpath = os.path.join(ARCHIVE_DIR, arch_date)
        if not os.path.isdir(dpath) or len(arch_date) != 10:
            continue
        for product, fn in PRODUCTS.items():
            path = os.path.join(dpath, fn)
            if not os.path.exists(path):
                continue
            with open(path, newline="", encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    key = (product, (r.get("date") or "")[:10],
                           r.get("div", ""), r.get("home", ""),
                           r.get("away", ""))
                    prev = chosen.get(key)
                    # Snapshot pra-kickoff terakhir menang; snapshot yang
                    # terarsip sesudah tanggal laga tidak menggantikan.
                    if prev is None or (
                            arch_date <= key[1]
                            and arch_date >= prev["_archive"]):
                        r = dict(r)
                        r["_archive"] = arch_date
                        chosen[key] = r
    return chosen


def _grade_all(today_iso):
    preds = _collect_predictions()
    spine = _spine_index()
    labels = _labels_1h_index()
    store = {}
    for (product, fdate, div, home, away), r in sorted(preds.items()):
        line = _num(r.get("rec_line"))
        side = r.get("rec_side") or ""
        prob = _num(r.get("rec_prob"))
        row = {
            "product": product, "date": fdate, "div": div,
            "home": home, "away": away,
            "line": line, "side": side, "prob": prob,
            "actual": None, "status": "pending",
            "archive_date": r.get("_archive"),
        }
        if fdate < today_iso and line is not None and side in (
                "Over", "Under"):
            if product in ("sot", "cards"):
                e = _find_actual(spine, fdate, div, home, away)
                actual = None if e is None else e[
                    "sot" if product == "sot" else "cards"]
            else:
                e = _find_actual(labels, fdate, div, home, away)
                actual = None if e is None else e["total"]
            if actual is None:
                row["status"] = "unmatched"
            else:
                row["actual"] = actual
                row["status"] = settle_ou(actual, line, side)
        store[f"{product}|{fdate}|{div}|{home}|{away}"] = row
    return store


def _build_summary(store):
    summary = {}
    for product in PRODUCTS:
        rows = [g for g in store.values() if g["product"] == product]
        settled = [g for g in rows
                   if g["status"] in ("hit", "lose", "push")]
        probs = [g["prob"] for g in settled if g["prob"] is not None]
        summary[product] = {
            "predictions": len(rows),
            "settled": len(settled),
            "hit": sum(1 for g in settled if g["status"] == "hit"),
            "lose": sum(1 for g in settled if g["status"] == "lose"),
            "push": sum(1 for g in settled if g["status"] == "push"),
            "pending": sum(1 for g in rows if g["status"] == "pending"),
            "unmatched": sum(1 for g in rows
                             if g["status"] == "unmatched"),
            "hit_rate_settled": round(
                sum(1 for g in settled if g["status"] == "hit")
                / len(settled), 4) if settled else None,
            "mean_prob_settled": round(sum(probs) / len(probs), 4)
            if probs else None,
        }
    return summary


def _atomic_write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main(argv=None):
    today_iso = datetime.now(timezone.utc).date().isoformat()
    store = _grade_all(today_iso)
    summary = _build_summary(store)
    os.makedirs(LEDGER_DIR, exist_ok=True)
    _atomic_write(GRADES_OUT, "".join(
        json.dumps(store[k], ensure_ascii=False) + "\n"
        for k in sorted(store)))
    payload = {"generated_for_date": today_iso, "products": summary}
    _atomic_write(SUMMARY_OUT,
                  json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
    for product in PRODUCTS:
        s = summary[product]
        print(f"[grade-new] {product}: {s['predictions']} prediksi, "
              f"settled {s['settled']} (hit {s['hit']}, lose {s['lose']}, "
              f"push {s['push']}), pending {s['pending']}, "
              f"unmatched {s['unmatched']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
