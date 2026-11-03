# -*- coding: utf-8 -*-
"""fotmob_fixtures.py — pengganti input Understat via FotMob.

Latar: understat.com down sejak 31 Okt (403 challenge) dan belum pulih.
FotMob terbuka dari mesin ini dan punya xG per tembakan (Opta). Kontrak
output: list laga dgn schema identik dump Understat (id / isResult /
h / a / goals / xG / datetime UTC), sehingga semua konsumen
(football_etl.load_fixtures, score_ledger, build_xg_matches,
model_corners_v3, pipeline_orchestrator._refresh_understat_seasons)
bekerja tanpa perubahan.

Endpoint:
1. GET /api/data/leagues?id={lid}&ccode3={cc}
   -> fixtures.allMatches: seluruh laga musim berjalan (hasil + jadwal).
2. GET /api/data/matchDetails?matchId={mid} — HANYA utk laga selesai
   yang belum punya xG (cache xg_raw/fotmob_xg.json) ->
   content.shotmap.shots (xG per tembakan, teamId) disum per tim.

Catatan konsistensi: xG lama (Understat) dan baru (FotMob/Opta) berasal
dari model berbeda — biaya densitas kecil vs data beku diterima; hasil
`build_xg_matches` membaca keduanya secara campur. Modul ini TIDAK
menyentuh model/config/hasil; hanya menulis file input (pola
refresh_fixtures). Pemetaan nama fotmob->understat dipersist di
xg_raw/fotmob_names.json (mis. 'Coventry City' -> 'Coventry').
"""
from __future__ import annotations

import difflib
import glob
import json
import os
import shutil
import sys
import time
import unicodedata
from datetime import datetime

PROJ = os.path.dirname(os.path.abspath(__file__))
if PROJ not in sys.path:
    sys.path.insert(0, PROJ)
XG = os.path.join(PROJ, "xg_raw")

NMAP_CACHE = os.path.join(XG, "fotmob_names.json")
XG_CACHE = os.path.join(XG, "fotmob_xg.json")
API = "https://www.fotmob.com/api/data"

# id liga internal FotMob (diverifikasi via api/data/matches, 3 Nov 2026).
LEAGUES = {
    "EPL": (47, "ENG", "E0"),
    "La_liga": (87, "ESP", "SP1"),
    "Bundesliga": (54, "GER", "D1"),
    "Serie_A": (55, "ITA", "I1"),
    "Ligue_1": (53, "FRA", "F1"),
}

# Max laga di-enrich xG per fetch() per liga; backfill=True mematikan
# batas (dipakai sekali saat migrasi). Run harian biasanya butuh <20.
XG_MAX_ENRICH_PER_RUN = 60

LAST_SOURCES = {}
_client = None


def _hdr():
    from stealth import headers
    return headers({"Accept": "application/json"},
                   referer="https://www.fotmob.com/")


def _get(url, params=None, tries=3, timeout=45):
    """GET JSON dengan retry sadar-status + jitter (pola stealth)."""
    import httpx

    global _client

    last = None
    for i in range(tries):
        if i:
            time.sleep(min(2 * 2 ** i, 20))
        try:
            if _client is None:
                _client = httpx.Client(timeout=timeout)
            r = _client.get(url, params=params, headers=_hdr(),
                            follow_redirects=True)
            if r.status_code == 200:
                return r.json()
            if r.status_code in (429, 500, 502, 503, 504):
                last = httpx.HTTPStatusError(
                    f"{r.status_code}", request=r.request, response=r)
                continue
            raise httpx.HTTPStatusError(
                f"{r.status_code}", request=r.request, response=r)
        except httpx.HTTPStatusError:
            raise
        except Exception as e:  # noqa: BLE001
            last = e
    raise last or RuntimeError(f"GET gagal: {url}")


def _clean(name):
    """Normalisasi nama tim: ascii-lower, pisaub token."""
    s = unicodedata.normalize("NFKD", name or "").encode("ascii", "ignore")
    s = s.decode("ascii").lower()
    s = "".join(" " if not ch.isalnum() else ch for ch in s)
    return " ".join(s.split())


def _token_match(cf, cu):
    """Nama cocok bila string sama ATAU salah sat set token superset dari
    yang lain dengan irisan tak kosong ('coventry' ⊂ 'coventry city',
    'west ham' ⊂ 'west ham united'). Kembaran dgn prefiks sama ('sheffield
    united' vs 'sheffield wednesday') tidak lolos: tak ada superset."""
    if not cf or not cu:
        return False
    if cf == cu:
        return True
    tf, tu = set(cf.split()), set(cu.split())
    if not (tf & tu):
        return False
    return tf <= tu or tu <= tf


# Alias satu klub yang tidak saling token-match per masalah antar-musim
# data frozen (Understat 2025/26 memakai 'FC Cologne' & 'RasenBallsport
# Leipzig', FotMob '1. FC Köln' & 'RB Leipzig').
ALIAS_GROUPS = {
    "fc koln": {"fc cologne", "1 fc koln", "fc koln", "koln", "cologne"},
    "rb leipzig": {"rb leipzig", "rasenballsport leipzig"},
}


def _club_key(title_clean):
    """Kunci klub kanonik: anggota/keys ALIAS_GROUPS dinormalkan."""
    for key, grp in ALIAS_GROUPS.items():
        if title_clean == key or title_clean in grp:
            return key
    return title_clean


def _name_match(cf, cu):
    """Token match ATAU alias satu grup kanonik."""
    return _token_match(cf, cu) or _club_key(cf) == _club_key(cu)


def _ustat_titles(slug, yr4=None):
    """Semua nama tim Understat yang pernah tercatat utk liga ini.

    Bila yr4 diberikan: hanya dari dump musim {slug}_{yr4}.json —
    alias antar-musim ('FC Cologne' vs '1. FC Köln') TIDAK boleh
    campur, karena pemetaan harian hanya mencocokkan payung musim
    berjalan. Bila file musim itu kosong, fallback ke semua musim."""
    titles = set()
    if yr4:
        p = os.path.join(XG, f"{slug}_{yr4}.json")
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
            for d in data:
                for side in ("h", "a"):
                    t = (d.get(side) or {}).get("title")
                    if t:
                        titles.add(t)
            if titles:
                return titles
        except Exception:  # noqa: BLE001
            pass
    for p in glob.glob(os.path.join(XG, f"{slug}_20[0-9][0-9].json")):
        try:
            with open(p, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:  # noqa: BLE001
            continue
        for d in data:
            for side in ("h", "a"):
                t = (d.get(side) or {}).get("title")
                if t:
                    titles.add(t)
    return titles


def _load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return default if default is not None else {}


def _save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)


def _shot_xg(md):
    """(xgh_str, xga_str) dari matchDetails (shotmap + teamId), None
    bila struktur tidak tersedia / tak ada tembakan ber-xG."""
    try:
        shots = md["content"]["shotmap"]["shots"]
        ht = md["header"]["teams"][0]["id"]
        at = md["header"]["teams"][1]["id"]
    except (KeyError, TypeError, IndexError):
        return None
    xgh = xga = 0.0
    seen = False
    for s in shots:
        if s.get("isOwnGoal"):
            continue
        x = s.get("expectedGoals")
        if x is None:
            continue
        seen = True
        if s.get("teamId") == ht:
            xgh += float(x)
        elif s.get("teamId") == at:
            xga += float(x)
    if not seen:
        return None
    return (f"{xgh:.6f}", f"{xga:.6f}")


def _fetch_xg(mid, xg_cache):
    """(xgh, xga) dari cache dulu, lalu GET matchDetails."""
    k = str(mid)
    if k in xg_cache:
        return tuple(xg_cache[k])
    try:
        md = _get(f"{API}/matchDetails", params={"matchId": k})
    except Exception:  # noqa: BLE001
        return None
    vals = _shot_xg(md)
    if vals:
        xg_cache[k] = list(vals)
    return vals


def _resolve_names(div, slug, names, nmap, yr4=None):
    """Peta {name_fotmob: title_understat}; hasil difersist ke nmap.
    div untuk kunci peta ('E0'|...), slug untuk lokasi file dump musim
    ('EPL'|...). Pencocokan token-match & difflib >=0.74 terhadap nama
    understat, alias satu grup (ALIAS_GROUPS) diperlakukan setara.
    Bila judul terpilih bukan alias yang dipakai musim berjalan, tiada
    diganti alias musim berjalan agar row gabungan konsisten. Return
    ({nama: title|None}, {nama_gagal})."""
    yr_titles = _ustat_titles(slug, yr4)
    all_titles = _ustat_titles(slug)
    title_lut = {_clean(t): t for t in all_titles | yr_titles}
    fails = set()
    for n in names:
        key = f"{div}|{n}"
        if nmap.get(key):  # entri None dari run lama tetap dicoba lagi
            continue
        cand = _clean(n)
        got = None
        for clt, t in title_lut.items():
            if _name_match(cand, clt):
                got = t
                break
        if got is None and title_lut:
            r, t = max((difflib.SequenceMatcher(None, cand, c).ratio(), ct)
                       for c, ct in title_lut.items())
            if r >= 0.74:
                got = t
        if got is not None:
            # samakan alias dgn yang dipakai musim berjalan
            gk = _club_key(_clean(got))
            sib = sorted(t for t in yr_titles
                         if _club_key(_clean(t)) == gk)
            if sib:
                got = sib[0]
        nmap[key] = got
        if got is None:
            fails.add(n)
        else:
            fails.discard(n)
    resolved = {n: nmap.get(f"{div}|{n}") for n in names}
    fails = {n for n in names if not resolved.get(n)}
    return resolved, fails


def _row_key(r):
    return ((r.get("datetime") or ""),
            (r.get("h") or {}).get("title", ""),
            (r.get("a") or {}).get("title", ""))


def _xg_year():
    d = datetime.now()
    return d.year if d.month >= 7 else d.year - 1


def fetch(slug, backfill=False):
    """Musim berjalan menyatu dengan dump lama (riwayat Understat tetap).

    Return list rows Understat-schema (terurut datetime). Amber:
    - baris lama dipertahankan identik bila tak ada informasi baru;
    - baris lama 'bukan hasil' yang kini selesai di FotMob DIGANTIKAN
      dgn baris FotMob (goals + xG);
    - laga selesai tanpa xG dienrich dari matchDetails (batas
      XG_MAX_ENRICH_PER_RUN per run, backfill=True mematikan batas).
    """
    lid, cc, div = LEAGUES[slug]
    yr4 = _xg_year()
    lg = _get(f"{API}/leagues", params={"id": lid, "ccode3": cc})
    fixtures = (lg.get("fixtures") or {})
    matches = fixtures.get("allMatches") or []
    if not matches:
        raise ValueError(f"allMatches kosong u/ {slug} ({lid}/{cc})")
    season_now = (lg.get("allAvailableSeasons") or ["?"])[0]
    if str(season_now) != f"{yr4}/{yr4 + 1}":
        raise ValueError(
            f"musim FotMob {season_now} != {yr4}/{yr4 + 1} utk {slug}")

    base = _load_json(os.path.join(XG, f"{slug}_{yr4}.json"), [])
    base_by_key = {_row_key(r): r for r in base}

    nmap = _load_json(NMAP_CACHE, {})
    xg_cache = _load_json(XG_CACHE, {})

    # Nama payload: gunakan longName (nama panjang, 'Coventry City')
    rows_new = []

    def _score(status):
        """('3','0') dari status.scoreStr ('3 - 0'); None bila tak valid."""
        ss = str(status.get("scoreStr") or "").strip()
        parts = [p for p in ss.replace("–", "-").split("-")]
        if len(parts) == 2:
            try:
                return (str(int(parts[0].strip())),
                        str(int(parts[1].strip())))
            except ValueError:
                return None
        return None

    for m in matches:
        status = m.get("status") or {}
        utctime = status.get("utcTime")
        if not utctime:
            continue
        try:
            dt = datetime.fromisoformat(
                str(utctime).replace("Z", "+00:00")).strftime(
                "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        hm, aw = m.get("home") or {}, m.get("away") or {}
        rows_new.append({
            "id": str(m.get("id") or ""),
            "dt": dt,
            "fin": bool(status.get("finished")) and not
            status.get("cancelled") and not status.get("awarded"),
            "score": _score(status),
            "idh": str(hm.get("id") or ""),
            "ida": str(aw.get("id") or ""),
            "nhome": hm.get("longName") or hm.get("name") or "",
            "naway": aw.get("longName") or aw.get("name") or "",
        })

    names = sorted(({r["nhome"] for r in rows_new} |
                    {r["naway"] for r in rows_new}) - {""})
    resolved, fails = _resolve_names(div, slug, names, nmap, yr4=yr4)
    if fails:
        LAST_SOURCES.setdefault("_fails", {})[div] = sorted(fails)

    out = list(base)

    def _pk(h, a):
        """Kunci pasangan alias-aware: 'FC Cologne' ≡ '1. FC Köln'."""
        return (_club_key(_clean(h)), _club_key(_clean(a)))

    # Pasangan (h, a) unik per musim (double round-robin) — basis
    # rekonsiliasi: Understat beku bisa memuat pasangan ganda
    # (jadwal placeholder vs reschedule) dgn jam berbeda dari FotMob;
    # baris lama 'bukan hasil' dgn pasangan sama digantikan, sisa
    # duplikat pasangan dibuang.
    pair_idx: dict[tuple, int] = {}
    extra_pairs: dict[tuple, list[int]] = {}
    for i, r in enumerate(out):
        k = _pk((r.get("h") or {}).get("title") or "",
                (r.get("a") or {}).get("title") or "")
        if k not in pair_idx:
            pair_idx[k] = i
        elif pair_idx[k] != i:
            extra_pairs.setdefault(k, []).append(i)

    def _pairs_all(k):
        return ([pair_idx[k]] if k in pair_idx else []) + \
            extra_pairs.get(k, [])

    def _reindex():
        pair_idx.clear()
        extra_pairs.clear()
        for i, rr in enumerate(out):
            k2 = _pk((rr.get("h") or {}).get("title") or "",
                     (rr.get("a") or {}).get("title") or "")
            if k2 not in pair_idx:
                pair_idx[k2] = i
            elif pair_idx[k2] != i:
                extra_pairs.setdefault(k2, []).append(i)

    enriched = 0
    for r in rows_new:
        th = resolved.get(r["nhome"]) or r["nhome"]
        ta = resolved.get(r["naway"]) or r["naway"]
        pair = _pk(th, ta)
        key = (r["dt"], th, ta)
        base_ids = _pairs_all(pair)
        base_result = any(out[i].get("isResult") for i in base_ids)

        if base_ids and base_result:
            # Understat sudah mencatat hasil (xG-nya): pertahankan,
            # buang duplikat pasangan lain agar tak menumpuk.
            keep_i = next((i for i in base_ids if out[i].get("isResult")),
                          base_ids[0])
            for i in sorted(set(base_ids) - {keep_i}, reverse=True):
                out.pop(i)
            _reindex()
            continue

        row = {
            "id": r["id"],
            "isResult": bool(r["fin"]),
            "h": {"id": r["idh"], "title": th, "short_title": th[:3].upper()},
            "a": {"id": r["ida"], "title": ta, "short_title": ta[:3].upper()},
            "datetime": r["dt"],
        }
        if r["fin"] and r["score"] is not None:
            row["goals"] = {"h": r["score"][0], "a": r["score"][1]}
            xg = None
            cached = xg_cache.get(r["id"])
            if cached:
                xg = {"h": cached[0], "a": cached[1]}
            if xg is None and (enriched < XG_MAX_ENRICH_PER_RUN or backfill):
                vals = _fetch_xg(r["id"], xg_cache)
                if vals:
                    xg = {"h": vals[0], "a": vals[1]}
                enriched += 1
            if xg is not None:
                row["xG"] = xg
        if base_ids:
            first_i = base_ids[0]
            out[first_i] = row
            for i in sorted(base_ids[1:], reverse=True):
                out.pop(i)
            _reindex()
        else:
            out.append(row)
            pair_idx.setdefault(pair, len(out) - 1)

    _save_json(NMAP_CACHE, nmap)
    _save_json(XG_CACHE, xg_cache)
    out.sort(key=_row_key)
    return out


def main():
    """Segarkan semua liga; return {div: sumber} (kontrak refresh_fixtures).

    Sumber 'fotmob.com' = segar; 'fallback disk (...)' = fetch gagal dan
    file ditulis ulang dari dump _all.json beku di disk. Menulis tiga
    file per liga: {slug}_{yr}_fixtures.json, {slug}_{yr}.json,
    {slug}_{yr}_all.json (semua berisi dump musim penuh yang sama).
    """
    bdir = os.path.join(XG, "backup_fixtures")
    os.makedirs(bdir, exist_ok=True)
    sources = {}
    LAST_SOURCES.clear()
    yr4 = _xg_year()
    for slug, (lid, cc, div) in LEAGUES.items():
        path = os.path.join(XG, f"{slug}_{yr4}_fixtures.json")
        old = _load_json(path, [])
        src = "fotmob.com"
        try:
            fresh = fetch(slug)
        except Exception as e:  # noqa: BLE001
            allp = os.path.join(XG, f"{slug}_{yr4}_all.json")
            fresh = _load_json(allp, [])
            if not fresh:
                print(f"[{div:>3}] GAGAL: fetch FotMob error & fallback "
                      f"disk kosong ({e!r})")
                continue
            src = f"fallback disk ({e})"
        old_keys = {_row_key(r) for r in old}
        new_keys = {_row_key(r) for r in fresh}
        add = sorted(x for x in new_keys - old_keys if x[0])
        drop = sorted(x for x in old_keys - new_keys if x[0])
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        bpath = os.path.join(bdir, f"{slug}_{yr4}_fixtures_{ts}.json")
        try:
            shutil.copy2(path, bpath)
        except OSError:
            pass
        aged = sorted(f for f in os.listdir(bdir)
                      if f.startswith(f"{slug}_{yr4}_fixtures_"))
        for f in aged[:-4]:
            try:
                os.remove(os.path.join(bdir, f))
            except OSError:
                pass
        _save_json(path, fresh)
        for p in (os.path.join(XG, f"{slug}_{yr4}.json"),
                  os.path.join(XG, f"{slug}_{yr4}_all.json")):
            try:
                _save_json(p, fresh)
            except OSError as e:
                print(f"[{div:>3}] tulis {os.path.basename(p)} gagal: {e!r}")
        sources[div] = src
        LAST_SOURCES[div] = src
        print(f"[{div:>3}] {src}: {len(old)}->{len(fresh)} rows "
              f"| baru>=H: +{len(add)} / -{len(drop)}")
        for d in add[:5]:
            print("  +", d[0], d[1][:16], "v", d[2])
        for d in drop[:5]:
            print("  -", d[0], d[1][:16], "v", d[2])
    fails = LAST_SOURCES.pop("_fails", None)
    if fails:
        print("PERINGATAN: nama FotMob yang gagal dipetakan "
              "(row tetap pakai nama mentah):")
        for div, fs in fails.items():
            print(f"  [{div}] {fs}")
    return sources


if __name__ == "__main__":
    _s = main()
    if any(str(s).startswith("fallback") for s in _s.values()):
        print("PERINGATAN: sebagian liga disegarkan dari fallback disk "
              "(konten beku), bukan dari FotMob")
        raise SystemExit(1)
