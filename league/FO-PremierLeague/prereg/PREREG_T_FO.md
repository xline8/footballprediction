# Pre-registration — T-FO (Faroe Islands Premier League total-shots model)

**Committed before any fitting. No fitting is done under this prereg.**

## Feasibility verdict (the preregistered question)

Can a total-shots model be built for this league at all? **No —
T-FO is NOT BUILDABLE.** This prereg records the verdict with its
payload-level evidence, so that no fitting, no virgin read, and no
post-hoc arm can follow from it.

## Evidence (payload-verified 2026-11-10, 810/810 payloads read)

- Target data absent: `content.stats` present in **0/810** payloads;
  shotmap with shots > 0 in **0/810**. There is no total-shots count
  anywhere in the corpus — no stats-feed shot count, no shotmap
  shots, no shot events in the event feed.
- The total-shots family (production v1/v2, challenger E9) is a
  shots-count model; without a single observed shot count it has no
  training target, no naive baseline, and no calibration object.
  Goals are not shots and are not substituted as a proxy.
- Seasons 2021–2026 are otherwise complete (810 rows, 809 played
  after excluding the single awarded match 3822183), so the failure
  is purely a target-data failure, not a sample-size failure.

## Registered decisions

- Arms: **none** (the candidate never reaches design).
- Primary lines: **none chosen**.
- Virgin window (2026): **NOT READ** for T-FO — deliberately unread,
  because no arm passes (or can pass) a dev gate. Reading it would
  be a result in search of a gate.
- Halves constants: none frozen for total shots (no 1H shot splits exist).
- What ships: **nothing** — no engine, no fitted params, no predictions.

## Verdict

**T-FO: NOT BUILDABLE.** Any future revisit (e.g. FotMob coverage
improving to carry stats/shotmap for this league) needs a new
preregistration; nothing is scheduled.
