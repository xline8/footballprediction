# Preprocessing

`data/build_data.py` reads the league index, resolves payloads from the worktree first and the main warehouse second, and emits one row per finished match. It preserves warehouse season labels, FotMob ids/names, UTC date, league-round label, score, phase, referee and the All/FirstHalf/SecondHalf team statistics.

Goals are taken from the finished score. First-half goals are derived from FotMob Goal event times (`time <= 45`) only where period splits exist; the source is recorded as `events`, otherwise the fields are null. This is the only event-derived target quantity. `has_xg` reflects an All-period expected_goals key; `shotmap_n` is the raw shotmap shot count.

All downstream model windows use `phase=regular`. Finals are excluded because knockout ties are a different population. The 2025/2026 regular season is the virgin read (110); 2026/2027 is inventory-only and reserved. No fitting is performed in this phase.
