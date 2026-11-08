# Phase 1 — Data Understanding: FotMob Bangladesh Football League

Corpus: `data_enrichment/fotmob_world/Bangladesh/Bangladesh Football League/`,
indexed by league id 10443. Inventory is measured by `analysis/eda.py` and
stored in `inventory_summary.json`; the CSV is built by `data/build_data.py`.

## Integrity headline

- 394 index rows, 394 unique finished payloads, and 394 built match rows.
- Season counts are 95, 90, 90, 90, and 29 (in progress). There are 18 FotMob
  team ids and **no** name variants.
- Stats, shotmap shots, playerStats, and period splits are absent in all 394
  payloads. Events are present in 394/394; named referees in 33/394 (4 in
  2025/2026, all 29 in 2026/2027); lineups (11 starters both sides) in 394/394.
  CoverageLevel is `lower` throughout.

## Payload anatomy

| Section | Use |
|---|---|
| `general` | match id, season, round, date, team ids/names |
| `header.status.scoreStr` | official FT target and finished flag |
| `content.matchFacts.events.events` | goals, Half markers, Red/YellowRed cards, substitutions |
| `content.stats` | null in all payloads (the index `has_stats` flag is correct here) |
| `content.shotmap.shots` | empty list in all payloads (the `shotmap` dict exists but carries no shots; the index `has_shotmap` flag is correct in effect) |
| `content.matchFacts.infoBox.Referee` | empty text except 4 matches in 2025/2026 and all 29 in 2026/2027 |

## Format and identity

- 2022/2023 has 11 teams but only rounds 4–22 in the warehouse (19 rounds × 5
  = 95 matches; rounds 1–3, 15 matches, are absent from the index). Each team
  plays 17–18 matches instead of the 20 a full double round-robin of 11 would
  give. The season is therefore **incomplete in the warehouse**; it is used as
  the dev seed with that limitation recorded, never silently treated as complete.
- 2023/2024 through 2025/2026 have 10 teams and 18 rounds (90 each; double
  round-robin, each pair meets twice). No split group or playoff exists in any
  season.
- 2026/2027 is in progress: rounds 1–5, 29 matches through 2026-10-24, with
  **13 teams** (City Club and Chattogram City are new; Mohammedan returns
  after a one-season absence — it played 2022/2023–2024/2025, sat out
  2025/2026, and is back). Round 4 has 5 matches instead of 6: Fakirerpool,
  Dhaka Wanderers, and Fortis are all absent from round 4, i.e. one round-4
  fixture among them plus one bye is missing from the index (postponed or not
  yet captured). A 13-team double round-robin would be 24 rounds / 156 matches.
- Team identity is keyed by FotMob id. No renames or spelling variants exist
  in this corpus. Chittagong Abahani (2022/2023–2024/2025) and Chattogram City
  (2026/2027) are **different ids** (1503796 vs the new Chattogram City id);
  they are not treated as the same club.

## Quirks and events

The official score is the source of truth. There are **zero** score/event
mismatches: goal-event counts agree with `scoreStr` in 394/394. Half markers
exist in 394/394 and agree with goal times through 45 minutes in all 363
checked cases (the 31 unchecked are goalless first halves, where the check is
vacuous). Overall event counts are Half 788, Goal 1,167, Substitution 2,991,
Card 59. Cards are only Red (42) and YellowRed (17); plain Yellow events are
zero in every season, so no yellow-card target exists. Substitutions occur but
carry no model signal and are not used.
