#!/usr/bin/env python3
"""grade_recommendations.py — grading harian produk independ & rekomendasi.

Menilai tiga produk harian (pick teraman, single, slip ±2, slip ±10) yang
diarsipkan per tanggal di archive/<tanggal>/, dan mengakumulasi hasilnya
menjadi histori kalibrasi:

  ledger/daily_pick_grades.jsonl   — append-only, satu baris per unit
  ledger/calibration_summary.json  — ditulis ulang tiap run

Sumber hasil: ta/results.csv (tipsterarea FT 90 menit) — TANPA
API-Football. Corner aktual dari HC/AC di all_matches_clean.csv (laga liga);
corner piala tidak punya sumber aktual -> ungratefulable (dikeluarkan dari
statistik). Slip unit dinilai dengan aturan: satu leg kalah -> unit kalah;
leg push dikeluarkan; semua leg hit -> hit; leg pending -> unit pending.

Idempoten: kunci unik (date, product, level, home, away, market, line,
selection). Re-run tidak menduplikasi; baris pending boleh diperbarui ke
final saat hasil terbit. Kegagalan langkah ini tidak menggagalkan pipeline.

Run: python grade_recommendations.py
"""
import csv
import hashlib
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE = os.path.join(HERE, "archive")
RESULTS = os.path.join(HERE, "ta", "results.csv")
CORNER_DATA = os.path.join(HERE, "all_matches_clean.csv")
LEDGER = os.path.join(HERE, "ledger")
GRADES = os.path.join(LEDGER, "daily_pick_grades.jsonl")
SUMMARY = os.path.join(LEDGER, "calibration_summary.json")

TOP5 = ("E0", "D1", "I1", "SP1", "F1")
CUP_COMP = ("EFL Cup", "DFB Pokal")
CUP_LEAGUE = {"EFL Cup": "England - EFL Cup", "DFB Pokal": "Germany - Cup Germany"}

PRODUCT_FILES = {
    "best_picks_today.csv": "pick_teraman",
    "recommended_single.csv": "single",
    "recommended_slip.csv": "slip2",
    "recommended_slip10.csv": "slip10",
}
SLIP_PRODUCTS = ("slip2", "slip10")

BANDS = [(0.50, 0.60), (0.60, 0.70), (0.70, 0.80),
         (0.80, 0.90), (0.90, 1.00)]
MIN_BAND = 0.50

from ta_model import norm, sim  # noqa: E402


# ---------------------------------------------------------------- settlement murni
def settle_1x2(sh, sa, sel):
    """1X2 dari skor FT 90 menit."""
    if sel == "1":
        return "hit" if sh > sa else "lose"
    if sel == "2":
        return "hit" if sa > sh else "lose"
    if sel == "X":
        return "hit" if sh == sa else "lose"
    return None


def settle_dc(sh, sa, sel):
    """Double Chance: kombinasi dua hasil 1X2."""
    if sel == "1X":
        return "hit" if sh >= sa else "lose"
    if sel == "X2":
        return "hit" if sh <= sa else "lose"
    if sel == "12":
        return "hit" if sh != sa else "lose"
    return None


def settle_ou(total, line, side):
    """Total goal/corner vs garis. Garis bulat bisa push (` total == line)."""
    ln = float(line)
    if total > ln:
        return "hit" if side == "Over" else "lose"
    if total < ln:
        return "hit" if side == "Under" else "lose"
    return "push"  # garis bulat: total sama persis


def settle_btts(sh, sa, side):
    """Kedua tim mencetak gol."""
    b = sh > 0 and sa > 0
    return "hit" if b == (side == "Yes") else "lose"


def settle_corner(total, line, side):
    """Sama dgn OU, tapi total dari HC+AC."""
    return settle_ou(total, line, side)


def settle_slip_unit(statuses):
    """Settlement unit slip dari status leg.

    - satu leg kalah -> unit kalah
    - leg push dikeluarkan (unit dinilai dari sisa)
    - semua sisa hit -> hit; tanpa sisa -> push
    - ada leg pending -> pending; leg ungratefulable dikeluarkan seperti push
    """
    if any(s == "pending" for s in statuses):
        return "pending"
    eff = [s for s in statuses if s != "ungradeable"]
    if not eff:
        return "ungradeable" if any(s == "ungradeable" for s in statuses) else "push"
    if any(s == "lose" for s in eff):
        return "lose"
    rem = [s for s in eff if s != "push"]
    if not rem:
        return "push"
    return "hit"


# ---------------------------------------------------------------- io
def _read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _result_index():
    """date -> [(norm_home, norm_away, sh, sa, league)] untuk baris FT."""
    idx = defaultdict(list)
    for r in _read_csv(RESULTS):
        if r.get("status") != "FT":
            continue
        try:
            sh, sa = int(r["score_h"]), int(r["score_a"])
        except (TypeError, ValueError):
            continue
        d = r.get("date") or ""
        if not d:
            continue
        idx[d].append((norm(r.get("home") or ""), norm(r.get("away") or ""),
                       sh, sa, r.get("league") or ""))
    return idx


POSTPONE_MAX_DAYS = 45


def _match_result(idx, match_date, home, away, comp):
    """Cari skor FT untuk (tanggal, home, away).

    Skor = kemiripan nama (sim) kedua tim; hint kompetisi piala memberi
    dorongan kecil untuk memisahkan laga liga vs piala di tanggal sama.
    Return (skor_home, skor_away, tanggal_hasil) atau None.

    Fallback laga tunda (audit ronde 12, C12-4): lookup utama
    berjangkar tanggal pick, jadi laga yang digeser ke tanggal lain
    tidak akan pernah ter-grade. Bila tanggal persis gagal, tanggal
    SETELAH tanggal pick dipindai menaik dan tanggal paling awal
    dengan kandidat meyakinkan yang dipakai — pasangan tim yang sama
    bertemu lagi di putaran kedua, jadi mengambil yang paling akhir
    akan menilai leg dengan laga yang salah.

    Pemindaian dibatasi POSTPONE_MAX_DAYS hari (audit ronde 13): tanpa
    batas, leg dari laga yang DIBATALKAN (tidak pernah dimainkan)
    akan settle dari pertemuan berikutnya pasangan yang sama —
    berbulan-bulan kemudian, mungkin di kompetisi lain — dan grade
    final tidak pernah ditulis ulang. Tanggal hasil yang cocok kini
    dikembalikan dan dicatat di baris grade (result_date) supaya
    penilaian tunda selalu bisa diaudit sesudahnya.
    """
    nh, na = norm(home), norm(away)
    hint = CUP_LEAGUE.get(comp or "")

    def _best_on(cands):
        best, bs = None, 0.0
        for rh, ra, sh, sa, lge in cands or []:
            s_h, s_a = sim(nh, rh), sim(na, ra)
            # Lantai per sisi (audit ronde 15): ambang produk 0,75
            # bisa dicapai pasangan timpang (1,00 x 0,75, atau
            # 0,72 + bonus piala) — satu sisi pasti, satu sisi
            # meragukan. Pasangan sejati yang terukur di data
            # produksi selalu >= 0,95 per sisi, jadi kedua sisi
            # dituntut >= 0,80. Pemicunya: leg Bundesliga sempat
            # dinilai dari laga Selandia Baru bertanggal sama
            # (token "b" menggelembungkan sim; diperbaiki di
            # ta_model.sim — lantai ini lapis keduanya).
            if min(s_h, s_a) < 0.80:
                continue
            sc = s_h * s_a
            if hint and lge == hint:
                sc += 0.05
            if sc > bs:
                bs, best = sc, (sh, sa)
        return best if bs >= 0.75 else None

    got = _best_on(idx.get(match_date))
    if got is not None:
        return got[0], got[1], match_date
    try:
        limit = (date.fromisoformat(match_date)
                 + timedelta(days=POSTPONE_MAX_DAYS)).isoformat()
    except (TypeError, ValueError):
        limit = None
    for d in sorted(idx):
        if d <= match_date:
            continue
        if limit is not None and d > limit:
            break
        got = _best_on(idx[d])
        if got is not None:
            return got[0], got[1], d
    return None


def _corner_actuals_index():
    """(date, home_norm, away_norm) -> hc+ac untuk laga liga TOP5."""
    idx = {}
    for r in _read_csv(CORNER_DATA):
        if r.get("Div") not in TOP5:
            continue
        hc, ac = _f(r.get("HC")), _f(r.get("AC"))
        if hc is None or ac is None:
            continue
        idx[(r.get("Date") or "", norm(r.get("HomeTeam") or ""),
             norm(r.get("AwayTeam") or ""))] = int(hc + ac)
    return idx


# ---------------------------------------------------------------- kunci idempoten
def _key(g):
    return (g["date"], g["product"], g["level"], g["home"], g["away"],
            g["market"], g["line"], g["selection"])


def _same(a, b):
    """True bila dua grade setara (abaikan graded_at — cap waktu tiap run)."""
    if len(a) != len(b):
        return False
    for k, v in a.items():
        if k == "graded_at":
            continue
        if k not in b or b[k] != v:
            return False
    return True


def _load_grades():
    store = {}
    if os.path.exists(GRADES):
        with open(GRADES, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                g = json.loads(line)
                store[_key(g)] = g
    return store


def _save_grades(store):
    os.makedirs(LEDGER, exist_ok=True)
    rows = sorted(store.values(), key=lambda g: _key(g))
    # Tulis atomik (tmp + replace): file ini ditulis ulang PENUH setiap
    # run; penulisan langsung bisa meninggalkan file terpotong bila
    # proses mati di tengah (riwayat grading hilang / JSON rusak).
    tmp = GRADES + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for g in rows:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    os.replace(tmp, GRADES)
    return rows


# ---------------------------------------------------------------- per-leg grading
def _grade_leg(product, row, res_idx, cor_idx):
    """Kembalikan dict grade untuk satu leg (status ditentukan)."""
    match_date = (row.get("date") or "").strip()
    home = (row.get("home") or "").strip()
    away = (row.get("away") or "").strip()
    comp = (row.get("competition") or "").strip()
    market = (row.get("market") or "").strip()
    line = (row.get("line") or "").strip()
    if product == "pick_teraman":
        sel = (row.get("side") or "").strip()
        p_model = _f(row.get("prob"))
        odds = None
        tier = (row.get("tier") or "").strip()
    else:
        sel = (row.get("selection") or "").strip()
        p_model = _f(row.get("p_model"))
        odds = _f(row.get("o_1xbet"))
        tier = ""

    g = {"date": match_date, "product": product, "level": "leg",
         "home": home, "away": away, "competition": comp,
         "market": market, "line": line, "selection": sel,
         "p_model": p_model, "odds": odds, "tier": tier,
         "status": "pending", "score": "", "reason": "", "graded_at": "",
         "result_date": ""}

    mkt = market.lower()
    if mkt in ("corners", "corner", "corner total"):
        # corner: aktual dari HC/AC (liga); piala tanpa sumber -> ungratefulable
        if comp in CUP_COMP:
            g["status"] = "ungradeable"
            g["reason"] = "no_actuals_source"
            return g
        key = (match_date, norm(home), norm(away))
        total = cor_idx.get(key)
        if total is None:
            g["status"] = "pending"
            g["reason"] = "corner_actuals_pending"
            return g
        st = settle_corner(total, line, sel)
        if st is None:
            g["status"] = "pending"
            g["reason"] = "unknown_selection"
            return g
        g["status"] = st
        g["score"] = f"{total}"
        g["graded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        return g

    # pasar hasil (1X2/DC/OU/BTTS): butuh skor FT
    res = _match_result(res_idx, match_date, home, away, comp)
    if res is None:
        g["status"] = "pending"
        g["reason"] = "no_result_yet"
        return g
    sh, sa, rdate = res
    g["result_date"] = rdate
    if mkt in ("1x2", "1 x 2"):
        st = settle_1x2(sh, sa, sel)
    elif mkt == "dc":
        st = settle_dc(sh, sa, sel)
    elif mkt in ("ou", "over/under"):
        st = settle_ou(sh + sa, line, sel)
    elif mkt in ("bts", "btts"):
        st = settle_btts(sh, sa, sel)
    else:
        g["status"] = "pending"
        g["reason"] = "unknown_market"
        return g
    if st is None:
        g["status"] = "pending"
        g["reason"] = "unknown_selection"
        return g
    g["status"] = st
    g["score"] = f"{sh}-{sa}"
    g["graded_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return g


# ---------------------------------------------------------------- per-arsip
def _grade_archive(archive_date, store, res_idx, cor_idx, now, seen=None):
    d = os.path.join(ARCHIVE, archive_date)
    if not os.path.isdir(d):
        return 0
    changed = 0
    for fname, product in PRODUCT_FILES.items():
        fpath = os.path.join(d, fname)
        if not os.path.exists(fpath):
            continue  # produk tidak ada di arsip tanggal itu — lewati
        rows = _read_csv(fpath)
        if not rows:
            continue
        # grade legs
        leg_statuses = []
        leg_grades = []
        for row in rows:
            g = _grade_leg(product, row, res_idx, cor_idx)
            leg_grades.append(g)
            k = _key(g)
            if seen is not None:
                seen.add(k)
            old = store.get(k)
            # Tulis bila: baru; berubah DAN (yang baru final — termasuk
            # finalisasi dari pending — atau yang lama masih pending).
            # Pending yang di-regenerasi arsip dengan harga/p_model
            # terkoreksi ikut segar; final tidak pernah di-downgrade
            # menjadi pending.
            if old is None or (
                    not _same(old, g)
                    and (g["status"] != "pending"
                         or old["status"] == "pending")):
                g["graded_at"] = g["graded_at"] or now
                store[k] = g
                changed += 1
            leg_statuses.append(g["status"])
        # unit slip (slip2/slip10): satu unit per produk per tanggal arsip
        if product in SLIP_PRODUCTS:
            unit_status = settle_slip_unit(leg_statuses)
            unit_g = {
                "date": archive_date, "product": product, "level": "unit",
                "home": "", "away": "", "competition": "",
                "market": "", "line": "", "selection": "",
                "p_model": None, "odds": None, "tier": "",
                "status": unit_status,
                "score": "", "reason": "",
                "graded_at": now,
            }
            if unit_status == "pending":
                unit_g["reason"] = "legs_pending"
            elif unit_status == "ungradeable":
                unit_g["reason"] = "no_actuals_source"
            if unit_g["status"] != "pending":
                unit_g["graded_at"] = now
            # p_model/odds unit dari kolom agregat slip (bila ada)
            jp = _f(rows[0].get("slip_joint_prob"))
            tot = _f(rows[0].get("slip_total_odds"))
            unit_g["p_model"] = jp
            unit_g["odds"] = tot
            # Identitas unit = ISI slip (gabungan kunci leg-nya), bukan
            # tanggal arsip. Dulu unit dikunci per tanggal arsip, jadi
            # file rekomendasi basi yang terarsip ulang di tanggal lain
            # (rantai harian tetap mengarsipkan walau langkah produksi
            # gagal) menghasilkan unit kedua untuk slip fisik yang sama
            # dan statistik unit di ringkasan terhitung ganda. Kunci leg
            # sendiri sudah berbasis isi (tanggal laga/pasar/pilihan).
            leg_sig = ";".join(sorted(
                "|".join(map(str, _key(g))) for g in leg_grades))
            unit_g["selection"] = "unit:" + hashlib.md5(
                leg_sig.encode()).hexdigest()[:12]
            # Tanggal kunci unit = tanggal leg TERPAwal slip itu sendiri
            # (isi), BUKAN tanggal arsip. Fix PR #23 hanya memindahkan
            # hash isi ke field selection, tapi _key() tetap diawali
            # tanggal arsip — audit ronde 3 membuktikan lewat simulasi
            # bahwa slip yang sama di dua tanggal arsip tetap menjadi
            # dua unit. Dengan tanggal dari isi, kuncinya kini identik
            # lintas tanggal arsip.
            if leg_grades:
                unit_g["date"] = min(g["date"] for g in leg_grades)
            uk = _key(unit_g)
            # Migrasi: buang unit skema lama (selection kosong) untuk
            # produk + tanggal arsip ini agar tidak jadi pending yatim.
            for k in [k for k, v in store.items()
                      if v["level"] == "unit" and v["product"] == product
                      and v["date"] == archive_date and not v["selection"]]:
                del store[k]
                changed += 1
            # Migrasi: buang duplikat sig yang sama di kunci tanggal
            # arsip lain (sisa skema tanggal-arsip dari PR #23).
            for k in [k for k, v in store.items()
                      if v["level"] == "unit" and v["product"] == product
                      and v["selection"] == unit_g["selection"] and k != uk]:
                del store[k]
                changed += 1
            if seen is not None:
                seen.add(uk)
            uold = store.get(uk)
            if uold is None or (
                    not _same(uold, unit_g)
                    and (unit_g["status"] != "pending"
                         or uold["status"] == "pending")):
                store[uk] = unit_g
                changed += 1
    return changed


# ---------------------------------------------------------------- proses ulang store
def _leg_row_from_store(g):
    """Bangun baris produk dari baris leg tersimpan di store, untuk
    dinilai ulang oleh _grade_leg (pemetaan kebalikan dari yang
    ditulis _grade_archive)."""
    row = {"date": g["date"], "home": g["home"], "away": g["away"],
           "competition": g["competition"], "market": g["market"],
           "line": g["line"]}
    if g["product"] == "pick_teraman":
        row["side"] = g["selection"]
        row["prob"] = g["p_model"]
        row["tier"] = g["tier"]
    else:
        row["selection"] = g["selection"]
        row["p_model"] = g["p_model"]
        row["o_1xbet"] = g["odds"]
    return row


def _find_unit_legs(unit, cand_keys, store):
    """Kembalikan tuple kunci leg penyusun `unit`, atau None.

    Ukuran subset dibatasi 6 = batas generator (slip_recommender:
    slip2 ≤ 4 leg, slip10 ≤ 6 leg); unit ber-leg lebih dari itu
    hanya bisa lahir dari file korup dan memang tidak dicari.
    Kecocokan hash pertama langsung dipakai — dua himpunan leg
    berbeda yang berbagi sidik md5-48 yang sama bukan ambiguitas
    realistis, dan versi enumerasi-penuh ronde 15 membayar biaya
    kombinatoriknya di SETIAP run untuk unit yang tak bisa pulih
    (audit ronde 16, A16-1: jendela 40 kandidat = 52,6 detik).

    Biaya ditekan tanpa mengubah vonis (hash isi tetap penentu
    akhir), lewat pencarian dua fase:
    - Fase 1 (cepat): DFS menyaring produk odds dan produk
      p_model terhadap angka unit tersimpan — produk odds hanya
      naik (semua odds leg ≥ 1), produk p hanya turun (p ≤ 1),
      jadi jalur di luar pita toleransi 2% tidak akan kembali
      masuk. Ini menutup kasus normal segenerasi (selisih
      pembulatan cetak < 0,5%).
    - Fase 2 (eksak): hash murni tanpa saringan numerik, hanya
      early-exit + anggaran node. WAJIB ada karena pita fase 1
      bisa menolak subset sejati tepat di skenario penyelamatan
      itu sendiri: unit arsip 2026-10-30 '518d' menyimpan leg
      dari generasi file berbeda — p_model-nya cocok persis
      (probabilitas model stabil antar-generasi) tetapi odds
      pasarnya sudah bergerak 3,1% dari total unit tersimpan.
      Vonis tidak pernah bergantung pada toleransi: fase 2
      menemukan apa pun yang enumerasi lama temukan, selama
      anggaran node cukup — dan anggaran 300 ribu node menampung
      enumerasi penuh jendela sampai ±25 kandidat (17 kandidat
      ≈ 33 ribu kombinasi, 25 kandidat ≈ 245 ribu) dengan biaya
      terburuk di bawah satu detik. Melewati anggaran, pencarian menyerah dan
      unit tetap pending: degradasi terbatas pada jendela
      raksasa berangka korup, bukan lagi 52 detik per run.
    String kunci tiap leg kandidat dibangun sekali per fase,
    bukan per kombinasi. Fase 1 dilewati bila angka unit atau
    satu pun leg kandidat tidak lengkap.
    """
    target = unit["selection"]
    items = [(lk, store[lk]) for lk in cand_keys]
    key_str = {lk: "|".join(map(str, _key(lg))) for lk, lg in items}
    u_odds, u_p = unit["odds"], unit["p_model"]
    filtered = (u_odds is not None and u_p is not None and all(
        lg["odds"] is not None and lg["odds"] >= 1.0
        and lg["p_model"] is not None and lg["p_model"] <= 1.0
        for _, lg in items))
    def search(use_filters, budget):
        found = []

        def dfs(start, chosen, odds_prod, p_prod, size):
            # Ukuran subset dijelajahi menaik (1..6) seperti
            # enumerasi versi lama: DFS sedalam-dalamnya lebih
            # dulu akan menghabiskan anggaran node pada subset
            # berawalan kandidat awal sebelum sempat mencoba
            # kombinasi kecil di akhir daftar.
            if found or budget[0] <= 0:
                return
            budget[0] -= 1
            if len(chosen) == size:
                if (not use_filters
                        or (abs(odds_prod - u_odds) <= 0.02 * u_odds
                            and abs(p_prod - u_p) <= 0.02 * u_p)):
                    sig = ";".join(sorted(key_str[lk] for lk in chosen))
                    if ("unit:" + hashlib.md5(sig.encode()).hexdigest()[:12]
                            == target):
                        found.append(tuple(chosen))
                return
            for i in range(start, len(items)):
                lk, lg = items[i]
                n_odds, n_p = odds_prod, p_prod
                if use_filters:
                    n_odds = odds_prod * lg["odds"]
                    n_p = p_prod * lg["p_model"]
                    if n_odds > u_odds * 1.02 or n_p < u_p * 0.98:
                        continue
                chosen.append(lk)
                dfs(i + 1, chosen, n_odds, n_p, size)
                chosen.pop()
                if found or budget[0] <= 0:
                    return

        for size in (1, 2, 3, 4, 5, 6):
            if size > len(items):
                break
            dfs(0, [], 1.0, 1.0, size)
            if found or budget[0] <= 0:
                break
        return found[0] if found else None

    if filtered:
        hit = search(True, [300_000])
        if hit is not None:
            return hit
    return search(False, [300_000])


def _regrade_orphans(store, seen, res_idx, cor_idx, now):
    """Nilai baris PENDING yang tidak ter-regenerasi arsip mana pun
    pada run ini, langsung dari store — dipanggil SEBELUM pemangkasan
    yatim di main().

    Audit ronde 15 (C15-1): grader murni digerakkan arsip, jadi leg
    yang file arsipnya rusak/tergenerasi ulang (archive/2026-10-30:
    slip kosong, slip10 berisi leg tanggal lain) tidak pernah dinilai
    ulang — satu-satunya jalan keluarnya adalah prune, dan 13 leg
    2026-10-30 yang laganya sudah FT nyaris terhapus tanpa grade
    (mekanisme yang sama dengan yatim Le Havre ronde 14, yang saat
    itu diselamatkan manual). Kini leg yatim dinilai dari indeks
    hasil yang sama seperti jalur arsip; yang hasilnya belum ada
    tetap pending dan tetap tunduk pada aturan prune yang sama.

    Unit slip yatim: identitas unit adalah hash isi leg-legnya
    (lihat _grade_archive), jadi keanggotaan unit bisa dipulihkan
    secara eksak — subset leg store yang hash isinya sama persis
    dengan sidik unit (pencariannya di _find_unit_legs). Tanpa
    kecocokan, unit dibiarkan pending (prune usia 14 hari tetap
    menjadi jalan keluar terakhirnya).
    Return jumlah baris yang berubah.
    """
    changed = 0
    # leg dulu: status leg menentukan status unit di bawah.
    for k in sorted(store):
        g = store[k]
        if k in seen or g["status"] != "pending" or g["level"] != "leg":
            continue
        ng = _grade_leg(g["product"], _leg_row_from_store(g),
                        res_idx, cor_idx)
        if ng["status"] == "pending":
            continue
        ng["graded_at"] = ng["graded_at"] or now
        if not _same(g, ng):
            store[k] = ng
            changed += 1

    legs_by_product = defaultdict(list)
    for k, g in store.items():
        if g["level"] == "leg" and g["product"] in SLIP_PRODUCTS:
            legs_by_product[g["product"]].append(k)
    for k in sorted(store):
        g = store[k]
        if (k in seen or g["status"] != "pending"
                or g["level"] != "unit"
                or g["product"] not in SLIP_PRODUCTS
                or not (g["selection"] or "").startswith("unit:")):
            continue
        try:
            # Jendela harus menampung ekspansi pool slip10 yang sah:
            # leg bisa jatuh sampai tanggal unit + S10_MAX_EXPAND_DAYS
            # (4 hari, slip_recommender) — audit-diri ronde 15, L1.
            last = (date.fromisoformat(g["date"])
                    + timedelta(days=4)).isoformat()
        except (TypeError, ValueError):
            continue
        cands = sorted(lk for lk in legs_by_product[g["product"]]
                       if g["date"] <= store[lk]["date"] <= last)
        combo = _find_unit_legs(g, cands, store)
        if combo is None:
            continue
        st = settle_slip_unit([store[lk]["status"] for lk in combo])
        if st == "pending":
            continue
        ng = dict(g)
        ng["status"] = st
        ng["reason"] = "no_actuals_source" if st == "ungradeable" else ""
        ng["graded_at"] = now
        if not _same(g, ng):
            store[k] = ng
            changed += 1
    return changed


# ---------------------------------------------------------------- ringkasan
def _stats(final_legs):
    npush = [g for g in final_legs if g["status"] != "push"]
    push = sum(1 for g in final_legs if g["status"] == "push")
    n = len(npush)
    if n == 0:
        return {"n": 0, "mean_p": None, "hit_rate": None, "diff": None,
                "push": push}
    with_p = [g for g in npush if g["p_model"] is not None]
    mean_p = (sum(g["p_model"] for g in with_p) / len(with_p)) if with_p \
        else None
    hit = sum(1 for g in npush if g["status"] == "hit")
    hr = hit / n
    return {"n": n,
            "mean_p": round(mean_p, 4) if mean_p is not None else None,
            "hit_rate": round(hr, 4),
            "diff": round(hr - mean_p, 4) if mean_p is not None else None,
            "push": push}


def _band(p):
    if p is None:
        return None
    if p < MIN_BAND:
        return "<0.50"
    for lo, hi in BANDS:
        if lo <= p < hi:
            return f"{lo:.2f}-{hi:.2f}"
    return "0.90-1.00"


def _build_summary(store):
    fin = {k: g for k, g in store.items()
           if g["status"] in ("hit", "lose", "push")}
    legs = [g for g in fin.values() if g["level"] == "leg"]
    units = [g for g in fin.values() if g["level"] == "unit"]

    summary = {"overall": _stats(legs)}

    # overall menghitung LEG per produk: seleksi yang sama bisa muncul
    # di dua produk (mis. single yang juga menjadi leg slip2) dan
    # terhitung dua kali. overall_unique men-dedup per seleksi agar
    # ukuran sampel uniknya terbaca di samping angka leg
    # (audit ronde 7).
    _uniq = {}
    for g in legs:
        k = (g.get("date"), g.get("home"), g.get("away"),
             g.get("market"), g.get("line"), g.get("selection"))
        _uniq.setdefault(k, g)
    summary["overall_unique"] = _stats(list(_uniq.values()))

    # by_product
    by_product = {}
    for p in ("pick_teraman", "single", "slip2", "slip10"):
        pl = [g for g in legs if g["product"] == p]
        entry = {"leg": _stats(pl)}
        if p in SLIP_PRODUCTS:
            pu = [g for g in units if g["product"] == p]
            entry["unit"] = _stats(pu)
        by_product[p] = entry
    summary["by_product"] = by_product

    # by_market — semua produser menulis "BTS"; versi lama mencari
    # "BTTS" sehingga bucket-nya permanen n=0. Samakan keduanya ke BTS.
    def _canon(m):
        return "BTS" if m in ("BTS", "BTTS") else m

    by_market = {}
    for mkt in ("1X2", "DC", "OU", "BTS", "Corners"):
        ml = [g for g in legs if _canon(g["market"]) == mkt]
        by_market[mkt] = _stats(ml)
    summary["by_market"] = by_market

    # by_band (hanya leg dengan p_model)
    by_band = {}
    bands_seen = sorted({_band(g["p_model"]) for g in legs if g["p_model"] is not None})
    for b in bands_seen:
        bl = [g for g in legs if _band(g["p_model"]) == b]
        by_band[b] = _stats(bl)
    summary["by_band"] = by_band

    # Brier pick_teraman (leg final non-push, wajib punya p_model —
    # tanpa guard ini leg tanpa probabilitas membuat TypeError dan
    # seluruh ringkasan gagal dibuat)
    pl = [g for g in legs if g["product"] == "pick_teraman"
          and g["status"] != "push" and g["p_model"] is not None]
    if pl:
        brier = sum((g["p_model"] - (1 if g["status"] == "hit" else 0)) ** 2
                    for g in pl) / len(pl)
        summary["brier_pick_teraman"] = round(brier, 4)
    else:
        summary["brier_pick_teraman"] = None

    # pending / ungratefulable
    reasons = defaultdict(int)
    for g in store.values():
        if g["status"] in ("pending", "ungradeable"):
            reasons[g["status"] + ":" + (g["reason"] or "")] += 1
    summary["pending"] = {"count": sum(1 for g in store.values()
                                       if g["status"] == "pending"),
                          "reasons": {k: v for k, v in reasons.items()
                                      if k.startswith("pending")}}
    summary["ungradeable"] = {
        "count": sum(1 for g in store.values() if g["status"] == "ungradeable"),
        "reasons": {k: v for k, v in reasons.items()
                    if k.startswith("ungradeable")}}
    summary["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return summary


def _is_date_name(name):
    """Nama folder arsip yang sah adalah tanggal ISO (audit ronde 13):
    folder non-tanggal di archive/ dulu bisa membuat fromisoformat di
    peringatan C12-3 melempar ValueError yang tertelan dan mematikan
    seluruh pemeriksaan secara diam-diam."""
    try:
        date.fromisoformat(name)
        return True
    except (TypeError, ValueError):
        return False


def _missing_archive_dates(dates, today):
    """Tanggal tanpa folder arsip di rentang [arsip pertama,
    min(arsip terakhir, kemarin)] — dasar peringatan C12-3. dates
    terurut menaik dan semuanya nama tanggal yang sah."""
    if not dates:
        return []
    first = date.fromisoformat(dates[0])
    last = min(date.fromisoformat(dates[-1]), today - timedelta(days=1))
    have = set(dates)
    missing = []
    d = first
    while d <= last:
        if d.isoformat() not in have:
            missing.append(d.isoformat())
        d += timedelta(days=1)
    return missing


# ---------------------------------------------------------------- main
def main(argv=None):
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    store = _load_grades()
    res_idx = _result_index()
    cor_idx = _corner_actuals_index()

    # proses semua tanggal arsip (dalam urutan naik); idempoten per kunci
    if not os.path.isdir(ARCHIVE):
        print("  ! tidak ada folder arsip")
        return 1
    dates = sorted(d for d in os.listdir(ARCHIVE)
                   if os.path.isdir(os.path.join(ARCHIVE, d))
                   and _is_date_name(d))
    # C12-3: tanggal yang hilang di tengah rentang arsip tidak boleh
    # lenyap diam-diam — folder yang tidak ada berarti rekomendasi
    # hari itu tidak akan pernah masuk riwayat kalibrasi (mis. arsip
    # gagal sementara prediksinya sukses). Peringatkan secara eksplisit.
    if dates:
        missing = _missing_archive_dates(
            dates, datetime.now(timezone.utc).date())
        if missing:
            last = min(dates[-1],
                       (datetime.now(timezone.utc).date()
                        - timedelta(days=1)).isoformat())
            print(f"  ! PERINGATAN: {len(missing)} tanggal tanpa "
                  f"folder arsip di rentang {dates[0]}.."
                  f"{last}: {', '.join(missing)}")
    total_changed = 0
    seen = set()
    for archive_date in dates:
        changed = _grade_archive(archive_date, store, res_idx, cor_idx,
                                 now, seen)
        total_changed += changed
    # Proses ulang store (audit ronde 15, C15-1): leg/unit pending
    # yang tidak dihasilkan arsip mana pun pada run ini dinilai
    # langsung dari indeks hasil SEBELUM pemangkasan yatim di bawah
    # sempat menghapusnya. Kerusakan arsip dengan demikian berhenti
    # menjadi kehilangan histori kalibrasi.
    regraded = _regrade_orphans(store, seen, res_idx, cor_idx, now)
    if regraded:
        print(f"[grade] yatim dinilai dari store: {regraded}")
        total_changed += regraded
    # Pangkas yatim: baris PENDING yang kuncinya tidak lagi dihasilkan
    # arsip mana pun menggantung sebagai pending abadi tanpa
    # pemangkasan ini. Sejak ronde 15, _regrade_orphans di atas sudah
    # menilai baris yatim yang laganya punya hasil — termasuk leg
    # yang seleksinya tergantikan di hari yang sama (kebijakan lama
    # memangkasnya sebagai "seleksi tergantikan"; kini histori
    # kalibrasi menampung semua seleksi yang sempat diterbitkan).
    # Yang tersisa untuk dipangkas di sini: baris yang hasilnya tak
    # bisa ditemukan (laga batal/pindah di luar jendela) dan baris
    # tua. Hanya pending berumur > 1 hari yang dipangkas; baris final
    # adalah riwayat kalibrasi dan tidak pernah dibuang.
    # Syarat tambahan (audit ronde 4): pemangkasan versi lama percaya
    # penuh pada kelengkapan arsip — laga yang DITUNDA yang arsipnya
    # hilang/tergenerasi ulang akan ikut terbuang padahal belum main.
    # Kini leg hanya dipangkas bila laganya SUDAH punya hasil (memang
    # yatim), dan semua baris punya jalan keluar usia 14 hari.
    cutoff = (datetime.now(timezone.utc).date()
              - timedelta(days=1)).isoformat()
    ancient = (datetime.now(timezone.utc).date()
               - timedelta(days=14)).isoformat()

    def _played(g):
        if g["level"] != "leg" or not g["home"]:
            return False
        try:
            return _match_result(res_idx, g["date"], g["home"],
                                 g["away"], g["competition"]) is not None
        except Exception:
            return False

    orphans = [k for k, g in store.items()
               if k not in seen and g["status"] == "pending"
               and g["date"] < cutoff
               and (g["date"] < ancient or _played(g))]
    for k in orphans:
        del store[k]
    if orphans:
        print(f"[grade] baris yatim dipangkas: {len(orphans)}")
    _save_grades(store)

    summary = _build_summary(store)
    os.makedirs(LEDGER, exist_ok=True)
    # Atomik: laporan pagi mem-parse file ini; salinan terpotong
    # merusak bacaan hari itu.
    tmp = SUMMARY + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    os.replace(tmp, SUMMARY)

    st = defaultdict(int)
    for g in store.values():
        st[g["status"]] += 1
    print(f"[grade] arsip={dates} baris_baru/diperbarui={total_changed}")
    print(f"[grade] total grades={len(store)} breakdown={dict(st)}")
    print(f"[grade] summary -> {SUMMARY}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
