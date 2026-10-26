"""synthesize_european.py — sintesis fixture Eropa/midweek (heuristic).

Dataset asli tidak memuat jadwal UCL/UEL/UECL (div 'EC' ternyata English
National League). Solusi heuristic: peril tim yang bermain >=2 laga dalam
jendela 7 hari (termasuk hari kerja) menandakan jadwal padat — kemungkinan
besar karena laga piala/Eropa midweek. `midweek_cup_flag` = 1 bila tim punya
laga lain dalam +-3 hari sebelum pertandingan ini.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

from .utils import setup_logging, norm_team

_log = setup_logging()


def build_midweek_map(matches: list[dict[str, Any]]) -> dict[tuple[str, str, str], tuple[int, int]]:
    """Key (div, date_iso, home_norm, away_norm) -> (flag_home, flag_away)."""
    team_dates: dict[str, list[date]] = defaultdict(list)
    for m in matches:
        d = m.get("Date") or m.get("date")
        if isinstance(d, str):
            try:
                d = date.fromisoformat(d[:10])
            except ValueError:
                continue
        if not isinstance(d, date):
            continue
        team_dates[norm_team(m.get("HomeTeam") or m.get("home"))].append(d)
        team_dates[norm_team(m.get("AwayTeam") or m.get("away"))].append(d)

    def flag(team: str, d: date) -> int:
        for x in team_dates[team]:
            if x != d and abs((x - d).days) <= 3:
                return 1
        return 0

    out: dict[tuple[str, str, str], tuple[int, int]] = {}
    for m in matches:
        d = m.get("Date") or m.get("date")
        if isinstance(d, str):
            d = date.fromisoformat(d[:10])
        if not isinstance(d, date):
            continue
        home, away = norm_team(m.get("HomeTeam") or m.get("home")), \
            norm_team(m.get("AwayTeam") or m.get("away"))
        key = (m.get("Div") or m.get("div"), d.isoformat(), home, away)
        out[key] = (flag(home, d), flag(away, d))
    return out
