# -*- coding: utf-8 -*-
"""score_ledger.py — grade picks pending dgn hasil aktual; append grades.jsonl.

- Hasil dibaca dari xg_raw/{SLUG}_2026_all.json (Understat, hasil + fixture),
  nama tim dipetakan balik FD->UG via map_full.json. Hasil yang belum
  ada di dump Understat diisi dari ta/results.csv (TipsterArea, FT)
  yang disinkronkan chain harian (audit GPT 2026-10-31, F).
- Settle memakai odds_open yang TERSIMPAN saat pick dibuat (jujur: harga yang
  memang bisa diambil ketika pick lahir) — bukan harga closing belakangan.
- CLV (closing line value): metrik kualitas headline. odds_close diisi dari
  all_matches_clean.csv kolom closing (hierarki Pinnacle -> AvgC -> B365C),
  dicocokkan pada (Div, Date, HomeTeam, AwayTeam) dgn normalize_name.
  Per-pick:
    clv_ev   = p_fair_close(taken selection) * odds_open - 1
    clv_price = odds_open / odds_close_taken - 1
  p_fair_close = de-vig Shin (_fair_probs) pada pasar closing penuh (3 harga
  1X2; dua sisi OU). Settle TETAP di odds_open.
- Append-only: pick_id yang sudah di-grade di-skip. Idempoten. Backfill pass
  mengisi odds_close/clv pada grade lama tanpa duplikasi atau sentuh ret_open.
"""
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

import paths
from ta_scrape import _cap_key as _capdt  # helper kanonis (lihat ta_scrape)
PROJ = paths.BASE
LEDGER = os.path.join(PROJ, "ledger")
PICKS = os.path.join(LEDGER, "picks.jsonl")
GRADES = os.path.join(LEDGER, "grades.jsonl")
SUMMARY = os.path.join(LEDGER, "ledger_summary.json")
SLUG = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
        "I1": "Serie_A", "F1": "Ligue_1"}

from football_etl import normalize_name
from backtest_picks import _fair_probs

# Varian nama klub yang berada di luar jangkauan lipatan normalize_name
# (audit ronde 12, C12-1): nama Understat ternormalisasi -> bentuk
# kanonis TipsterArea. Dipakai di KEDUA sisi kunci hasil TA (muat dan
# cari), jadi pasangan yang sama selalu bertemu. Daftar ini diturunkan
# dari join empiris hasil UG vs TA per (divisi, tanggal, skor) —
# 397 hasil UG <= 2026-10-27, nol ketidaksepakatan skor di kunci yang
# cocok — bukan tebakan: cologne/koln, Internazionale/Inter Milan,
# Stade Rennais/rennais dst. memang klub yang sama dengan ejaan
# berbeda di dua sumber.
_TA_ALIAS = {
    "cologne": "koln",
    "rasenballsport leipzig": "rb leipzig",
    "nottingham forest": "nottingham",
    "internazionale": "inter milan",
    "alaves": "deportivo alaves",
    "athletic": "athletic bilbao",
    "olympique lyonnais": "lyonnais",
    "stade rennais": "rennais",
    "hamburger sv": "hamburger",
    "vfb stuttgart": "stuttgart",
}


def _ta_key_name(name):
    """Nama kunci untuk pencocokan hasil TipsterArea (normalize + alias)."""
    n = normalize_name(name)
    return _TA_ALIAS.get(n, n)


def _by_teams_index(keyed):
    """{(scope, date, home, away): skor} -> {(scope, home, away):
    [(date, skor), ...] terurut tanggal menaik}.

    Untuk fallback laga tunda (C12-4): lookup utama berjangkar
    tanggal pick, jadi laga yang digeser tidak akan pernah ketemu
    hasilnya. Fallback mencari tanggal main paling awal SETELAH
    tanggal pick untuk pasangan tim yang sama (hasil tidak mungkin
    mendahului pick-nya, dan pasangan yang sama bertemu lagi di
    putaran kedua sehingga yang paling awal yang benar).
    """
    idx = {}
    for (scope, d, h, a), sc in keyed.items():
        idx.setdefault((scope, h, a), []).append((d, sc))
    for v in idx.values():
        v.sort()
    return idx


def _postponed_lookup(entries, pick_date, max_days=45):
    """Skor laga tunda dari indeks _by_teams_index: tanggal main
    paling awal SETELAH tanggal pick, dibatasi max_days hari
    (audit ronde 13). Tanpa batas, pick dari laga yang DIBATALKAN
    (tidak pernah dimainkan) bisa dinilai dari pertemuan putaran
    kedua berbulan-bulan kemudian; 45 hari menampung penjadwalan
    ulang yang realistis. entries terurut tanggal menaik.
    Return skor atau None."""
    try:
        limit = (date.fromisoformat(pick_date)
                 + timedelta(days=max_days)).isoformat()
    except (TypeError, ValueError):
        limit = None
    for d, sc in entries or []:
        if d <= pick_date:
            continue
        if limit is not None and d > limit:
            break
        return sc
    return None

def _load_fd2ug():
    """Peta nama FD -> nama Understat per divisi (dari xg_raw/map_*)."""
    NMAP = {}
    for _fn in ("map_full.json", "map_ext.json"):
        _p = os.path.join(PROJ, "xg_raw", _fn)
        if os.path.exists(_p):
            with open(_p, encoding="utf-8") as f:
                NMAP.update(json.load(f))
    fd2ug = {}
    for k, v in NMAP.items():
        div, ug = k.split("|", 1)
        fd2ug.setdefault(div, {})[normalize_name(v)] = ug
    return fd2ug


# hasil: {(div, date, home_ug, away_ug) -> (yh, ya)}
def _load_results(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for d in data:
        if not d.get("isResult") or d.get("goals", {}).get("h") is None:
            continue
        date = d["datetime"][:10]
        out[(date, d["h"]["title"], d["a"]["title"])] = \
            (int(d["goals"]["h"]), int(d["goals"]["a"]))
    return out


def _load_all_results():
    """Hasil liga dari dump Understat (all + fixtures, fixtures menang)."""
    results = {}
    for div, slug in SLUG.items():
        stem = os.path.join(PROJ, "xg_raw", f"{slug}_2026")
        merged = _load_results(stem + "_all.json")
        # _fixtures.json di-refresh harian dan lebih segar (sampai 10-25);
        # bila kunci sama, hasil fixtures menang.
        merged.update(_load_results(stem + "_fixtures.json"))
        for (date, h, a), g in merged.items():
            results[(div, date, h, a)] = g
    return results


# hasil liga dari ta/results.csv (FT): {(div, date, home_norm, away_norm)}
# Chain harian menyinkronkan file ini, tapi grading liga dulu hanya
# membaca dump Understat yang bisa tertinggal beberapa hari — pick
# tertahan pending padahal skor finalnya sudah ada (audit GPT
# 2026-10-31, F). TA hanya MENGISI kunci yang belum ada di sumber
# Understat (Understat menang bila keduanya ada), dengan pencocokan
# (divisi, tanggal, nama ternormalisasi) yang sama seperti jalur piala.
TA_LEAGUE = {"England - Premier League": "E0",
             "Spain - Primera Division": "SP1",
             "Germany - Bundesliga": "D1",
             "Italy - Serie A": "I1",
             "France - Ligue 1": "F1"}


def _load_ta_league_results():
    """Hasil liga FT dari ta/results.csv."""
    out = {}
    _res_path = os.path.join(PROJ, "ta", "results.csv")
    if os.path.exists(_res_path):
        with open(_res_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if (r.get("status") or "").upper() != "FT":
                    continue
                div = TA_LEAGUE.get(r.get("league", ""))
                if not div:
                    continue
                sh, sa = r.get("score_h"), r.get("score_a")
                if sh in (None, "") or sa in (None, ""):
                    continue
                out[(div, r["date"][:10],
                     _ta_key_name(r["home"]), _ta_key_name(r["away"]))] = \
                    (int(sh), int(sa))
    return out


# hasil piala dari ta/results.csv (FT): {(competition, date, home_norm, away_norm)}
CUP_COMP = {"England - EFL Cup": "EFL Cup", "Germany - Cup Germany": "DFB Pokal"}
def _load_cup_results():
    """Hasil piala FT dari ta/results.csv."""
    cup_results = {}
    _res_path = os.path.join(PROJ, "ta", "results.csv")
    if os.path.exists(_res_path):
        with open(_res_path, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if (r.get("status") or "").upper() != "FT":
                    continue
                comp = CUP_COMP.get(r.get("league", ""))
                if not comp:
                    continue
                sh, sa = r.get("score_h"), r.get("score_a")
                if sh is None or sa is None:
                    continue
                cup_results[(comp, r["date"][:10],
                             _ta_key_name(r["home"]), _ta_key_name(r["away"]))] = \
                    (int(sh), int(sa))
    return cup_results


# ---------- closing odds (CLV source) ----------
# Hierarki per pasar: Pinnacle close -> AvgC -> B365C (dari all_matches_clean.csv).
# Pinnacle memakai PPC* di baris musim 2627 dan PSC* di musim lama —
# kedua ejaan masuk rantai (audit ronde 3: tanpa PPC*, CLV musim ini
# diam-diam selalu bersumber AvgC).
CLOSE_1X2 = (("PPCH", "PPCD", "PPCA"),
              ("PSCH", "PSCD", "PSCA"),
              ("AvgCH", "AvgCD", "AvgCA"),
              ("B365CH", "B365CD", "B365CA"))
CLOSE_OU = (("PC>2.5", "PC<2.5"),
            ("AvgC>2.5", "AvgC<2.5"),
            ("B365C>2.5", "B365C<2.5"))


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None





def _load_close_map():
    """{(div, date_iso, home_norm, away_norm) -> (o_1x2, o_ou)}."""
    m = {}
    p = paths.DATA_CLEAN
    if not os.path.exists(p):
        return m
    with open(p, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            div, dt = r.get("Div"), r.get("Date")
            if not div or not dt:
                continue
            h = normalize_name(r.get("HomeTeam") or "")
            a = normalize_name(r.get("AwayTeam") or "")
            if not h or not a:
                continue
            key = (div, dt[:10], h, a)
            o = None
            for ch, cd, ca in CLOSE_1X2:
                vh, vd, va = _num(r.get(ch)), _num(r.get(cd)), _num(r.get(ca))
                if vh and vd and va:
                    o = (vh, vd, va)
                    break
            ou = None
            for co, cu in CLOSE_OU:
                vo, vu = _num(r.get(co)), _num(r.get(cu))
                if vo and vu:
                    ou = (vo, vu)
                    break
            if o is not None or ou is not None:
                m[key] = (o, ou)
    return m


CLOSE_MAP = {}  # diisi main() — impor modul tidak boleh membaca data

# snack piala: snapshot terakhir sebelum kickoff per (home,away,date).
# Prematch dijamin DUA lapis: status NS DAN captured_at < kickoff
# (fixtures.csv, waktu UTC) bila kickoff dikenal — status NS saja
# tidak membuktikan snapshot diambil sebelum laga mulai.
def _load_cup_snapshots():
    kickoff = {}
    fp = os.path.join(PROJ, "ta", "fixtures.csv")
    if os.path.exists(fp):
        with open(fp, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                gid = (r.get("game_id") or "").strip()
                d = (r.get("date") or "")[:10]
                t = (r.get("time") or "")[:5]
                if gid and d and t:
                    ko = _capdt(f"{d}T{t}:00+0000")
                    if ko.year > 2000:  # parse gagal -> datetime.min
                        kickoff[gid] = ko
    best = {}
    p = os.path.join(PROJ, "ta", "odds_1x2_snapshots.csv")
    if not os.path.exists(p):
        return best
    with open(p, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if (r.get("status") or "") != "NS":
                continue
            dt = (r.get("date") or "").strip()
            h = normalize_name(r.get("home") or "")
            a = normalize_name(r.get("away") or "")
            o1, ox, o2 = _num(r.get("o1")), _num(r.get("ox")), _num(r.get("o2"))
            if not dt or not h or not a or not (o1 and ox and o2):
                continue
            cap = r.get("captured_at") or ""
            ko = kickoff.get((r.get("game_id") or "").strip())
            if ko is not None and _capdt(cap) >= ko:
                continue  # tertangkap sesudah kickoff: bukan prematch
            key = (h, a, dt[:10])
            cur = best.get(key)
            if cur is None or _capdt(cap) > _capdt(cur[0]):
                best[key] = (cap, o1, ox, o2)
    return best


CUP_SNAPS = {}  # diisi main() — impor modul tidak boleh membaca data


def _cup_close_proxy(pk):
    key = (normalize_name(pk.get("home") or ""),
           normalize_name(pk.get("away") or ""),
           (pk.get("date") or "")[:10])
    row = CUP_SNAPS.get(key)
    return (row[1], row[2], row[3]) if row else None


def _clv(pk, o, ou):
    """Kembalikan (clv_ev, clv_price, odds_close_taken). None bila tidak lengkap."""
    odds_open = _num(pk.get("odds_open"))
    if not odds_open or odds_open <= 1.0:
        return None, None, None
    market, side = pk.get("market"), pk.get("side")
    if market == "1X2":
        if o is None:
            return None, None, None
        idx = {"H": 0, "D": 1, "A": 2}.get(side)
        if idx is None:
            return None, None, None
        fair = _fair_probs(o, "shin")
        pf, c_taken = fair[idx], o[idx]
    elif market == "OU":
        if ou is None:
            return None, None, None
        # Pasangan closing `ou` selalu garis 2.5 (satu-satunya yang
        # disediakan football-data). Pick bergaris lain tidak boleh
        # dinilai CLV-nya terhadap garis 2.5 — kembalikan None.
        try:
            plf = float(pk.get("line")) if pk.get("line") not in (None, "") \
                else 2.5
        except (TypeError, ValueError):
            plf = 2.5
        if plf != 2.5:
            return None, None, None
        fair = _fair_probs(ou, "shin")
        if side == "Over":
            pf, c_taken = fair[0], ou[0]
        elif side == "Under":
            pf, c_taken = fair[1], ou[1]
        else:
            return None, None, None
    else:
        return None, None, None
    clv_ev = round(pf * odds_open - 1.0, 5)
    clv_price = round(odds_open / c_taken - 1.0, 5) if c_taken > 0 else None
    return clv_ev, clv_price, c_taken


def _grade_close_payload(pk):
    """isi (odds_close_1x2, odds_close_o25, clv_ev, clv_price)."""
    comp = pk.get("competition") or ""
    if comp in ("EFL Cup", "DFB Pokal"):
        o, ou = _cup_close_proxy(pk), None
    else:
        key = (pk.get("div"), pk.get("date"), pk.get("home"), pk.get("away"))
        o, ou = CLOSE_MAP.get(key, (None, None))
    clv_ev, clv_price, c_taken = _clv(pk, o, ou)
    o1x2 = [None, None, None]
    if o is not None:
        o1x2 = [round(v, 4) if v is not None else None for v in o]
    o25 = round(c_taken, 4) if (pk.get("market") == "OU" and c_taken) else None
    return o1x2, o25, clv_ev, clv_price


def settle(market, side, yh, ya, odds, line=None):
    """Return (ret, won, push); ret = gross return as a multiple of stake.

    OU is settled against the pick's own `line` when it carries one
    (cup picks store theirs, e.g. 1.5); without a line the historical
    default 2.5 applies (every league OU pick is 2.5). A total exactly
    on an integer line is a push (ret 1.0). Before this fix every OU
    pick was settled against a hardcoded 2.5 (audit K3).
    """
    if market == "1X2":
        if side not in ("H", "D", "A"):
            # Side kosakata asing (mis. "1"/"X"/"2" yang belum
            # diterjemahkan) harus gagal keras, bukan kalah diam-diam.
            raise ValueError(f"settle 1X2: side tak dikenal {side!r}")
        wk = "H" if yh > ya else ("A" if ya > yh else "D")
        return (odds if side == wk else 0.0), (side == wk), False
    if market != "OU":
        # Guard: versi lama memperlakukan SEMUA pasar non-1X2 sebagai
        # OU (side selain "Over" dinilai sebagai Under). Pick DC/BTS di
        # masa depan harus gagal keras di sini, bukan ter-grade salah.
        raise ValueError(f"settle: pasar tak dikenal {market!r}")
    if side not in ("Over", "Under"):
        raise ValueError(f"settle OU: side tak dikenal {side!r}")
    try:
        ln = float(line) if line not in (None, "") else 2.5
    except (TypeError, ValueError):
        ln = 2.5
    tot = yh + ya
    q = ln * 4
    if abs(q - round(q)) < 1e-9 and int(round(q)) % 2 == 1:
        # Garis seperempat (2.25/2.75): stake terbelah ke dua garis
        # tetangga; return = rata-rata keduanya (audit ronde 3 —
        # versi lama menilainya sebagai garis utuh).
        ret = (_ou_once(tot, side, ln - 0.25, odds)
               + _ou_once(tot, side, ln + 0.25, odds)) / 2.0
        return ret, ret > 1.0, ret == 1.0
    ret = _ou_once(tot, side, ln, odds)
    return ret, ret > 1.0, ret == 1.0


def _ou_once(tot, side, ln, odds):
    """Return satu garis OU utuh/setengah: odds menang, 1.0 push, 0 kalah."""
    if tot == ln:
        return 1.0
    over = tot > ln
    won = over if side == "Over" else not over
    return odds if won else 0.0


def _settle_guarded(pk, yh, ya, skipped):
    """settle() dengan kesalahan per-pick ditelan: ValueError pasar/side
    asing dan KeyError pick cacat (field hilang) sama-sama melewatkan
    pick itu (tetap pending) dan mencatatnya ke daftar `skipped`,
    BUKAN menggagalkan seluruh run grading harian."""
    try:
        return settle(pk["market"], pk["side"], yh, ya,
                      pk["odds_open"], pk.get("line"))
    except (ValueError, KeyError):
        skipped.append(
            (pk["pick_id"], pk.get("market"), pk.get("side")))
        return None


def _result_label(ret, odds, push):
    """Label hasil dari ret. Garis seperempat menghasilkan ret pecahan
    di antara nilai utuh (half_win/half_loss); label polos win/loss
    akan menyesatkan konsumen yang menghitung dari `result` saja."""
    if push:
        return "push"
    if ret >= odds:
        return "win"
    if ret <= 0.0:
        return "loss"
    return "half_win" if ret > 1.0 else "half_loss"


def _backfill(grades, picks_by_id, recompute_clv):
    out = []
    for g in grades:
        new = dict(g)
        pk = picks_by_id.get(g["pick_id"])
        if pk is not None:
            o1x2, o25, clv_ev, clv_price = _grade_close_payload(pk)
            if recompute_clv:
                # Restatement paksa: timpa field close/CLV dari hierarki
                # sumber saat ini. ret_open/result/yh/ya tidak disentuh —
                # settlement adalah fakta historis, CLV adalah penilaian.
                new["odds_close_1x2"] = o1x2
                new["odds_close_o25"] = o25
                new["clv_ev"] = clv_ev
                new["clv_price"] = clv_price
            else:
                # hanya timpa saat nilai sekarang null (idempoten)
                cur1 = new.get("odds_close_1x2")
                if not cur1 or all(v is None for v in cur1):
                    new["odds_close_1x2"] = o1x2
                if new.get("odds_close_o25") is None:
                    new["odds_close_o25"] = o25
                if new.get("clv_ev") is None:
                    new["clv_ev"] = clv_ev
                if new.get("clv_price") is None:
                    new["clv_price"] = clv_price
        out.append(new)
    return out


def main():
    """Jalankan grading satu kali (kontrak subprocess: kode keluar +
    stdout + file ledger). Semua pemuatan data dan penulisan file
    tinggal di sini — mengimpor modul ini tidak mengeksekusi apa pun,
    sehingga settle/_clv bisa diuji sebagai fungsi murni."""
    recompute_clv = "--recompute-clv" in sys.argv
    global CLOSE_MAP, CUP_SNAPS
    CLOSE_MAP = _load_close_map()
    CUP_SNAPS = _load_cup_snapshots()
    fd2ug = _load_fd2ug()
    results = _load_all_results()
    ta_results = _load_ta_league_results()
    cup_results = _load_cup_results()

    # Indeks per pasangan tim untuk fallback laga tunda (C12-4).
    ug_by_teams = _by_teams_index(results)
    ta_by_teams = _by_teams_index(ta_results)
    cup_by_teams = _by_teams_index(cup_results)

    if not os.path.exists(PICKS):
        raise SystemExit("picks.jsonl belum ada")
    with open(PICKS, encoding="utf-8") as f:
        picks = [json.loads(l) for l in f if l.strip()]
    picks_by_id = {p["pick_id"]: p for p in picks}
    graded_ids = set()
    if os.path.exists(GRADES):
        with open(GRADES, encoding="utf-8") as f:
            for l in f:
                if l.strip():
                    graded_ids.add(json.loads(l)["pick_id"])

    new_grades = []
    unmapped = defaultdict(set)
    skipped_unknown = []
    n_ta_filled = 0

    for pk in picks:
        if pk["pick_id"] in graded_ids:
            continue
        comp = pk.get("competition") or ""
        o1x2, o25, clv_ev, clv_price = _grade_close_payload(pk)
        if comp in ("EFL Cup", "DFB Pokal"):
            # pick piala: hasil dari ta/results.csv (samakan nama)
            res = cup_results.get((comp, pk["date"],
                                   _ta_key_name(pk["home"]), _ta_key_name(pk["away"])))
            if res is None:
                # Laga tunda (C12-4): hasil ada di tanggal main yang
                # baru, bukan tanggal pick — cari pasangan tim yang
                # sama di tanggal paling awal setelah tanggal pick,
                # dibatasi 45 hari (ronde 13).
                res = _postponed_lookup(
                    cup_by_teams.get((comp, _ta_key_name(pk["home"]),
                                      _ta_key_name(pk["away"])), []),
                    pk["date"])
            if res is None:
                unmapped[comp].add(f"{pk['home']} v {pk['away']}")
                continue
            yh, ya = res
            sres = _settle_guarded(pk, yh, ya, skipped_unknown)
            if sres is None:
                continue
            ret, won, push = sres
            new_grades.append({
                "pick_id": pk["pick_id"], "competition": comp,
                "graded_ts": datetime.now(timezone.utc).isoformat(),
                "result": _result_label(ret, pk["odds_open"], push),
                "yh": yh, "ya": ya,
                "ret_open": round(ret, 4),
                "odds_close_1x2": o1x2, "odds_close_o25": o25,
                "clv_ev": clv_ev, "clv_price": clv_price,
            })
            continue
        home_ug = fd2ug.get(pk["div"], {}).get(pk["home"])
        away_ug = fd2ug.get(pk["div"], {}).get(pk["away"])
        if not home_ug:
            unmapped[pk["div"]].add(f"home={pk['home']}")
        if not away_ug:
            unmapped[pk["div"]].add(f"away={pk['away']}")
        res = results.get((pk["div"], pk["date"], home_ug, away_ug)) if home_ug and away_ug else None
        if res is None and home_ug and away_ug:
            # Fallback TipsterArea (audit GPT F): dump Understat belum
            # memuat hasil ini, tapi chain harian sudah menyinkronkan
            # skor finalnya ke ta/results.csv.
            res = ta_results.get((pk["div"], pk["date"],
                                  _ta_key_name(home_ug),
                                  _ta_key_name(away_ug)))
            if res is not None:
                n_ta_filled += 1
        if res is None and home_ug and away_ug:
            # Laga tunda (C12-4): coba tanggal main baru, Understat
            # dulu lalu TipsterArea, paling awal setelah tanggal pick,
            # dibatasi 45 hari (ronde 13).
            res = _postponed_lookup(
                ug_by_teams.get((pk["div"], home_ug, away_ug), []),
                pk["date"])
            if res is None:
                res = _postponed_lookup(
                    ta_by_teams.get((pk["div"], _ta_key_name(home_ug),
                                     _ta_key_name(away_ug)), []),
                    pk["date"])
                if res is not None:
                    n_ta_filled += 1
        if res is None:
            continue  # belum main / belum keluar hasilnya
        yh, ya = res
        sres = _settle_guarded(pk, yh, ya, skipped_unknown)
        if sres is None:
            continue
        ret, won, push = sres
        new_grades.append({
            "pick_id": pk["pick_id"], "competition": "",
            "graded_ts": datetime.now(timezone.utc).isoformat(),
            "result": _result_label(ret, pk["odds_open"], push),
            "yh": yh, "ya": ya,
            "ret_open": round(ret, 4),
            "odds_close_1x2": o1x2, "odds_close_o25": o25,
            "clv_ev": clv_ev, "clv_price": clv_price,
        })

    if n_ta_filled:
        print(f"hasil liga dari TipsterArea dipakai untuk {n_ta_filled} "
              f"pick (dump Understat belum memuatnya)")

    if skipped_unknown:
        print(f"! {len(skipped_unknown)} pick dilewati (pasar/side tak dikenal): "
              f"{skipped_unknown}")

    if new_grades:
        with open(GRADES, "a", encoding="utf-8") as f:
            for g in new_grades:
                f.write(json.dumps(g, ensure_ascii=False) + "\n")

    # ---------- backfill idempoten: isi odds_close/clv pada grade lama ----------

    # ------- ringkasan
    gmap = {}
    if os.path.exists(GRADES):
        with open(GRADES, encoding="utf-8") as f:
            all_grades = [json.loads(l) for l in f if l.strip()]
        all_grades = _backfill(all_grades, picks_by_id, recompute_clv)
        # Tulis atomik (tmp + replace): penulisan ulang penuh ini sekarang
        # berjalan setiap hari (langkah [15/16] rantai harian); penulisan
        # langsung yang terpotong di tengah akan merusak riwayat grading.
        _tmp = GRADES + ".tmp"
        with open(_tmp, "w", encoding="utf-8") as f:
            for g in all_grades:
                f.write(json.dumps(g, ensure_ascii=False) + "\n")
        os.replace(_tmp, GRADES)
        gmap = {g["pick_id"]: g for g in all_grades}
    else:
        all_grades = []

    agg = defaultdict(lambda: dict(n=0, prof=0.0, n_clv=0, s_ev=0.0,
                                   s_pr=0.0, beat=0))
    headline = dict(n=0, n_clv=0, s_ev=0.0, s_pr=0.0, beat=0)
    for pk in picks:
        g = gmap.get(pk["pick_id"])
        if not g:
            continue
        comp = pk.get("competition") or g.get("competition") or "league"
        a = agg[(comp, pk["market"])]
        a["n"] += 1
        a["prof"] += g["ret_open"] - 1.0
        headline["n"] += 1
        ev, pr = g.get("clv_ev"), g.get("clv_price")
        if ev is not None:
            a["n_clv"] += 1
            a["s_ev"] += ev
            headline["n_clv"] += 1
            headline["s_ev"] += ev
        if pr is not None:
            a["s_pr"] += pr
            headline["s_pr"] += pr
            if pr > 0:
                a["beat"] += 1
                headline["beat"] += 1


    def clv_block(a):
        n_clv = a["n_clv"]
        return {
            "n_clv": n_clv,
            "clv_coverage": round(n_clv / a["n"], 4) if a["n"] else None,
            "mean_clv_ev": round(a["s_ev"] / n_clv, 5) if n_clv else None,
            "mean_clv_price": round(a["s_pr"] / n_clv, 5) if n_clv else None,
            "beat_close_rate": round(a["beat"] / n_clv, 4) if n_clv else None,
        }


    competitions = {}
    for (comp, market), a in agg.items():
        block = competitions.setdefault(comp, {})
        block[market] = {"n": a["n"], "profit": round(a["prof"], 2),
                         "roi": round(a["prof"] / a["n"], 4) if a["n"] else None,
                         **clv_block(a)}

    comp_summary = {}
    for comp in ("league", "EFL Cup", "DFB Pokal"):
        block = competitions.get(comp, {})
        n = sum(b["n"] for b in block.values())
        prof = sum(b["profit"] for b in block.values())
        agg_c = dict(n=n, prof=prof, n_clv=sum(b["n_clv"] for b in block.values()),
                     s_ev=sum(b["mean_clv_ev"] * b["n_clv"] for b in block.values() if b["mean_clv_ev"] is not None),
                     s_pr=sum(b["mean_clv_price"] * b["n_clv"] for b in block.values() if b["mean_clv_price"] is not None),
                     beat=sum(b["beat_close_rate"] * b["n_clv"] for b in block.values() if b["beat_close_rate"] is not None))
        comp_summary[comp] = {
            "n": n,
            "profit": round(prof, 2),
            "roi": round(prof / n, 4) if n else None,
            "markets": block,
            **clv_block(agg_c),
        }
    summary = {
        "graded_ts": datetime.now(timezone.utc).isoformat(),
        "n_picks": len(picks),
        "n_graded": sum(1 for p in picks if p["pick_id"] in gmap),
        "n_pending": sum(1 for p in picks if p["pick_id"] not in gmap),
        "headline_clv": clv_block(headline),
        "competitions": comp_summary,
        "note": "Settle di odds_open saat pick lahir (flat 1 unit). odds_close & CLV "
                "diisi dari all_matches_clean.csv kolom closing (hierarki Pinnacle -> "
                "AvgC -> B365C); clv_ev = p_fair_close(taken) * odds_open - 1, "
                "clv_price = odds_open / odds_close_taken - 1. CLV adalah metrik "
                "kualitas; settle tetap di odds_open. Ringkasan per kompetisi: liga "
                "gabungan (kunci 'league') + tiap piala.",
    }
    with open(SUMMARY, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"graded baru: {len(new_grades)} | total graded: {len(all_grades)} | pending: {summary['n_pending']}")
    if recompute_clv:
        print(f"  CLV dihitung ulang paksa untuk {len(all_grades)} grade "
              f"(hierarki sumber saat ini; ret_open/result tidak berubah)")
    if unmapped:
        print("!! tidak terpetakan:")
        for comp, names in sorted(unmapped.items()):
            print(f"   {comp}: {sorted(names)}")
    for comp, c in summary["competitions"].items():
        print(f"  [{comp}] n={c['n']} profit={c['profit']}")
        for m, a in c["markets"].items():
            roi = a["roi"]
            print(f"     {m}: n={a['n']} ROI={roi*100 if roi is not None else 0:.2f}% "
                  f"| CLV EV={a['mean_clv_ev']} PRICE={a['mean_clv_price']} "
                  f"beat={a['beat_close_rate']} cov={a['clv_coverage']}")
    print(f"  headline CLV: EV={summary['headline_clv']['mean_clv_ev']} "
          f"PRICE={summary['headline_clv']['mean_clv_price']} "
          f"beat={summary['headline_clv']['beat_close_rate']} "
          f"n={summary['headline_clv']['n_clv']} "
          f"cov={summary['headline_clv']['clv_coverage']}")
    for g in new_grades[:5]:
        print("  *", g["pick_id"], g.get("competition", ""), g["result"], "ret=", g["ret_open"])


if __name__ == "__main__":
    main()
