# Verdict — G-CA (CA-PremierLeague goals model)

**FAIL — Gate Zero fails the dev gate; virgin NOT read.**

Dev (season-blocked walk-forward, seed 2021, pooled n = 336):

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.079719 | 0.228900 | 0.714525 |
| SHRINK | 1.079719 | 0.228900 | 0.714525 |
| Climatology | **1.078165** | 0.229412 | **0.693734** |

Gate arithmetic (PREREG_G_CA): the dev gate requires pooled 1X2
LL AND RPS to beat climatology AND OU2.5 LL to beat the base
rate. Gate Zero beats climatology on RPS only; its 1X2 LL is
worse (1.079719 > 1.078165) and its OU2.5 LL is worse by 0.021
(0.714525 > 0.693734). Gate Zero is dead; per the prereg,
variants are moot, the verdict is FAIL, and the virgin window
(2025) was NOT read for this candidate.

SHRINK is numerically identical to Gate Zero in every dev season.
That is by construction here, not a bug: the fit is season-blocked,
so the only in-scope entry club (Vancouver FC, 2023) enters with
n = 0 prior in-league matches, where the shrink rule reduces to
Gate Zero's unseen-team rule, and no in-season refit ever gives it
a 1–5-match state. The arm had no room to differ on this corpus.

Per-season 1X2 LL (Gate Zero vs climatology): 2022 1.080496 vs
1.066396; 2023 1.093911 vs 1.087346; 2024 1.064750 vs 1.080752 —
the model wins only the last dev season. With 8 clubs and
112-match seasons, team ratings are estimated on very thin
per-season samples; the DC pattern does not beat pooled rates.

Ships: nothing. Virgin read: NO (deliberately unread).
