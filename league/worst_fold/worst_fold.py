"""P6 worst-fold dev reporting (AUDIT.md section 6, proposal P6).

Design: every verdict reports the WORST DEV SEASON's legs beside the
pooled legs — information only, NO gate change. This tool reads a
league's persisted dev artefacts (engine/<market>/results_dev.json)
and emits the verdict-format block.

The completed program persisted results_dev.json in several shapes;
this extractor normalises the common ones:

  A. {"arms": {arm: {"pooled": {...}, "seasons": {season: {...}}}},
      "baselines": {name: {same}}}          (e.g. AE-ProLeague SOT)
  B. {"arms": {arm: {"seasons": {season: {series: {line: {"ll": ...}}}}}}}
                                             (e.g. AE-ProLeague cards)
  C. [ {"arm": ..., "kind": ..., "season": ..., "ll_<line>": ..., "n": ...} ]
                                             (e.g. J1 goals, AT corners)
  D. {"rows": [ ...same row shape as C... ]} and other dicts holding a
     row list under a 'rows'/'results' key.

Metrics: for counting markets the primary metric is LL at the primary
line (protocol.primary_line if persisted, else --line, else the line
named in the league's prereg, else the middle ladder line). For goals
the primary metric is the 1X2 LL (ll_1x2 / ll), with OU2.5 LL and RPS
reported too when present.

Pooled values are taken from the artefact when persisted; otherwise
they are computed as the n-weighted mean of the per-season LLs and
labelled "(n-weighted, computed)". Worst season = the dev season with
the highest LL for that entity at the primary metric (higher LL is
worse). Baselines are reported on the model's worst season, so the
block answers: in the model's worst fold, did it still beat the
baselines it is gated against?

Usage:
  .venv/bin/python -m league.worst_fold.worst_fold league/AE-ProLeague/engine/sot/results_dev.json
  .venv/bin/python -m league.worst_fold.worst_fold league/J1 goals
  .venv/bin/python -m league.worst_fold.worst_fold league/AT-Bundesliga corners --line 9.5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEASON_KEY_RE = re.compile(r"^\d{4}(?:[/\- ]\d{2,4})?(?:\s*-\s*\w+)?$")
LL_KEY_RE = re.compile(r"^ll(?:_(.+))?$", re.IGNORECASE)


# --------------------------------------------------------------------------
# Extraction: artefact -> {entity: {"seasons": {season: {metric: (ll, n)}},
#                                   "pooled": {metric: ll}}}
# --------------------------------------------------------------------------

def _season_items(d: dict):
    return [(k, v) for k, v in d.items() if SEASON_KEY_RE.match(str(k)) and isinstance(v, dict)]


def _metrics_from_flat(d: dict):
    """{ll_9.5: v, ll: v, rps: v, oull_2_5: v, n: ...} -> {metric: ll}."""
    out = {}
    for k, v in d.items():
        if isinstance(v, dict) and str(k).lower() in ("logloss", "log_loss", "ll_by_line"):
            for line, ll in v.items():
                if isinstance(ll, (int, float)):
                    out[f"ll_{line}"] = float(ll)
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            lk = str(k).lower()
            if lk in ("primary_ll", "ll_primary"):
                out["ll"] = float(v)
            elif LL_KEY_RE.match(lk) or lk in ("rps", "oull_2_5", "ou_ll", "ll_1x2"):
                out[str(k)] = float(v)
    return out


def _metrics_from_nested_series(season_dict: dict):
    """{series: {line: {ll: v, n: v}}} -> {series: {metric: (ll, n)}}."""
    out = {}
    for series, lines in season_dict.items():
        if not isinstance(lines, dict):
            continue
        m = {}
        for line, cell in lines.items():
            if isinstance(cell, dict) and isinstance(cell.get("ll"), (int, float)):
                m[f"ll_{line}"] = (float(cell["ll"]), cell.get("n"))
        if m:
            out[str(series)] = m
    return out


def _add_entity(store: dict, name: str, seasons: dict, pooled: dict | None):
    ent = store.setdefault(name, {"seasons": {}, "pooled": {}})
    for season, metrics in seasons.items():
        ent["seasons"].setdefault(str(season), {}).update(metrics)
    if pooled:
        ent["pooled"].update(pooled)


def _entity_from_arm_block(store: dict, name: str, block: dict):
    if not isinstance(block, dict):
        return
    pooled = {}
    if isinstance(block.get("pooled"), dict):
        pooled = {m: v for m, v in _metrics_from_flat(block["pooled"]).items()}
    seasons_node = block.get("seasons") if isinstance(block.get("seasons"), dict) else block
    s_items = _season_items(seasons_node)
    if not s_items:
        return
    # Shape B check: season -> series -> line -> {ll}
    first = s_items[0][1]
    nested = _metrics_from_nested_series(first) if first else {}
    if nested and not _metrics_from_flat(first):
        for season, sdict in s_items:
            per_series = _metrics_from_nested_series(sdict)
            n_season = sdict.get("n")
            for series, metrics in per_series.items():
                ent_name = name if series == "model" else f"{name} [{series}]"
                seasons_map = {str(season): {m: (ll, n if n is not None else n_season)
                                             for m, (ll, n) in metrics.items()}}
                _add_entity(store, ent_name, seasons_map, None)
        return
    seasons_map = {}
    for season, sdict in s_items:
        n = sdict.get("n")
        seasons_map[str(season)] = {m: (v, n) for m, v in _metrics_from_flat(sdict).items()}
    _add_entity(store, name, seasons_map, pooled)


def _entities_from_rows(store: dict, rows: list):
    for row in rows:
        if not isinstance(row, dict) or "season" not in row:
            continue
        season = str(row["season"])
        if season.lower() in ("pooled", "all", "dev", "total"):
            continue
        arm = str(row.get("arm", "model"))
        kind = row.get("kind")
        entity = arm if kind in (None, "model") else str(kind)
        if kind not in (None, "model") and arm not in ("model", "gate_zero", "Gate Zero", "GZ"):
            entity = f"{arm} [{kind}]"
        metrics = {m: (v, row.get("n")) for m, v in _metrics_from_flat(row).items()}
        # Nested per-line dicts in a row: {"9.5": {"ll": ...}, ...}
        for k, v in row.items():
            if isinstance(v, dict) and isinstance(v.get("ll"), (int, float)):
                metrics[f"ll_{k}"] = (float(v["ll"]), v.get("n", row.get("n")))
        if metrics:
            _add_entity(store, entity, {season: metrics}, None)


def extract_entities(data) -> dict:
    store: dict = {}
    if isinstance(data, list):
        _entities_from_rows(store, data)
        return store
    if not isinstance(data, dict):
        return store
    for container_key in ("arms", "baselines"):
        node = data.get(container_key)
        if isinstance(node, dict):
            for name, block in node.items():
                label = name if container_key == "arms" else f"baseline: {name}"
                _entity_from_arm_block(store, label, block)
    if store:
        return store
    for key in ("rows", "results", "dev", "per_season", "metrics"):
        node = data.get(key)
        if isinstance(node, list):
            _entities_from_rows(store, node)
            if store:
                return store
        elif isinstance(node, dict):
            for name, block in node.items():
                if isinstance(block, dict):
                    label = f"baseline: {name}" if name.startswith("baseline") else str(name)
                    _entity_from_arm_block(store, label, block)
            if store:
                return store
    # Last resort: any arm-like top-level block with season-keyed children.
    for name, block in data.items():
        if isinstance(block, dict) and name not in ("protocol", "fitted_params", "tuning"):
            _entity_from_arm_block(store, str(name), block)
    return store


# --------------------------------------------------------------------------
# Block construction
# --------------------------------------------------------------------------

def primary_metric(entities: dict, protocol, line: str | None) -> str | None:
    if not isinstance(protocol, dict):
        protocol = {}
    metrics = set()
    for ent in entities.values():
        for season_metrics in ent["seasons"].values():
            metrics.update(season_metrics)
        metrics.update(ent["pooled"])
    if not metrics:
        return None
    if any(m.lower() == "ll_1x2" for m in metrics):
        return next(m for m in metrics if m.lower() == "ll_1x2")
    ll_lines = sorted((m for m in metrics if LL_KEY_RE.match(m) and m.lower() != "ll"),
                      key=lambda m: float(LL_KEY_RE.match(m).group(1)) if LL_KEY_RE.match(m).group(1) else 0)
    if line is not None:
        want = f"ll_{line}"
        if want in metrics:
            return want
    pl = (protocol or {}).get("primary_line")
    if pl is not None and f"ll_{pl}" in metrics:
        return f"ll_{pl}"
    if ll_lines:
        return ll_lines[len(ll_lines) // 2]
    if "ll" in metrics:
        return "ll"
    return sorted(metrics)[0]


def _pooled_ll(ent: dict, metric: str):
    if metric in ent["pooled"]:
        return ent["pooled"][metric], "persisted"
    num = den = 0.0
    for metrics in ent["seasons"].values():
        if metric in metrics:
            ll, n = metrics[metric]
            if n:
                num += ll * n
                den += n
    if den:
        return num / den, "n-weighted, computed"
    vals = [m[metric][0] for m in ent["seasons"].values() if metric in m]
    return (sum(vals) / len(vals), "mean of seasons, computed") if vals else (None, "")


def _fmt(v):
    return f"{v:.4f}" if isinstance(v, (int, float)) else "—"


def _dedupe(entities: dict) -> dict:
    """Drop entities whose per-season + pooled numbers are identical to an
    earlier entity (row-shape artefacts repeat each arm's baselines under
    every arm; the duplicates carry no information)."""
    seen, out = [], {}
    for name, ent in entities.items():
        signature = json.dumps(
            {"s": {s: {m: ll for m, (ll, n) in ms.items()} for s, ms in sorted(ent["seasons"].items())},
             "p": ent["pooled"]}, sort_keys=True)
        if signature in seen:
            continue
        seen.append(signature)
        out[name] = ent
    return out


def build_block(league_label: str, market_label: str, entities: dict,
                protocol: dict, line: str | None, source: str) -> str:
    entities = _dedupe(entities)
    metric = primary_metric(entities, protocol, line)
    if metric is None:
        return (f"### P6 worst-fold block — {league_label} {market_label}\n\n"
                f"No per-season dev LLs could be extracted from {source}.\n")
    # Worst season is defined on the reference arm (Gate Zero) when it is
    # present — the fold where the gated arm struggled most — else on the
    # worst model entity overall. Baselines never define the fold.
    model_entities = {k: v for k, v in entities.items() if not k.startswith("baseline:")}
    reference = next((k for k in model_entities
                      if k.lower().replace(" ", "_") in ("gate_zero", "gz", "gatezero")), None)
    worst_season, worst_val = None, None
    pool = {reference: model_entities[reference]} if reference else model_entities
    for ent in pool.values():
        for season, metrics in ent["seasons"].items():
            if metric in metrics and (worst_val is None or metrics[metric][0] > worst_val):
                worst_season, worst_val = season, metrics[metric][0]
    lines = [
        f"### P6 worst-fold block — {league_label} {market_label} (primary metric: {metric})",
        "",
        f"Source: `{source}` (persisted dev artefacts; information only — no gate change).",
        f"Worst dev season (highest {metric} for the reference arm): **{worst_season}**.",
        "",
        f"| Entity | Pooled {metric} | Pooled source | Worst-season ({worst_season}) {metric} | n (worst) | Δ vs pooled |",
        "|---|---|---|---|---|---|",
    ]
    for name in sorted(entities, key=lambda k: (k.startswith("baseline:"), k)):
        ent = entities[name]
        pooled, psrc = _pooled_ll(ent, metric)
        w = ent["seasons"].get(worst_season, {}).get(metric)
        w_ll, w_n = (w[0], w[1]) if w else (None, None)
        delta = (w_ll - pooled) if (w_ll is not None and pooled is not None) else None
        lines.append(f"| {name} | {_fmt(pooled)} | {psrc} | {_fmt(w_ll)} | "
                     f"{w_n if w_n is not None else '—'} | {format(delta, '+.4f') if delta is not None else '—'} |")
    lines += ["", "Per-season legs for every entity are in the machine-readable output of the tool "
              "(`--json`). Reading: the worst-season column is the model's hardest dev fold; "
              "compare it against the baselines' worst-season values on the same fold before "
              "trusting the pooled margin."]
    return "\n".join(lines)


def load_dev_artefact(path: Path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    protocol = data.get("protocol", {}) if isinstance(data, dict) else {}
    return data, protocol


def prereg_primary_line(league_dir: Path, market: str) -> str | None:
    for f in sorted((league_dir / "prereg").glob("*.md")) if (league_dir / "prereg").is_dir() else []:
        if market and market[0].upper() not in f.name.upper():
            continue
        m = re.search(r"[Pp]rimary line[^0-9]*(\d+\.\d+)", f.read_text(encoding="utf-8", errors="replace"))
        if m:
            return m.group(1)
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", help="league dir (with market) or a results_dev.json path")
    ap.add_argument("market", nargs="?", default=None, help="goals|sot|corners|cards|total_shots")
    ap.add_argument("--line", default=None, help="primary line override, e.g. 9.5")
    ap.add_argument("--json", default=None, help="also write machine-readable extraction here")
    args = ap.parse_args(argv)

    target = Path(args.target)
    if target.is_file():
        dev_path = target
        league_label = target.parents[2].name if len(target.parents) > 2 else target.stem
        market_label = target.parents[0].name if target.parents else ""
        league_dir = target.parents[2] if len(target.parents) > 2 else target.parent
    else:
        league_dir = target
        market_label = args.market or ""
        dev_path = league_dir / "engine" / market_label / "results_dev.json"
        league_label = league_dir.name
    if not dev_path.exists():
        print(f"no persisted dev artefact at {dev_path}")
        return 1
    data, protocol = load_dev_artefact(dev_path)
    entities = extract_entities(data)
    if not entities:
        print(f"could not extract per-season dev LLs from {dev_path}")
        return 1
    line = args.line or (None if protocol.get("primary_line") is not None
                         else prereg_primary_line(league_dir, market_label))
    block = build_block(league_label, market_label, entities, protocol, line, str(dev_path))
    print(block)
    if args.json:
        entities = _dedupe(entities)
        serial = {name: {"pooled": ent["pooled"],
                         "seasons": {s: {m: ll for m, (ll, n) in ms.items()}
                                     for s, ms in ent["seasons"].items()}}
                  for name, ent in entities.items()}
        Path(args.json).write_text(json.dumps(
            {"league": league_label, "market": market_label, "source": str(dev_path),
             "primary_metric": primary_metric(entities, protocol, line),
             "entities": serial}, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
