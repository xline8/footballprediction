# Verdict — G-ES (ES-LaLiga2 goals) — **FAIL** (dev gate; virgin deliberately NOT read)

Prereg: `prereg/PREREG_G_ES.md`. Goals-only DC by design (xG era
starts inside the virgin). Dev n=1,404, virgin 2025/2026 n=468
**not read**.

## Dev (pooled; climatology 1X2 LL 1.0644, RPS 0.2153, OU2.5 base-rate LL 0.6790)

| Arm | 1X2 LL | RPS | OU2.5 LL | Dev outcome |
|---|---|---|---|---|
| Gate Zero | 1.0563 | 0.2130 | **0.6829** | beats climatology on 1X2/RPS, **fails the OU leg** (0.6829 > 0.6790) |
| SHRINK | 1.0563 | 0.2130 | 0.6829 | bit-identical to Gate Zero (see below) |
| X2 | 1.0575 | 0.2133 | **0.6832** | beats climatology on 1X2/RPS, **fails the OU leg**; also worse than GZ on 1X2 LL |

Gate arithmetic: the dev gate requires all three legs. Every arm
fails the OU2.5 leg on its own numbers, so the verdict is FAIL
without needing the variants-moot rule (which would end it anyway:
Gate Zero failed its own dev gate). **Virgin NOT read; nothing
ships.**

Two construction facts, recorded plainly:

1. **SHRINK is degenerate under season-blocked fitting** — prior
   in-league match counts at a season start are 0 or ≥42, so the
   n/6 factor only ever takes the values 0 (= Gate Zero's unseen
   rule) or 1. The arm is bit-identical to Gate Zero by
   construction, as the IN-ISL prereg pre-recorded could happen.
   It is not evidence about shrinkage at match-level granularity.
2. **X2 as first ported never ran**: the ported `mover_ids` kept
   the ENGCH league-id tuple (47/108/48) in its index filter while
   the inner mapping used the ES ids (87/8968/140), so every index
   row was filtered out and the mover set was empty — X2 silently
   equalled Gate Zero in the first dev run. The coordinator caught
   the identical-to-4-decimals table on review, fixed the tuple,
   and re-ran **dev only**: movers then resolve to exactly the 7
   clubs per season named in EDA F4 (accent-normalised matching
   works: 'cadiz', 'castellon', 'cordoba' all hit), and X2's true
   dev numbers are the ones in the table above. The fix changed no
   gate outcome — X2 fails the same OU leg and trails Gate Zero on
   1X2 LL — and the virgin was never touched by either run.

**Ships: nothing.** G-ES is FAIL. Independent checks: coordinator
re-ran the goals dev harness bit-identically (Gate Zero/SHRINK to
full precision) before and after the X2 fix; grep confirms the
engine reads no `expected_goals` column anywhere (goals-only as
frozen); the mover lists were recomputed from the index by hand.
