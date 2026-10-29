#!/usr/bin/env python3
"""football_etl.py — Shared ETL utilities, loaders, dan cache layer.

Fase 1 dari refactoring pipeline prediksi sepakbola.
Menyamakan parsing, normalisasi, dan caching untuk semua modul model.
"""

import csv
import json
import os
import pickle
import math
from typing import Optional, List, Dict, Any
from collections import defaultdict
from datetime import datetime, date

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "all_matches_clean.csv")
RAW_DIR = os.path.join(BASE, "raw")
XGRAW = os.path.join(BASE, "xg_raw")
CACHE_DIR = os.path.join(BASE, ".cache", "models")

TOP5 = ["E0", "D1", "I1", "SP1", "F1"]

# Konfigurasi default model
DEFAULT_CONFIG = {
    "hl": 270,
    "freq": "m",
    "w_1x2": 0.05,
    "w_ou": 0.05
}


def to_float(x) -> Optional[float]:
    """Konversi aman ke float, mengembalikan None jika tidak valid."""
    try:
        if x is None or (isinstance(x, str) and not x.strip()):
            return None
        v = float(x)
        return v if v == v else None  # check NaN
    except (TypeError, ValueError):
        return None


def to_int(x) -> Optional[int]:
    """Konversi aman ke int."""
    try:
        if x is None or (isinstance(x, str) and not x.strip()):
            return None
        return int(float(x))
    except (TypeError, ValueError):
        return None


# --- Normalisasi Nama Tim ---
ALIAS = {
    "man city": "man city",
    "manchester city": "man city",
    "man united": "man united",
    "manchester united": "man united",
    "man utd": "man united",
    "newcastle": "newcastle",
    "newcastle united": "newcastle",
    "newcastle utd": "newcastle",
    "tottenham": "tottenham",
    "tottenham hotspur": "tottenham",
    "wolves": "wolverhampton",
    "wolverhampton": "wolverhampton",
    "wolverhampton wanderers": "wolverhampton",
    "west brom": "west bromwich albion",
    "west bromwich": "west bromwich albion",
    "west ham": "west ham united",
    "west ham united": "west ham united",
    "qpr": "queens park rangers",
    "stoke": "stoke city",
    "swansea": "swansea city",
    "cardiff": "cardiff city",
    "norwich": "norwich city",
    "hull": "hull city",
    "birmingham": "birmingham city",
    "derby": "derby county",
    "ipswich": "ipswich town",
    "leeds": "leeds united",
    "nottm forest": "nottingham forest",
    "nottingham forest": "nottingham forest",
    "brighton": "brighton and hove albion",
    "brighton and hove albion": "brighton and hove albion",
    "bournemouth": "bournemouth",
    "sheffield weds": "sheffield wednesday",
    "sheffield united": "sheffield united",
    "sheffield wednesday": "sheffield wednesday",
    "ath madrid": "atletico madrid",
    "atletico madrid": "atletico madrid",
    "ath bilbao": "athletic bilbao",
    "athletic bilbao": "athletic bilbao",
    "athletic club": "athletic bilbao",
    "sociedad": "real sociedad",
    "real sociedad": "real sociedad",
    "betis": "real betis",
    "real betis": "real betis",
    "espanyol": "espanyol",
    "espanol": "espanyol",
    "spanyol": "espanyol",
    "celta": "celta vigo",
    "celta vigo": "celta vigo",
    "vallecano": "rayo vallecano",
    "rayo vallecano": "rayo vallecano",
    "santander": "racing santander",
    "racing santander": "racing santander",
    "dortmund": "borussia dortmund",
    "borussia dortmund": "borussia dortmund",
    "bayern munich": "bayern munchen",
    "bayern munchen": "bayern munchen",
    "bayern leverkusen": "bayer leverkusen",
    "bayer leverkusen": "bayer leverkusen",
    "leverkusen": "bayer leverkusen",
    "wolfsburg": "vfl wolfsburg",
    "vfl wolfsburg": "vfl wolfsburg",
    "stuttgart": "vfb stuttgart",
    "vfb stuttgart": "vfb stuttgart",
    "mainz": "mainz 05",
    "mainz 05": "mainz 05",
    "hoffenheim": "tsg hoffenheim",
    "tsg hoffenheim": "tsg hoffenheim",
    "hertha": "hertha berlin",
    "hertha berlin": "hertha berlin",
    "schalke": "schalke 04",
    "schalke 04": "schalke 04",
    "union berlin": "union berlin",
    "dusseldorf": "fortuna dusseldorf",
    "monchengladbach": "monchengladbach",
    "borussia monchengladbach": "monchengladbach",
    "m gladbach": "monchengladbach",
    "ein frankfurt": "eintracht frankfurt",
    "eintracht frankfurt": "eintracht frankfurt",
    "frankfurt": "eintracht frankfurt",
    "fc koln": "koln",
    "koln": "koln",
    "paris sg": "paris saint germain",
    "paris saint germain": "paris saint germain",
    "psg": "paris saint germain",
    "paris st germain": "paris saint germain",
    "marseille": "olympique marseille",
    "olympique marseille": "olympique marseille",
    "lyon": "olympique lyonnais",
    "olympique lyonnais": "olympique lyonnais",
    "lille": "losc lille",
    "losc lille": "losc lille",
    "nice": "ogc nice",
    "ogc nice": "ogc nice",
    "rennes": "stade rennais",
    "stade rennais": "stade rennais",
    "saint etienne": "as saint etienne",
    "as saint etienne": "as saint etienne",
    "le havre": "le havre",
    "inter": "internazionale",
    "internazionale": "internazionale",
    "milan": "ac milan",
    "ac milan": "ac milan",
    "roma": "as roma",
    "as roma": "as roma",
    "lazio": "ss lazio",
    "ss lazio": "ss lazio",
    "napoli": "ssc napoli",
    "ssc napoli": "ssc napoli",
    "juve": "juventus",
    "juventus": "juventus",
    "verona": "hellas verona",
    "hellas verona": "hellas verona",
    "atalanta": "atalanta",
    "fiorentina": "fiorentina",
    "roma": "as roma",
    "bologna": "bologna",
    "torino": "torino",
    "monza": "monza",
    "lecce": "lecce",
    "lecce": "lecce",
    "feyenoord": "feyenoord",
    "ajax": "ajax",
    "psv": "psv eindhoven",
    "az alkmaar": "az alkmaar",
    "fc midtjylland": "fc midtjylland",
    "brondby": "brondby",
    "dynamo dresden": "dynamo dresden",
    "sc freiburg": "sc freiburg",
    "fsv mainz": "mainz 05",
    "eintracht frankfurt": "eintracht frankfurt",
}

DROP_TOKENS = {"fc", "cf", "sc", "ac", "as", "ss", "us", "ud", "rc", "afc", "club",
               "bk", "if", "cd", "ca", "sv", "vfl", "vfb", "tsg", "fsv", "de", "the",
               "calcio", "ssc", "acf", "krc", "rsc", "kv", "ogc", "losc"}


def normalize_name(name: str) -> str:
    """Normalisasi nama tim ke format standar."""
    if not name:
        return ""
    s = name.lower().strip()
    # Hapus angka (misal "05", "04")
    import re
    s = re.sub(r"\b\d+\b", " ", s)
    s = re.sub(r"[^a-z ]", " ", s)
    tokens = [t for t in s.split() if t not in DROP_TOKENS]
    s = " ".join(tokens) if tokens else s
    s = ALIAS.get(s, s)
    # Coba lagi setelah alias
    tokens = [t for t in s.split() if t not in DROP_TOKENS]
    return " ".join(tokens) if tokens else s


# --- Load Matches ---
def load_matches(path: str = None) -> List[Dict[str, Any]]:
    """Load semua match dari all_matches_clean.csv ke list of dict."""
    if path is None:
        path = DATA

    if not os.path.exists(path):
        raise FileNotFoundError(f"File data tidak ditemukan: {path}")

    records = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec = dict(row)
            # Parse tanggal
            d = to_date(rec.get("Date", ""))
            rec["date"] = d
            rec["season"] = rec.get("Season", "")
            rec["div"] = rec.get("Div", "").strip()
            rec["home"] = normalize_name(rec.get("HomeTeam", ""))
            rec["away"] = normalize_name(rec.get("AwayTeam", ""))
            rec["yh"] = to_int(rec.get("FTHG"))
            rec["ya"] = to_int(rec.get("FTAG"))
            rec["ftr"] = (rec.get("FTR") or "").strip().upper()
            # Corner data
            rec["hc"] = to_int(rec.get("HC"))
            rec["ac"] = to_int(rec.get("AC"))
            # Odds
            rec["ps_close"] = (
                to_float(rec.get("PSCH")),
                to_float(rec.get("PSCD")),
                to_float(rec.get("PSCA"))
            )
            rec["avg_close"] = (
                to_float(rec.get("AvgCH")),
                to_float(rec.get("AvgCD")),
                to_float(rec.get("AvgCA"))
            )
            rec["b365_close"] = (
                to_float(rec.get("B365CH")),
                to_float(rec.get("B365CD")),
                to_float(rec.get("B365CA"))
            )
            rec["open"] = (
                to_float(rec.get("AvgH")),
                to_float(rec.get("AvgD")),
                to_float(rec.get("AvgA"))
            )
            rec["open_b365"] = (
                to_float(rec.get("B365H")),
                to_float(rec.get("B365D")),
                to_float(rec.get("B365A"))
            )
            rec["ou_close"] = (
                to_float(rec.get("AvgC>2.5")),
                to_float(rec.get("AvgC<2.5"))
            )
            rec["ou_open"] = (
                to_float(rec.get("Avg>2.5")),
                to_float(rec.get("Avg<2.5"))
            )
            rec["ou_open_b365"] = (
                to_float(rec.get("B365>2.5")),
                to_float(rec.get("B365<2.5"))
            )
            rec["ah_line"] = to_float(rec.get("AHh"))
            rec["ah_close"] = (
                to_float(rec.get("AvgCAHH")),
                to_float(rec.get("AvgCAHA"))
            )
            rec["hst"] = to_int(rec.get("HST"))
            rec["ast"] = to_int(rec.get("AST"))
            rec["hs"] = to_int(rec.get("HS"))
            rec["as_"] = to_int(rec.get("AS"))
            records.append(rec)

    return records


def parse_date(s) -> Optional[date]:
    """Parse tanggal dari beberapa format umum.

    Data football-data.co.uk memakai dd/mm/yyyy pada file raw, sedangkan
    all_matches_clean.csv memakai YYYY-MM-DD. Satu parser untuk keduanya
    menghilangkan risiko join yang gagal karena misformat.
    """
    if s is None:
        return None
    s = s.strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def to_date(s) -> Optional[date]:
    """Alias compat: parse tanggal (multi-format)."""
    return parse_date(s)


# --- Cache Layer ---
class MatchCache:
    """Cache layer untuk match data dan lookup indexes."""

    def __init__(self, force_reload: bool = False):
        self._cache_file = os.path.join(BASE, ".cache", "matches.pkl")
        self._last_modified = 0
        self.matches: List[Dict[str, Any]] = []
        self.by_div: Dict[str, List[int]] = defaultdict(list)
        self.by_team: Dict[str, List[int]] = defaultdict(list)
        self.by_date: Dict[date, List[int]] = defaultdict(list)
        self._load_or_build(force_reload)

    def _load_or_build(self, force_reload: bool):
        try:
            current_mtime = os.path.getmtime(DATA)
        except OSError:
            current_mtime = 0

        cache_exists = os.path.exists(self._cache_file)

        if cache_exists and not force_reload:
            cache_mtime = os.path.getmtime(self._cache_file)

            # Gunakan cache hanya jika data belum berubah
            if cache_mtime >= current_mtime:
                try:
                    with open(self._cache_file, 'rb') as f:
                        data = pickle.load(f)
                    self.matches = data['matches']
                    self.by_div = data['by_div']
                    self.by_team = data['by_team']
                    self.by_date = data['by_date']
                    self._last_modified = cache_mtime
                    return
                except Exception:
                    # Jika cache rusak, build ulang
                    pass

        # Build dari awal
        self._build_indexes()
        self._save_cache()

    def _build_indexes(self):
        self.matches = load_matches()
        self.by_div = defaultdict(list)
        self.by_team = defaultdict(list)
        self.by_date = defaultdict(list)

        for i, m in enumerate(self.matches):
            self.by_div[m['div']].append(i)
            self.by_team[m['home']].append(i)
            self.by_team[m['away']].append(i)
            if m['date']:
                self.by_date[m['date']].append(i)

    def _save_cache(self):
        os.makedirs(os.path.dirname(self._cache_file), exist_ok=True)
        data = {
            'matches': self.matches,
            'by_div': dict(self.by_div),
            'by_team': dict(self.by_team),
            'by_date': dict(self.by_date)
        }
        with open(self._cache_file, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def get_div_matches(self, div: str) -> List[Dict]:
        """Dapatkan semua match untuk divisi tertentu, terurut tanggal."""
        indices = self.by_div.get(div, [])
        return [self.matches[i] for i in sorted(indices, key=lambda j: self.matches[j]['date'])]

    def get_team_history(self, team: str, cutoff: date) -> List[Dict]:
        """Dapatkan riwayat pertandingan tim hingga tanggal tertentu."""
        norm_team = normalize_name(team)
        indices = self.by_team.get(norm_team, [])
        history = []
        for i in indices:
            m = self.matches[i]
            if m['date'] and m['date'] < cutoff and m['ftr'] in ('H', 'D', 'A'):
                history.append(m)
        return sorted(history, key=lambda x: x['date'])

    def get_matches_in_date_range(self, div: str, start: date, end: date) -> List[Dict]:
        """Dapatkan semua match dalam range tanggal untuk divisi."""
        result = []
        indices = self.by_div.get(div, [])
        for i in indices:
            m = self.matches[i]
            if m['date'] and start <= m['date'] <= end:
                result.append(m)
        return result


# --- Fixture & Odds Loading ---
def load_fixtures(season_year: str = "2026") -> List[Dict]:
    """Load fixture dari xg_raw/{slug}_{year}_fixtures.json (hanya >= hari ini)."""
    today = date.today()
    slug_map = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
                "I1": "Serie_A", "F1": "Ligue_1"}

    fixtures = []
    for div, slug in slug_map.items():
        path = os.path.join(XGRAW, f"{slug}_{season_year}_fixtures.json")
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        # Load name mapping
        nmap = {}
        for map_file in ["map_full.json", "map_ext.json"]:
            mp = os.path.join(XGRAW, map_file)
            if os.path.exists(mp):
                with open(mp, encoding="utf-8") as f:
                    nmap.update(json.load(f))

        for item in data:
            home = nmap.get(f"{div}|{item['h']['title']}")
            away = nmap.get(f"{div}|{item['a']['title']}")
            if not home or not away:
                continue
            dt = datetime.strptime(item["datetime"], "%Y-%m-%d %H:%M:%S").date()
            if dt < today:
                continue  # jangan muat fixture yang sudah lewat
            fixtures.append({
                "div": div,
                "date": dt,
                "time": item["datetime"].split()[1][:5],
                "home": normalize_name(home),
                "away": normalize_name(away),
                "uid": item["id"]
            })

    fixtures.sort(key=lambda x: (x['date'], x['div'], x['time']))
    return fixtures


def load_fd_odds(div: str, season: str = "2627") -> Dict[tuple, Dict]:
    """Load odds dari raw/{div}_{season}.csv (football-data).
    Kunci: (div, date_iso, home, away) -> odds dict
    """
    path = os.path.join(RAW_DIR, f"{div}_{season}.csv")
    odds_map = {}

    if not os.path.exists(path):
        return odds_map

    with open(path, encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            dt = parse_date(row.get("Date"))
            if dt is None:
                continue

            key = (div, dt.isoformat(),
                   normalize_name(row.get("HomeTeam", "")),
                   normalize_name(row.get("AwayTeam", "")))

            odds_map[key] = {
                "b365": (
                    to_float(row.get("B365H")),
                    to_float(row.get("B365D")),
                    to_float(row.get("B365A"))
                ),
                "avg": (
                    to_float(row.get("AvgH")),
                    to_float(row.get("AvgD")),
                    to_float(row.get("AvgA"))
                ),
                "ou": (
                    to_float(row.get("Avg>2.5")),
                    to_float(row.get("Avg<2.5"))
                ),
                "b365_ou": (
                    to_float(row.get("B365>2.5")),
                    to_float(row.get("B365<2.5"))
                )
            }

    return odds_map


def get_config(path: str = None) -> dict:
    """Load config dari v2_config.json atau gunakan default."""
    if path is None:
        path = os.path.join(BASE, "v2_config.json")

    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


# --- Utility Functions ---
def pois(k: int, lam: float) -> float:
    """Poisson probability mass function."""
    import math
    return math.exp(-lam + k * math.log(max(lam, 1e-12)) - math.lgamma(k + 1))


def tau(x: int, y: int, lh: float, la: float, rho: float) -> float:
    """Dixon-Coles tau adjustment."""
    if x == 0 and y == 0:
        return max(0.0, 1.0 - lh * la * rho)
    if x == 0 and y == 1:
        return max(0.0, 1.0 + lh * rho)
    if x == 1 and y == 0:
        return max(0.0, 1.0 + la * rho)
    if x == 1 and y == 1:
        return max(0.0, 1.0 - rho)
    return 1.0


def norm3(odds_tuple) -> Optional[tuple]:
    """Konversi odds 3-way ke probabilitas tanpa margin."""
    if not all(odds_tuple):
        return None
    inv = [1.0 / x for x in odds_tuple]
    s = sum(inv)
    if s <= 0:
        return None
    return tuple(v / s for v in inv)


def norm2(odds_tuple) -> Optional[float]:
    """Konversi odds over/under pasangan ke probabilitas over."""
    if not all(odds_tuple) or any(x <= 1.0 for x in odds_tuple):
        return None
    inv = [1.0 / x for x in odds_tuple]
    s = sum(inv)
    return inv[0] / s  # over probability


def blend3(p1: tuple, p2: tuple, w_model: float) -> tuple:
    """Blend model probs (p1) with market probs (p2) using log-linear weighting.

    Konvensi kanonik seluruh codebase: `w_model` adalah bobot pada MODEL
    (0 = murni pasar, 1 = murni model). Ini konsisten dengan tuning di
    model_v2.main_val (config `w_1x2` = bobot model).

    Args:
        p1: (ph, pd, pa) model probabilities
        p2: (ph, pd, pa) market (odds-implied) probabilities
        w_model: weight on the model (0 = pure market, 1 = pure model)
    """
    if p2 is None:
        return p1
    blended = []
    for a, b in zip(p1, p2):
        ba = max(a, 1e-6)
        bb = max(b, 1e-6)
        log_blend = w_model * math.log(ba) + (1 - w_model) * math.log(bb)
        blended.append(math.exp(log_blend))
    s = sum(blended)
    return tuple(v / s for v in blended)


def blend2(a: float, b: float, w_model: float) -> float:
    """Blend model over-prob (a) with market over-prob (b), log-linear.

    `w_model` = bobot pada model (0 = murni pasar, 1 = murni model).
    """
    if b is None:
        return a
    x = w_model * math.log(max(a, 1e-6)) + (1 - w_model) * math.log(max(b, 1e-6))
    y = w_model * math.log(max(1 - a, 1e-6)) + (1 - w_model) * math.log(max(1 - b, 1e-6))
    return math.exp(x) / (math.exp(x) + math.exp(y))


# Maximum goals to consider in probability grid
MAXG = 10


if __name__ == "__main__":
    # Test basic functionality
    print("Testing football_etl module...")

    # Test cache
    cache = MatchCache(force_reload=True)
    print(f"Loaded {len(cache.matches)} matches")
    print(f"Divisions: {list(cache.by_div.keys())}")

    # Test fixtures
    fixtures = load_fixtures("2026")
    print(f"Loaded {len(fixtures)} upcoming fixtures")

    # Test config
    cfg = get_config()
    print(f"Config: {cfg}")

    print("Done!")
