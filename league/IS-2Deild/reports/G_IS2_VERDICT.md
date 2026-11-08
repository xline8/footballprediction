# G-IS2 verdict — FAIL — virgin not read

Prereg: `prereg/PREREG_G_IS2.md`. Dev pooled n=528 (seasons 2022–2025, seed
2021). Virgin 2026 was **NOT read** because Gate Zero failed the dev gate;
no arm ships.

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---:|---:|---:|
| Gate Zero | 1.066661 | 0.241576 | 0.662205 |
| SHRINK | 1.066783 | 0.241467 | 0.667660 |
| X2 | 1.065650 | 0.240198 | 0.669252 |
| Climatology | 1.037573 | 0.236529 | 0.615360 |

Gate arithmetic: Gate Zero fails all three dev-gate legs — 1X2 LL 1.066661 >
climatology 1.037573, RPS 0.241576 > 0.236529, OU2.5 LL 0.662205 > base rate
0.615360. Per the frozen rule (Gate Zero fails dev ⇒ variants moot), SHRINK
and X2 are not evaluated further even though X2's pooled 1X2 LL (1.065650)
and RPS (0.240198) are marginally better than Gate Zero's — both still lose
to climatology on every leg, and the OU2.5 leg fails by a wide margin. The
virgin was not read.

Per-season Gate Zero 1X2 LL vs climatology: 2022 1.073137 vs 1.052382;
2023 1.085046 vs 1.022765; 2024 1.017768 vs 1.045769 (the only season Gate
Zero beats climatology on 1X2 LL); 2025 1.090692 vs 1.029377. OU2.5 LL loses
to the base rate in all four seasons. The DC ratings model does not beat the
expanding climatology in this league: a 12-team, 22-round, goals-only corpus
with modest team-trait reliability (split-half goals-for r=0.402,
goals-against r=0.370) and a high, volatile goal level (3.42–3.89 per match)
leaves the fitted ratings no edge over pooled outcome rates.

Diagnostics: SHRINK lambdas differ from Gate Zero on 134/528 matches
(early-season, as designed); X2 lambdas differ on 295/528 (212 vs SHRINK),
with source priors estimated only from completed prior transitions
(2022: none — no prior transitions, so X2 ≡ SHRINK that season).

**Verdict: FAIL. Nothing ships.**
