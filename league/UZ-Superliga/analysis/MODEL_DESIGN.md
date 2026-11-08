# Phase 4 — Model Design: Uzbekistan Superliga (FotMob 540)

## Feasibility matrix

| Candidate | Target exists? | Dev window? | Virgin window? | Design? |
|---|---|---|---|---|
| G-UZ goals | Yes (FT score 215/215; HT 99/215) | **No** — one partial season | **No** — no second season | NO |
| S-UZ SOT | No (stats null, shotmap empty 215/215) | No | No | NO |
| C-UZ corners | No | No | No | NO |
| K-UZ cards | No (referee blank 215/215; 29 Card events in 99 matches) | No | No | NO |
| T-UZ total shots | No | No | No | NO |

No candidate reaches design. There are no arms, no primary lines, no
gate legs to register — the prereg (`prereg/PREREG_UZ_SUPERLIGA.md`)
records the NOT BUILDABLE verdict instead.

## Why the goals candidate cannot be designed

The reference pattern (Gate Zero = the production Dixon-Coles analogue,
unmodified) needs a season-blocked walk-forward dev: at least one
training season plus at least one evaluation season. UZ has one partial
season (2026, 215/240 matches, in progress). It can be neither: it is
incomplete (not a training season) and there is no prior season to
train on (not an evaluation season). A round-blocked within-season dev
is a program-frame change, not a league decision, and is not run.

The SHRINK thin-data treatment is moot: there is nothing to shrink
toward a gate, because no gate can be run. The G-J2 shrinkage/prior
variant lesson does not apply — it addresses new-team lambdas inside a
gateable dev, and there is no dev here.

## Halves presentation

None. HT scores exist for 99/215 matches (share 0.4588, descriptive
only, late-season coverage); no constant is frozen and no 1H/2H
presentation is designed.

## What would change this (revisit condition)

Earliest gateable build: dev on 2026 (once complete) + 2027, virgin
2028 — under a fresh preregistration; nothing is scheduled. If FotMob
coverage improves (stats blocks appearing in later seasons), S/C/K/T
become re-assessable on the same revisit, verified from payloads.
