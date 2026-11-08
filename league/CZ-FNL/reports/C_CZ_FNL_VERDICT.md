# Verdict — C-CZ-FNL (CZ-FNL corners)

**NOT BUILDABLE — no prereg, no fitting, virgin NOT read.**

The candidate fails the template's feasibility condition: the target
must exist in the data. It does not exist in any era of this league's
feed.

Payload evidence (all 1,311 FNL matches, every season 2021/2022–
2026/2027): `content.stats` is `{"Periods": {"All": null}}` in every
file, and the string `corners` occurs in zero sampled rich-era files.
The warehouse index flag `has_stats=True` for 2025/2026+ is a
block-level artefact — the block exists but is null. There is no
possession covariate either (`BallPossesion` absent), so even the
corners Gate Zero pattern has no inputs. The builder stores
`corners_*` and `BallPossesion_*` columns as None in every row
(`data/fnl_matches.csv`) to record the absence in-schema.

There is no dev window with a target, no primary line, and no virgin
window containing the target. If FotMob ever backfills stats for this
league, the candidate can be re-registered with a fresh prereg and a
fresh virgin window.
