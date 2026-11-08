# G-BR verdict — FAIL at the dev gate (OU leg); virgin NOT read

Prereg: `prereg/PREREG_G_BR.md` (frozen 7056902, before fitting).
Dev pooled n = 1,140 (scored 2022–2024). Virgin 2025 **deliberately
NOT read** — Gate Zero failed its dev gate, so under the frozen
mechanical reading all variant arms are moot and the virgin window
stays unburned for G-BR (`results_virgin.json` records
`virgin_read: false`).

## Dev results — pooled (model vs climatology)

| Arm | 1X2 LL | RPS | OU2.5 LL |
|---|---|---|---|
| Gate Zero | 1.045444 | 0.216726 | 0.699187 |
| SHRINK | 1.045444 | 0.216726 | 0.699187 |
| X2 (mover offset) | 1.063510 | 0.222217 | 0.699189 |
| X3 (X2 + set-play) | 1.067996 | 0.223509 | 0.705456 |
| Climatology / base rate | 1.064424 | 0.222885 | **0.691271** |

## Gate arithmetic

- Dev gate (all three legs must beat climatology/base rate):
  Gate Zero passes 1X2 LL (1.045444 < 1.064424) and RPS
  (0.216726 < 0.222885) but **fails the OU2.5 leg**
  (0.699187 > 0.691271). Gate Zero is dead; variants are moot.
- For the record: SHRINK is numerically identical to Gate Zero —
  degenerate under season-blocked fitting, exactly as in DK (a
  promoted side has 0 prior in-league matches, where SHRINK ≡ the
  unseen-team rule; every other side has ≥38). X2 is worse than
  Gate Zero on 1X2 LL/RPS and equally dead on OU; X3 is worse than
  climatology itself on all three metrics — the set-play tilt,
  active only from the 2024 target season (xG coverage), hurt
  where it finally switched on.
- The diagnosis the table supports: BR's DC fit ranks results
  well (LL/RPS legs pass clearly) but its goal *totals* are
  mis-scaled against a simple prior-seasons over-rate — the same
  OU weakness that failed G-J1 on the virgin, here caught one
  stage earlier, on dev.

**Ships: nothing.** G-BR is FAIL. Coordinator verification: dev
rerun reproduced every pooled figure exactly; the X2 mover sets
were checked against the known promoted clubs (2022: Avaí,
Botafogo, Coritiba, Goiás; 2023: Bahia, Cruzeiro, Grêmio, Vasco;
2024: Atlético GO, Criciúma, Juventude, Vitória — all correct;
the "Botafogo"/"Botafogo RJ" double spelling is one club,
team_id 8517, and the name-keyed mover set covers both aliases,
while ratings are keyed by team_id and unaffected).
