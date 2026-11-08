# Verdict — C-TH2 (corners): **NOT BUILDABLE**

No prereg was written and nothing was fitted for this candidate,
because the feasibility condition in the programme template fails:
**the target does not exist in this league's data.**

Evidence (Step 1, independently recomputed from the raw payloads):
`content.stats.Periods.All` is a null-valued key in **all 681**
Thai League 2 payloads; there are no period splits anywhere. The
`corners` stat therefore has zero observations in the dev season and
zero in the virgin season (2025/2026). The territorial covariates are
absent too (possession, big chance and opp-box touches all live in the
same null stats feed; X7/X9 dropped in FEATURES). The warehouse
index's `has_stats` flag claimed 678/681 — it is computed as a
key-presence test (`"All" in periods`) and is a false positive for
this league.

With no target in the data and none in the virgin window, there is no
gate to run and no virgin to read. **C-TH2 is NOT BUILDABLE and nothing
ships.** If FotMob populates this league's stats feed in the future,
the candidate needs a fresh six-step pass over the new data; nothing
in this build pre-registers it.
