# Pre-registration — C-FO (Faroe Islands Premier League corners model)

**Committed before any fitting. No fitting is done under this prereg.**

## Feasibility verdict (the preregistered question)

Can a corners model be built for this league at all? **No —
C-FO is NOT BUILDABLE.** This prereg records the verdict with its
payload-level evidence, so that no fitting, no virgin read, and no
post-hoc arm can follow from it.

## Evidence (payload-verified 2026-11-10, 810/810 payloads read)

- Target data absent: `content.stats` present in **0/810** payloads;
  shotmap with shots > 0 in **0/810**. There is no corners count
  (no `corners` stat key, no corner events in the event feed — the
  feed carries Goal/Card/Substitution/Half events only).
- No corners proxy exists in the payloads, and none is invented
  here: possession, box touches, and big chances are all stats-feed
  keys, absent with the rest of the stats block (features X7/X9
  DROPPED — see `analysis/FEATURES.md`).
- Seasons 2021–2026 are otherwise complete (810 rows, 809 played
  after excluding the single awarded match 3822183), so the failure
  is purely a target-data failure, not a sample-size failure.

## Registered decisions

- Arms: **none** (the candidate never reaches design).
- Primary lines: **none chosen**.
- Virgin window (2026): **NOT READ** for C-FO — deliberately unread,
  because no arm passes (or can pass) a dev gate. Reading it would
  be a result in search of a gate.
- Halves constants: none frozen for corners (no 1H corner splits exist).
- What ships: **nothing** — no engine, no fitted params, no predictions.

## Verdict

**C-FO: NOT BUILDABLE.** Any future revisit (e.g. FotMob coverage
improving to carry stats for this league) needs a new
preregistration; nothing is scheduled.
