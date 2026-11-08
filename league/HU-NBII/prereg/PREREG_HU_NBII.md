# Phase A preregistration — HU-NBII (FotMob 9117)

**No fitting is done under this preregistration, and none is done.**

## Registered question

Is there a gateable season-blocked development window plus a virgin window for
G, S, C, K, or T? **No.** The gate needs at least one training season and one
evaluation season. 2025/26 has only 96/240 genuine scores (40%); 2026/27 is
transitional with 104 inventory-level matches. There is no complete genuine
season.

Payload evidence: 103 rows have no scoreStr and are pre-match fetches; 41 have
a scoreStr but `finished=false` and are mid-match captures. Stats, shotmap
shots, period splits, referee text, and usable lineups are absent in 344/344.
There are 47 card events total. Genuine scores are 96 + 104 = 200, with 533
goals; OU2.5 SE is 4.9pp at n=104 and 3.5pp pooled at n=200, versus a 1pp
clean-PASS threshold.

## Registered decisions

- Arms: none.
- Primary lines: none.
- Halves constants: none frozen.
- Virgin: **NOT READ for evaluation** for every candidate. 2026/27 is tallied
  only at inventory level (n, rounds, dates, levels); it is not a virgin score.
- No fitting, engines, predictions, or rescue arms.

Format is frozen as one 16-team, 30-round double round-robin with no split or
playoff. Pooling with HU-NBI is rejected as disjoint-tier transfer; using
partial scores is rejected as contamination; round-blocked dev is a program
frame change. Movers are recorded in EDA, but X2 is dropped: only three relevant
mover cases are usable and no window exists.

## Verdict

**0 PASS / 0 FAIL / 5 NOT BUILDABLE.** G-HU-NBII, S-HU-NBII, C-HU-NBII,
K-HU-NBII, and T-HU-NBII are not buildable. Earliest revisit is dev on
2025/26+2026/27 once both are complete and re-fetched, virgin 2027/28, under a
fresh preregistration. Nothing is scheduled.
