# Pre-registration — S-FO (Faroe Islands Premier League shots-on-target model)

**Committed before any fitting. No fitting is done under this prereg.**

## Feasibility verdict (the preregistered question)

Can a shots-on-target model be built for this league at all? **No —
S-FO is NOT BUILDABLE.** This prereg records the verdict with its
payload-level evidence, so that no fitting, no virgin read, and no
post-hoc arm can follow from it.

## Evidence (payload-verified 2026-11-10, 810/810 payloads read)

- Target data absent: `content.stats` present in **0/810** payloads;
  shotmap with shots > 0 in **0/810** (the key exists, the list is
  empty in every payload). There is no shots-on-target count, no
  total-shots count, and no xG anywhere in the corpus.
- The event feed carries Goal/Card/Substitution/Half events only —
  no shot events, no on-target markers. No SOT proxy exists in the
  payloads, and none is invented here: goals are not shots, and a
  goals-only SOT model would be a different (unregistered) target.
- Seasons 2021–2026 are otherwise complete (810 rows, 809 played
  after excluding the single awarded match 3822183), so the failure
  is purely a target-data failure, not a sample-size failure.

## Registered decisions

- Arms: **none** (the candidate never reaches design).
- Primary lines: **none chosen**.
- Virgin window (2026): **NOT READ** for S-FO — deliberately unread,
  because no arm passes (or can pass) a dev gate. Reading it would
  be a result in search of a gate.
- Halves constants: none frozen for SOT (no 1H SOT splits exist).
- Features X4/X6 (shot quality / xGOT): DROPPED — no shotmap data
  (see `analysis/FEATURES.md`).
- What ships: **nothing** — no engine, no fitted params, no predictions.

## Verdict

**S-FO: NOT BUILDABLE.** Any future revisit (e.g. FotMob coverage
improving to carry stats/shotmap for this league) needs a new
preregistration; nothing is scheduled.
