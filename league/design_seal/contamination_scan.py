"""P2 contamination scanner — audit existing analysis/ artefacts for sealed data.

For every league directory under league/ (one with a config.yaml), the
scanner takes the sealed season(s) from the league's own prereg partition
(config virgin_primary / virgin_confirmatory / virgin) and inspects every
artefact under that league's analysis/ directory:

  JSON_KEY    a JSON artefact has a mapping key equal to a sealed season
              (a per-season aggregate table that includes the sealed season)
  JSON_VALUE  a JSON string value equal to a sealed season
  MD_ROW      a Markdown table row naming a sealed season (a printed
              sealed-season level in an EDA table)
  MD_MENTION  any other Markdown line naming a sealed season
  CSV_ROW     a CSV row in analysis/ naming a sealed season
  PY_REF      generator code under analysis/ naming a sealed season
              literally (most generators iterate a SEASONS list instead;
              those are caught through their JSON/MD outputs, not here)

Classification per league:
  DATA       at least one of JSON_KEY / MD_ROW / CSV_ROW — sealed-season
             aggregates are present in builder-facing artefacts
  MENTION    only MD_MENTION / JSON_VALUE / PY_REF — the sealed season is
             named but no aggregate row for it was found by this scanner
  CLEAN      no reference at all
  NO_SEAL    config defines no sealed season (nothing to scan against)

This measures the OLD program's contamination (AUDIT.md section 4b: EDA
was fit-sealed but not design-sealed). It changes nothing on disk except
its own outputs.

Usage:
  .venv/bin/python -m league.design_seal.contamination_scan \
      [--league-root league] [--out-json PATH] [--out-md PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from seal import find_sealed_references, load_seal, text_mentions_sealed
else:
    from .seal import find_sealed_references, load_seal, text_mentions_sealed

DATA_KINDS = {"JSON_KEY", "MD_ROW", "CSV_ROW"}
TEXT_SUFFIXES = {".md", ".txt", ".py", ".csv", ".json"}


def scan_league(league_dir: Path) -> dict:
    seal = load_seal(league_dir)
    rec = {
        "league": seal.league,
        "sealed_seasons": seal.sealed_seasons,
        "dev_seasons": seal.dev_seasons,
        "hits": [],
        "classification": "CLEAN",
    }
    if not seal.sealed_seasons:
        rec["classification"] = "NO_SEAL"
        return rec
    analysis = league_dir / "analysis"
    if not analysis.is_dir():
        rec["classification"] = "NO_ANALYSIS"
        return rec
    for f in sorted(p for p in analysis.rglob("*") if p.is_file()):
        rel = str(f.relative_to(league_dir))
        suffix = f.suffix.lower()
        if suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if suffix == ".json":
            try:
                obj = json.loads(text)
            except json.JSONDecodeError:
                obj = None
            if obj is not None:
                for path, season, kind in find_sealed_references(obj, seal):
                    rec["hits"].append({
                        "file": rel, "kind": "JSON_KEY" if kind == "key" else "JSON_VALUE",
                        "season": season, "detail": path,
                    })
                continue  # JSON handled structurally; skip raw-text pass
        for season, lineno, line in text_mentions_sealed(text, seal):
            if suffix == ".md":
                kind = "MD_ROW" if line.startswith("|") else "MD_MENTION"
            elif suffix == ".csv":
                kind = "CSV_ROW"
            elif suffix == ".py":
                kind = "PY_REF"
            else:
                kind = "MD_MENTION"
            rec["hits"].append({
                "file": rel, "kind": kind, "season": season,
                "detail": f"line {lineno}: {line[:160]}",
            })
    kinds = {h["kind"] for h in rec["hits"]}
    if kinds & DATA_KINDS:
        rec["classification"] = "DATA"
    elif kinds:
        rec["classification"] = "MENTION"
    return rec


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--league-root", default="league")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--out-md", default=None)
    args = ap.parse_args(argv)

    root = Path(args.league_root)
    league_dirs = sorted(d for d in root.iterdir() if d.is_dir() and (d / "config.yaml").exists())
    records = [scan_league(d) for d in league_dirs]

    from collections import Counter
    census = Counter(r["classification"] for r in records)
    print(f"leagues scanned: {len(records)}")
    for cls in ("DATA", "MENTION", "CLEAN", "NO_SEAL", "NO_ANALYSIS"):
        print(f"  {cls}: {census.get(cls, 0)}")
    data_leagues = [r["league"] for r in records if r["classification"] == "DATA"]
    print("DATA leagues:", ", ".join(data_leagues))

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(
            {"census": dict(census), "n_scanned": len(records), "records": records},
            indent=1), encoding="utf-8")
        print(f"wrote {args.out_json}")
    if args.out_md:
        lines = ["# P2 contamination census — existing analysis/ artefacts vs each league's sealed season(s)", "",
                 f"Leagues scanned: {len(records)}. Classification counts: "
                 + ", ".join(f"{k}={census.get(k, 0)}" for k in ('DATA', 'MENTION', 'CLEAN', 'NO_SEAL', 'NO_ANALYSIS')) + ".",
                 "", "DATA = a sealed-season aggregate row/key is present in a builder-facing artefact. "
                 "MENTION = sealed season named, no aggregate row found. This is a census of the old "
                 "program (AUDIT.md §4b); nothing was modified.", ""]
        for cls in ("DATA", "MENTION"):
            rs = [r for r in records if r["classification"] == cls]
            lines.append(f"## {cls} ({len(rs)})")
            lines.append("")
            for r in rs:
                kinds = Counter(h["kind"] for h in r["hits"])
                lines.append(f"- **{r['league']}** (sealed: {', '.join(r['sealed_seasons'])}): "
                             + ", ".join(f"{k}×{v}" for k, v in sorted(kinds.items())))
            lines.append("")
        clean = [r["league"] for r in records if r["classification"] in ("CLEAN", "NO_SEAL", "NO_ANALYSIS")]
        lines.append(f"## No DATA/MENTION hit ({len(clean)})")
        lines.append("")
        lines.append(", ".join(clean))
        lines.append("")
        Path(args.out_md).write_text("\n".join(lines), encoding="utf-8")
        print(f"wrote {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
