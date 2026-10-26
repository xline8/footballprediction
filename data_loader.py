#!/usr/bin/env python3
"""data_loader.py — Loader sumber data terpadu dengan caching.

Menggantikan pembacaan file CSV berulang di setiap skrip dengan singleton cache.
Dipakai oleh semua modul model untuk load matches, fixtures, dan odds.
"""

import os
import json
from datetime import date, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict

# Gunakan modul lokal yang sudah kita buat (tanpa fallback diam-diam).
from football_etl import *

# Singleton loader instances
_loader_instance = None
_cache_instance = None


def get_match_cache() -> MatchCache:
    """Dapatkan singleton MatchCache instance."""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = MatchCache()
    return _cache_instance


def get_loader() -> 'MatchLoader':
    """Dapatkan singleton MatchLoader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = MatchLoader()
    return _loader_instance


class MatchLoader:
    """Loader data terpadu untuk pipeline prediksi.

    Fitur:
    - Singleton pattern (load sekali, gunakan di semua modul)
    - Caching otomatis via MatchCache
    - Method untuk load matches, fixtures, odds
    - Incremental loading (hanya muat data yang diminta)
    """

    def __init__(self):
        self.cache = get_match_cache()
        self._fixtures_cache: Dict[str, List[Dict]] = {}
        self._odds_cache: Dict[str, Dict] = {}

    def get_all_matches(self) -> List[Dict]:
        """Dapatkan semua match dari cache."""
        return self.cache.matches

    def get_matches_by_div(self, div: str) -> List[Dict]:
        """Dapatkan match untuk divisi tertentu."""
        return self.cache.get_div_matches(div)

    def get_matches_in_season(self, div: str, season: str) -> List[Dict]:
        """Dapatkan match untuk divisi dan musim tertentu."""
        all_matches = self.get_matches_by_div(div)
        return [m for m in all_matches if m.get('season') == season and
                m.get('ftr') in ('H', 'D', 'A')]

    def get_matches_in_date_range(self, div: str, start: date,
                                   end: date) -> List[Dict]:
        """Dapatkan match dalam rentang tanggal untuk divisi."""
        return self.cache.get_matches_in_date_range(div, start, end)

    def get_team_history(self, div: str, team: str, cutoff: date,
                          max_matches: int = 1000) -> List[Dict]:
        """Dapatkan riwayat pertandingan tim hingga tanggal tertentu."""
        # Gunakan cache untuk tim, lalu filter berdasarkan divisi
        all_history = self.cache.get_team_history(team, cutoff)

        # Filter hanya match di divisi ini (untuk akurasi)
        team_history = [
            m for m in all_history
            if m.get('div') == div and m.get('date') < cutoff and
               m.get('ftr') in ('H', 'D', 'A')
        ]

        # Sort by date
        team_history.sort(key=lambda x: x['date'])
        return team_history[-max_matches:] if max_matches else team_history

    def get_walk_forward_groups(self, div: str, seasons: set, freq: str = "m") -> Dict:
        """Buat kelompok match untuk walk-forward validation.

        freq: "m" = monthly, "w" = weekly
        """
        matches = self.get_matches_in_seasons(div, seasons)
        groups = defaultdict(list)

        for m in matches:
            d = m.get('date')
            if not d:
                continue

            if freq == "m":
                key = (m['div'], d.year, d.month)
            elif freq == "w":
                iso = d.isocalendar()
                key = (m['div'], iso[0], iso[1])
            else:  # daily
                key = (m['div'], d.year, d.month, d.day)

            groups[key].append(m)

        return dict(groups)

    def get_matches_in_seasons(self, div: str, seasons: set) -> List[Dict]:
        """Dapatkan semua match untuk divisi & musim tertentu."""
        all_matches = self.get_matches_by_div(div)
        return [
            m for m in all_matches
            if m.get('season') in seasons and m.get('ftr') in ('H', 'D', 'A')
        ]

    def load_fixtures(self, season: str = "2026") -> List[Dict]:
        """Load fixture dari xg_raw dengan caching."""
        cache_key = f"fixtures_{season}"
        if cache_key in self._fixtures_cache:
            return self._fixtures_cache[cache_key]

        fixtures = load_fixtures(season)
        self._fixtures_cache[cache_key] = fixtures
        return fixtures

    def load_fd_odds(self, div: str, season: str = "2627") -> Dict[Tuple, Dict]:
        """Load odds dari football-data CSV."""
        cache_key = f"odds_{div}_{season}"
        if cache_key in self._odds_cache:
            return self._odds_cache[cache_key]

        odds_map = load_fd_odds(div, season)
        self._odds_cache[cache_key] = odds_map
        return odds_map

    def get_config(self) -> dict:
        """Load konfigurasi model."""
        return get_config()

    def load_all_for_modeling(self, div: str, seasons: set,
                              freq: str = "m") -> Tuple[List[Dict], Dict]:
        """Load semua data yang diperlukan untuk modeling walk-forward.

        Returns:
            matches: List semua match (sorted by date)
            groups: Dict kelompok per (div, year, month) untuk test seasons
        """
        # Get all matches for this division
        matches = self.get_matches_in_seasons(div, seasons)

        # If no seasons specified, get all
        if not seasons:
            matches = self.get_matches_by_div(div)

        # Sort by date
        matches.sort(key=lambda x: (x['date'] or date.min))

        # Build walk-forward groups
        groups = defaultdict(list)
        for m in matches:
            d = m.get('date')
            if not d:
                continue

            if freq == "m":
                key = (m['div'], d.year, d.month)
            elif freq == "w":
                iso = d.isocalendar()
                key = (m['div'], iso[0], iso[1])
            else:
                key = (m['div'], d.year, d.month, d.day)

            groups[key].append(m)

        return matches, dict(groups)

    def get_team_matchup_history(self, div: str, home: str, away: str,
                                  cutoff: date) -> Dict:
        """Dapatkan statistik head-to-head antar dua tim.

        Returns dict dengan:
        - h2h_home: skor ketika home jadi tuan rumah
        - h2h_away: skor ketika away jadi tamu
        - last_n_home: N pertandingan terakhir home sebagai tuan rumah
        - last_n_away: N pertandingan terakhir away sebagai tamu
        """
        all_matches = self.get_matches_by_div(div)

        h2h_home = []
        h2h_away = []
        recent_home = []
        recent_away = []

        for m in all_matches:
            if not m.get('date') or m['date'] >= cutoff:
                continue

            # Head-to-head
            if m['home'] == home and m['away'] == away:
                h2h_home.append((m['yh'], m['ya'], m['ftr']))
                recent_home.append(m)
            elif m['home'] == away and m['away'] == home:
                h2h_away.append((m['ya'], m['yh'],
                                'H' if m['ftr'] == 'A' else ('A' if m['ftr'] == 'H' else 'D')))
                recent_away.append(m)

            # Recent form (last 5 matches for each team)
            if len(recent_home) < 5 and (
                    (m['home'] == home and m['date'] < cutoff) or
                    (m['away'] == home and m['date'] < cutoff)):
                recent_home.append(m)
            if len(recent_away) < 5 and (
                    (m['home'] == away and m['date'] < cutoff) or
                    (m['away'] == away and m['date'] < cutoff)):
                recent_away.append(m)

        return {
            'h2h_home': h2h_home[-10:],  # Last 10 encounters
            'h2h_away': h2h_away[-10:],
            'recent_home': recent_home[-5:],
            'recent_away': recent_away[-5:],
            'total_h2h': len(h2h_home) + len(h2h_away)
        }

    def get_league_stats(self, div: str, cutoff: date,
                          lookback_days: int = 365) -> Dict:
        """Dapatkan statistik liga (average goals, over rate, dll).

        Useful untuk baseline model atau calibration.
        """
        start_date = cutoff - timedelta(days=lookback_days)
        matches = self.get_matches_in_date_range(div, start_date, cutoff)

        total_goals = 0
        over_25 = 0
        btts = 0
        n = 0

        for m in matches:
            yh = m.get('yh')
            ya = m.get('ya')
            if yh is None or ya is None:
                continue

            total_goals += yh + ya
            over_25 += 1 if (yh + ya) > 2 else 0
            btts += 1 if (yh > 0 and ya > 0) else 0
            n += 1

        return {
            'avg_goals_per_game': total_goals / max(n, 1),
            'over_25_pct': over_25 / max(n, 1),
            'btts_pct': btts / max(n, 1),
            'total_matches': n,
            'period_start': start_date.isoformat(),
            'period_end': cutoff.isoformat()
        }

    def invalidate_fixture_cache(self, season: str = None):
        """Hapus cache fixtures (dipanggil saat ada update jadwal)."""
        if season:
            keys_to_remove = [k for k in self._fixtures_cache if season in k]
            for k in keys_to_remove:
                del self._fixtures_cache[k]
        else:
            self._fixtures_cache.clear()

    def get_data_summary(self) -> dict:
        """Dapatkan ringkasan data yang tersedia."""
        summary = {
            'total_matches': len(self.cache.matches),
            'divisions': list(self.cache.by_div.keys()),
            'season_range': None,
            'date_range': None,
            'top_teams': [],
            'cache_status': {}
        }

        # Date range
        dates = [m['date'] for m in self.cache.matches if m.get('date')]
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            summary['date_range'] = {
                'start': min_date.isoformat(),
                'end': max_date.isoformat()
            }

            # Season range
            seasons = set(m.get('season', '') for m in self.cache.matches)
            summary['season_range'] = {
                'count': len(seasons),
                'seasons': sorted(seasons)
            }

        # Per-division breakdown
        div_summary = {}
        for div in self.cache.by_div:
            div_matches = self.cache.get_div_matches(div)
            div_summary[div] = {
                'n_matches': len(div_matches),
                'seasons': sorted(set(m.get('season', '') for m in div_matches)),
                'teams': len(self.cache.get_team_history('', max_date or date.today())
                           ) if div_matches else 0
            }
        summary['per_division'] = div_summary

        # Cache info
        summary['cache_status'] = {
            'matches_cached': len(self.cache.matches) > 0,
            'cache_file': os.path.exists(self.cache._cache_file),
            'cache_dir': self.cache._cache_file
        }

        return summary


if __name__ == "__main__":
    # Test loader
    print("Testing data_loader module...")

    loader = get_loader()
    summary = loader.get_data_summary()
    print(f"\nData Summary:")
    print(json.dumps(summary, indent=2, default=str))

    # Test fixture loading
    fixtures = loader.load_fixtures("2026")
    print(f"\nUpcoming fixtures (2026): {len(fixtures)}")

    # Test match loading
    epl_matches = loader.get_matches_by_div("E0")
    print(f"EPL matches: {len(epl_matches)}")

    # Test team history
    team_hist = loader.get_team_history("E0", "arsenal", date(2020, 1, 1))
    print(f"Arsenal history (before 2020-01-01): {len(team_hist)} matches")

    print("\nDone!")
