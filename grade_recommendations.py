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


def _match_result(idx, match_date, home, away, comp):
    """Cari skor FT untuk (tanggal, home, away).

    Skor = kemiripan nama (sim) kedua tim; hint kompetisi piala memberi
    dorongan kecil untuk memisahkan laga liga vs piala di tanggal sama.
    None bila tidak ada kandidat meyakinkan.
    """
    cands = idx.get(match_date)
    if not cands:
        return None
    nh, na = norm(home), norm(away)
    hint = CUP_LEAGUE.get(comp or "")
    best, bs = None, 0.0
    for rh, ra, sh, sa, lge in cands:
        sc = sim(nh, rh) * sim(na, ra)
        if hint and lge == hint:
            sc += 0.05
        if sc > bs:
            bs, best = sc, (sh, sa)
    return best if bs >= 0.75 else None


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
         "status": "pending", "score": "", "reason": "", "graded_at": ""}

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
    sh, sa = res
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
    dates = sorted(d for d in os.listdir(ARCHIVE) if os.path.isdir(os.path.join(ARCHIVE, d)))
    total_changed = 0
    seen = set()
    for archive_date in dates:
        changed = _grade_archive(archive_date, store, res_idx, cor_idx,
                                 now, seen)
        total_changed += changed
    # Pangkas yatim: baris PENDING yang kuncinya tidak lagi dihasilkan
    # arsip mana pun (seleksi rekomendasi tergantikan sebelum sempat
    # ter-grade) menggantung sebagai pending abadi tanpa pemangkasan
    # ini. Hanya pending berumur > 1 hari yang dipangkas; baris final
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
