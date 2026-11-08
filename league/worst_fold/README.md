# P6 — Worst-fold dev reporting tool

Implements proposal P6 of `league/AUDIT.md` §6, adopted in
`league/IMPROVEMENT_PROGRAM.md`.

## Design

Every verdict reports the **worst dev season's legs beside the pooled
legs** — information only, **no gate change**. One season of the
existing per-season sign check, generalised: the fold is defined by
the reference arm (Gate Zero) at the primary metric, and every arm
and baseline is then reported on that same fold next to its pooled
numbers, so a pooled margin that rests on one easy season is visible
at verdict time.

## Usage

```bash
# from the repo root, project python
.venv/bin/python -m league.worst_fold.worst_fold league/<L> <market> [--line 9.5] [--json out.json]
.venv/bin/python -m league.worst_fold.worst_fold league/<L>/engine/<market>/results_dev.json
```

`<market>` is the engine directory name (`goals`, `sot`, `corners`,
`cards`, `total_shots`). The primary metric is LL at the primary line
(`protocol.primary_line` when persisted, else `--line`, else the
prereg's primary line, else the middle ladder line); for goals it is
the 1X2 LL. Pooled values are taken from the artefact when persisted,
otherwise computed as the n-weighted mean of the per-season LLs and
labelled as computed.

## Coverage

The completed program persisted `results_dev.json` in many shapes.
The extractor normalises the common ones (arm/baseline blocks with
`pooled` + `seasons`, nested series-per-season blocks, row lists,
`metrics` blocks, `logloss`-by-line cells, `primary_ll` rows). A sweep
over all 428 persisted dev artefacts in the tree: **373 (87%) are
extractable today**; the rest use one-off layouts. For NEW builds the
artefact shape should follow one of the supported layouts (the
arm/baseline `pooled` + `seasons` shape is the recommended one), and
then the block is a single command at verdict time.

## Gate Zero

P6 has **no statistical Gate Zero** — it changes no gate and no
verdict, so there is nothing to replay. It is adoptable independently,
and this tool is ready for the coordinator to mandate in the
improvement program's verdict format: append the emitted block to
every verdict, next to the pooled legs.
