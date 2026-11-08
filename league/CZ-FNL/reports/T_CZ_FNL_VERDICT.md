# Verdict — T-CZ-FNL (CZ-FNL total shots)

**NOT BUILDABLE — no prereg, no fitting, virgin NOT read.**

The candidate fails the template's feasibility condition: the target
must exist in the data. It does not exist in any era of this league's
feed — a stronger absence than the CZ-Liga / RO-LigaI counting break,
where the series at least existed and changed definition. Here there
is no series at all.

Payload evidence (all 1,311 FNL matches, every season 2021/2022–
2026/2027): `content.stats` is `{"Periods": {"All": null}}` in every
file, and the string `total_shots` occurs in zero sampled rich-era
files. The shotmap is empty in every match, so total shots cannot be
reconstructed from shots either. The builder stores `total_shots_*`
columns as None in every row (`data/fnl_matches.csv`) to record the
absence in-schema. (For contrast, the sibling CZ-Liga build faced a
dev≈17.5 → virgin 25.5 counting break; FNL has no dev-era level to
break from.)

There is no dev window with a target, no primary line, and no virgin
window containing the target. If FotMob ever backfills stats for this
league, the candidate can be re-registered with a fresh prereg and a
fresh virgin window.
