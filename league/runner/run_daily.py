"""One idempotent, config-driven daily FotMob league run."""
from __future__ import annotations

import ast
import csv
import importlib.util
import inspect
import json
import math
import os
import sys
import tempfile
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data_enrichment"))
sys.path.insert(0, str(ROOT / "league"))

from pull_fotmob_jleague import (HEADERS, INDEX, LEAGUES, SEASON_PARAMS, STORE,
                                  fetch_one, flags_of, get, load_index,
                                  score_of, season_dir, write_index)
import pull_fotmob_world as world_pull

RUNNER = ROOT / "league" / "runner"
RUN_LOG = RUNNER / "run_log.jsonl"


def _canonical_team_name(name):
    return "".join(ch for ch in unicodedata.normalize("NFKD", name)
                   if not unicodedata.combining(ch))


def _scalar(value):
    value = value.strip()
    if not value:
        return {}
    if value.startswith("[") and value.endswith("]"):
        return [_scalar(x) for x in value[1:-1].split(",") if x.strip()]
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        return value


def _strip_comment(line):
    quoted = False
    out = []
    for ch in line:
        if ch == '"':
            quoted = not quoted
        if ch == "#" and not quoted:
            break
        out.append(ch)
    return "".join(out).rstrip()


def read_yaml_subset(path):
    """Parse the runner's nested-map/scalar-list YAML subset without PyYAML."""
    root = {}
    stack = [(-1, root)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = _strip_comment(raw)
        if not line.strip() or line.lstrip().startswith("-"):
            raise ValueError("active.yaml supports maps and scalar lists only")
        indent = len(line) - len(line.lstrip(" "))
        key, sep, value = line.strip().partition(":")
        if not sep:
            raise ValueError(f"invalid YAML line: {raw}")
        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        if value.strip():
            parent[key] = _scalar(value)
        else:
            parent[key] = {}
            stack.append((indent, parent[key]))
    return root


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def log_step(league, step, counts=None, market=None):
    counts = counts or {}
    row = {"ts": datetime.now(timezone.utc).isoformat(), "league": league,
           "step": step, "market": market, "fetched_new": counts.get("fetched_new", 0),
           "fixtures_upcoming": counts.get("fixtures_upcoming", 0),
           "predicted": counts.get("predicted", 0), "settled": counts.get("settled", 0),
           "errors": counts.get("errors", [])}
    with RUN_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def pull_and_fixtures(name, cfg):
    import httpx
    from stealth import proxy_url
    league_id = int(cfg["fotmob_id"])
    ccode = cfg["ccode"]
    by_id, current = {}, []
    errors = []
    with httpx.Client(headers=HEADERS, timeout=60, follow_redirects=True, proxy=proxy_url()) as client:
        for param in cfg["seasons"]:
            try:
                payload = get(client, "leagues", {"id": league_id, "ccode3": ccode, "season": param}, 0.0)
                canonical = str((payload.get("details") or {}).get("selectedSeason") or param)
                fixtures = ((payload.get("fixtures") or {}).get("allMatches") or [])
                if fixtures:
                    current = (canonical, fixtures)
                for fixture in fixtures:
                    status = fixture.get("status") or {}
                    if status.get("finished") and not status.get("cancelled"):
                        mid = int(fixture["id"])
                        if mid not in by_id:
                            by_id[mid] = {"match_id": mid, "league": name, "season": canonical,
                                          "date": str(status.get("utcTime") or "")[:10],
                                          "home": (fixture.get("home") or {}).get("name") or "",
                                          "away": (fixture.get("away") or {}).get("name") or "",
                                          "score": score_of(fixture, None)}
            except Exception as exc:
                errors.append(f"season {param}: {exc!r}")
    index = load_index()
    missing = [x for x in by_id.values() if not (STORE / name / season_dir(x["season"]) / f"{x['match_id']}.json").exists()]
    fetched = 0
    outcomes = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(fetch_one, item, 0.0) for item in missing]
        for future in as_completed(futures):
            outcome = future.result(); outcomes.append(outcome)
            if outcome.get("origin") == "http": fetched += 1
            if "error" in outcome or "provider_stop" in outcome:
                errors.append(f"match {outcome['item']['match_id']}: {outcome.get('error', outcome.get('provider_stop'))}")
            else:
                item = outcome["item"]
                index[str(item["match_id"])] = {"match_id": item["match_id"], "league": name,
                    "season": item["season"], "date": item["date"], "home": item["home"],
                    "away": item["away"], "score": outcome["score"], **flags_of({})}
                index[str(item["match_id"])].update({k: outcome[k] for k in ("has_shotmap", "has_stats", "has_lineup", "has_period_splits")})
                index[str(item["match_id"])] ["path"] = str(Path("data_enrichment") / "fotmob_jleague" / name / season_dir(item["season"]) / f"{item['match_id']}.json")
    if missing or index:
        write_index(index)
    upcoming = []
    if current:
        _, fixtures = current
        for f in fixtures:
            s = f.get("status") or {}
            if not s.get("finished") and not s.get("cancelled"):
                upcoming.append({"match_id": int(f["id"]), "date": str(s.get("utcTime") or "")[:10],
                    "home": (f.get("home") or {}).get("name") or "", "away": (f.get("away") or {}).get("name") or "",
                    "home_id": (f.get("home") or {}).get("id"), "away_id": (f.get("away") or {}).get("id")})
    log_step(name, "pull_fixtures", {"fetched_new": fetched, "fixtures_upcoming": len(upcoming), "errors": errors})
    return upcoming, errors


def pull_and_fixtures_world(name, cfg):
    import httpx
    from stealth import proxy_url
    league_id = int(cfg["fotmob_id"])
    ccode = cfg["ccode"]
    country = cfg["country"]
    league = cfg["world_league"]
    by_id, current = {}, []
    errors = []
    with httpx.Client(headers=world_pull.HEADERS, timeout=60, follow_redirects=True,
                      proxy=proxy_url()) as client:
        for param in cfg["seasons"]:
            try:
                payload = world_pull.get(client, "leagues", {"id": league_id,
                    "ccode3": ccode, "season": param}, 0.0)
                canonical = str((payload.get("details") or {}).get("selectedSeason") or param)
                fixtures = ((payload.get("fixtures") or {}).get("allMatches") or [])
                if fixtures:
                    current = (canonical, fixtures)
                for fixture in fixtures:
                    status = fixture.get("status") or {}
                    if status.get("finished") and not status.get("cancelled"):
                        mid = int(fixture["id"])
                        if mid not in by_id:
                            by_id[mid] = {"match_id": mid, "country": country,
                                "ccode": ccode, "league": league, "league_id": str(league_id),
                                "season": canonical, "date": str(status.get("utcTime") or "")[:10],
                                "home": (fixture.get("home") or {}).get("name") or "",
                                "away": (fixture.get("away") or {}).get("name") or "",
                                "score": world_pull.score_of(fixture, None)}
            except Exception as exc:
                errors.append(f"season {param}: {exc!r}")
    missing = [x for x in by_id.values() if not (world_pull.STORE /
        world_pull.sanitize(x["country"]) / world_pull.sanitize(x["league"]) /
        world_pull.season_dir(x["season"]) / f"{x['match_id']}.json").exists()]
    fetched = 0
    index = world_pull.load_index()
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(world_pull.fetch_one, item, 0.0) for item in missing]
        for future in as_completed(futures):
            outcome = future.result()
            if outcome.get("origin") == "http": fetched += 1
            if "error" in outcome or "provider_stop" in outcome:
                errors.append(f"match {outcome['item']['match_id']}: "
                             f"{outcome.get('error', outcome.get('provider_stop'))}")
                continue
            item = outcome["item"]
            index[str(item["match_id"])] = {
                "match_id": item["match_id"], "country": item["country"],
                "ccode": item["ccode"], "league": item["league"],
                "league_id": item["league_id"], "season": item["season"],
                "date": item["date"], "home": item["home"], "away": item["away"],
                "score": outcome["score"], "has_shotmap": outcome["has_shotmap"],
                "has_stats": outcome["has_stats"], "has_lineup": outcome["has_lineup"],
                "has_period_splits": outcome["has_period_splits"],
                "path": str(Path("data_enrichment") / "fotmob_world" /
                    world_pull.sanitize(item["country"]) / world_pull.sanitize(item["league"]) /
                    world_pull.season_dir(item["season"]) / f"{item['match_id']}.json")}
    if missing or index:
        world_pull.write_index(index)
    upcoming = []
    if current:
        _, fixtures = current
        for f in fixtures:
            status = f.get("status") or {}
            if not status.get("finished") and not status.get("cancelled"):
                upcoming.append({"match_id": int(f["id"]), "date": str(status.get("utcTime") or "")[:10],
                    "home": (f.get("home") or {}).get("name") or "", "away": (f.get("away") or {}).get("name") or "",
                    "home_id": (f.get("home") or {}).get("id"), "away_id": (f.get("away") or {}).get("id"),
                    # The pull's fixture dicts carry `round` ("1".."34"
                    # regular; "Promotion Play-offs - ..." for playoffs,
                    # verified on SA-FirstDivision 2025/2026) — carried
                    # so a market can opt into regular-rounds-only
                    # prediction; no other consumer reads it.
                    "round": f.get("round")})
    log_step(name, "pull_fixtures", {"fetched_new": fetched,
        "fixtures_upcoming": len(upcoming), "errors": errors})
    return upcoming, errors


def rebuild_csv(name, cfg):
    from build_league_data import parse_match, team_rows
    warehouse = ROOT / cfg["warehouse"] / name
    rows = []
    seen = set()
    for sdir in sorted(p for p in warehouse.iterdir() if p.is_dir()):
        for path in sorted(sdir.glob("*.json")):
            row = parse_match(name, sdir.name, path)
            if row["match_id"] in seen: raise ValueError(f"duplicate match id {row['match_id']}")
            seen.add(row["match_id"]); rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out = ROOT / cfg["data"]["matches"]; out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    trows = [x for row in rows for x in team_rows(row)]
    tout = ROOT / cfg["data"]["team_matches"]
    with tout.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(trows[0])); writer.writeheader(); writer.writerows(trows)
    return out, rows


def rebuild_csv_world(name, cfg):
    builder = Path(cfg.get("data_builder", f"league/{name}/data/build_data.py"))
    mod = import_from(str(builder.parent), builder.name, f"daily_{name}_builder")
    mod.INDEX = ROOT / "data_enrichment" / "fotmob_world_index.csv"
    mod.MAIN_REPO = ROOT
    mod.main()
    out = ROOT / cfg["data"]["matches"]
    # SOT engines read the match's league column as their division key
    # (every SOT loader does div = r["league"]); DK-1Division's builder
    # omits the column, so its SOT adapter would raise KeyError. Append
    # it (the league name) when absent, only for leagues that run SOT;
    # builders that already write the column are untouched, and the file
    # is not rewritten at all when the column is present.
    if "sot" in cfg.get("markets", {}):
        with out.open(encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            fieldnames = reader.fieldnames or []
            rows = list(reader)
        if "league" not in fieldnames:
            fieldnames = fieldnames + ["league"]
            for r in rows:
                r["league"] = name
            with out.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=fieldnames)
                w.writeheader()
                w.writerows(rows)
    with out.open(encoding="utf-8", newline="") as fh:
        return out, list(csv.DictReader(fh))


def import_from(directory, filename, module):
    spec = importlib.util.spec_from_file_location(module, ROOT / directory / filename)
    mod = importlib.util.module_from_spec(spec); sys.modules[module] = mod; spec.loader.exec_module(mod); return mod


def predict_sot(cfg, upcoming, run_date):
    market = cfg["markets"]["sot"]
    model = import_from(market["engine_dir"], "model.py", "daily_sot_model")
    # Opt-in column remap + phase exclusion (default inert, mirroring the
    # corners `columns` / `exclude_phases` precedents): AU-ALeagueWomen's
    # builder writes home_-prefixed stat columns (home_total_shots,
    # home_ShotsOnTarget) and no `league` column, so the frozen engine's
    # load_matches silently loads ZERO rows from it (every row fails its
    # total_shots_home/ShotsOnTarget_home presence check). When `columns`
    # is set, the CSV is rewritten through the mapping into a temp file
    # (standard name -> the CSV's actual name, the corners direction) and
    # the market div is injected as `league` when that column is absent,
    # so the engine reads exactly the frozen harness's rows; with
    # team_key: id the team-name columns are swapped for the team ids,
    # exactly as the frozen harness keys its rows. `exclude_phases` drops
    # non-regular rows (the frozen harness is regular-only). Leagues
    # without either key read their CSV exactly as before.
    columns = market.get("columns", {})
    exclude_phases = set(market.get("exclude_phases", ()))
    # Opt-in per-league season allowlist (default inert, mirroring the
    # ratio_prior signature-check pattern below): SA-FirstDivision's
    # SOT loader is load_matches(path, seasons) — seasons is a
    # REQUIRED positional — so the stock one-argument call would raise
    # TypeError. When the market carries a `seasons` list AND the
    # loader's signature accepts a second positional, pass it; leagues
    # without the key, and loaders that take only one argument, call
    # exactly as before. SA passes ["2025/2026", "2026/2027"] only:
    # score-only 2024/2025 (empty stat fields) would crash the
    # loader's bare float(r[k]).
    load_seasons = None
    if market.get("seasons") is not None:
        params = list(inspect.signature(model.load_matches).parameters.values())
        if len(params) >= 2 and params[1].kind in (inspect.Parameter.POSITIONAL_ONLY,
                                                    inspect.Parameter.POSITIONAL_OR_KEYWORD):
            load_seasons = set(market["seasons"])
    src_path = ROOT / cfg["data"]["matches"]
    if columns or exclude_phases:
        raw = list(csv.DictReader(src_path.open(encoding="utf-8", newline="")))
        header = list(raw[0]) if raw else []
        for src in columns.values():
            if src not in header:
                raise ValueError(f"sot columns mapping: {src!r} not in {src_path}")
        rename = {actual: expected for expected, actual in columns.items()}
        fields = [rename.get(c, c) for c in header]
        if "league" not in fields:
            fields.append("league")
        rows_norm = []
        for r in raw:
            if r.get("phase") in exclude_phases:
                continue
            out = {rename.get(k, k): v for k, v in r.items()}
            if "league" not in out:
                out["league"] = market.get("div", "J1")
            if market.get("team_key") == "id":
                out["home_team"] = r["home_team_id"]
                out["away_team"] = r["away_team_id"]
            rows_norm.append(out)
        tmp = tempfile.NamedTemporaryFile("w", newline="", encoding="utf-8",
                                          suffix=".csv", delete=False)
        try:
            with tmp:
                w = csv.DictWriter(tmp, fieldnames=fields)
                w.writeheader(); w.writerows(rows_norm)
            matches = (model.load_matches(tmp.name, load_seasons) if load_seasons is not None
                       else model.load_matches(tmp.name))
        finally:
            os.unlink(tmp.name)
    else:
        matches = (model.load_matches(src_path, load_seasons) if load_seasons is not None
                   else model.load_matches(src_path))
    # Opt-in per-league season exclusion (default inert, mirroring the
    # corners/total-shots-C precedent): CN-SuperLeague's frozen SOT
    # harness fits on 2023+ only (2021/2022 are excluded eras), so its
    # market config excludes those seasons. Leagues without the key
    # load every season exactly as before.
    exclude_seasons = set(market.get("exclude_seasons", ()))
    if exclude_seasons:
        matches = [m for m in matches if str(m["season"]) not in exclude_seasons]
    # Opt-in canonical team names (CZ-Liga): strip diacritics (NFKD) from
    # history team names, so a club whose 2026/2027 spelling carries
    # diacritics keys onto the same ASCII history as its gated eras.
    # Leagues without team_key: canonical_name are untouched; the
    # canonicalisation is the identity on every gated-era CZ name.
    if market.get("team_key") == "canonical_name":
        for match in matches:
            match["home"] = _canonical_team_name(match["home"])
            match["away"] = _canonical_team_name(match["away"])
    # Opt-in id-keyed history (DK-1Division): its SOT loader keys history
    # on team names, but three FotMob ids carry two spellings inside the
    # fit window (9814 Horsens/AC Horsens, 8487 Sønderjyske/SønderjyskE,
    # 8470 Aalborg BK/AaB), so name-keyed history splits those teams and
    # does not reproduce the frozen id-keyed harness. When a market opts
    # into team_key: id and its loader keyed history on names, remap the
    # names to ids from the match CSV (a name that maps to more than one
    # id is left alone); loaders that already key on ids are untouched,
    # and the existing fixture-key cast below then keys fixtures on ints.
    if market.get("team_key") == "id" and matches and isinstance(matches[0]["home"], str):
        name_to_id, ambiguous = {}, set()
        for r in csv.DictReader((ROOT / cfg["data"]["matches"]).open(encoding="utf-8")):
            for id_col, name_col in (("home_team_id", "home_team"), ("away_team_id", "away_team")):
                if not r.get(name_col) or not r.get(id_col):
                    continue
                prev = name_to_id.get(r[name_col])
                if prev is None:
                    name_to_id[r[name_col]] = int(r[id_col])
                elif prev != int(r[id_col]):
                    ambiguous.add(r[name_col])
        for n in ambiguous:
            name_to_id.pop(n, None)
        for m in matches:
            if m["home"] in name_to_id:
                m["home"] = name_to_id[m["home"]]
            if m["away"] in name_to_id:
                m["away"] = name_to_id[m["away"]]
    # Some SOT engines take the runner's ratio_prior argument (the
    # keyword-only form), others fix the prior inside the engine
    # (DK-1Division's Engine takes only matches and arm, defaulting to
    # the frozen 200.0 for non-RS arms); pass the argument only when the
    # engine accepts it, mirroring the goals adapter's call-each-engine-
    # as-it-is-written rule. Leagues whose engines accept the argument
    # are unchanged.
    if "ratio_prior" in inspect.signature(model.Engine).parameters:
        eng = model.Engine(matches, market["arm"], ratio_prior=float(market.get("ratio_prior", 200)))
    else:
        eng = model.Engine(matches, market["arm"])
    for m in matches: eng.update(m)
    # FT-only presentation for leagues whose feed has no period splits
    # (first SOT user: BG-FirstLeague; the identical opt-in landed with
    # the CZ-Liga join); settlement reads only FT fields, so it is
    # unaffected.
    ft_only = "halves_share_1h" in market and market["halves_share_1h"] in (None, "null")
    share = None if ft_only else market["halves_share_1h"]
    rows = []
    for f in upcoming:
        # Opt-in regular-rounds-only (SA-FirstDivision): the frozen
        # harness excludes playoffs (phase != regular), but the pull
        # returns whatever FotMob lists as upcoming, including the
        # promotion playoffs (~May 2027). The pull's fixture dicts
        # carry `round` ("1".."34" regular; "Promotion Play-offs -
        # Semi-finals"/"Final" for playoffs, verified on the completed
        # 2025/2026 payload), so when the market opts in, skip a
        # fixture whose round is not a plain round number. A fixture
        # with no round info passes through (hand-built/synthetic
        # fixtures carry none), and leagues without the key are
        # unchanged.
        if market.get("regular_rounds_only") and f.get("round") is not None \
                and not str(f["round"]).isdigit():
            continue
        # Most SOT engines key team state on the team name (their
        # load_matches "home" field); ES-LaLiga2's keys on the FotMob
        # team_id instead (its load_matches "home" is home_team_id, and
        # 10 of its 42 ids carry two name spellings). A market may opt in
        # with team_key: id; absent the key the name is passed, exactly
        # as before, so existing leagues are unchanged.
        if market.get("team_key") == "id":
            # ES-LaLiga2's engine keys on the id as a string (its
            # load_matches "home" is the CSV's home_team_id text);
            # CN-SuperLeague's keys on the id as an int (its
            # load_matches casts home_team_id to int, because CSL clubs
            # rename across seasons). Cast the fixture ids to the type
            # the loaded history actually uses; string-keyed leagues
            # are unchanged.
            if matches and isinstance(matches[0]["home"], int):
                home_key, away_key = int(f["home_id"]), int(f["away_id"])
            else:
                home_key, away_key = str(f["home_id"]), str(f["away_id"])
        elif market.get("team_key") == "canonical_name":
            home_key, away_key = _canonical_team_name(f["home"]), _canonical_team_name(f["away"])
        else:
            home_key, away_key = f["home"], f["away"]
        m = {"match_id": str(f["match_id"]), "date": date.fromisoformat(f["date"]), "day": date.fromisoformat(f["date"]).toordinal(), "div": market.get("div", "J1"), "home": home_key, "away": away_key}
        pred = eng.predict(m); total = pred["exp_h"] + pred["exp_a"]
        out = {"market": "sot", "arm": market["arm"], "match_id": f["match_id"], "date": f["date"], "home_team": f["home"], "away_team": f["away"], "exp_total": total, "exp_1h": "" if ft_only else share * total, "exp_2h": "" if ft_only else (1 - share) * total}
        out.update({f"p_over_{L}": pred["probs"][L] for L in market["ladder"]})
        out.update({f"p_1h_over_{L}": "" if ft_only else model.nb_over(share * total, model.NB_R, L) for L in market.get("ladder_1h", (2.5, 3.5, 4.5))})
        out.update({f"p_2h_over_{L}": "" if ft_only else model.nb_over((1 - share) * total, model.NB_R, L) for L in market.get("ladder_2h", (3.5, 4.5, 5.5))})
        rows.append(out)
    return rows


def predict_goals(cfg, upcoming):
    market = cfg["markets"]["goals"]
    if market["arm"] not in ("gate_zero", "x3", "shrink"):
        raise ValueError(f"unknown goals arm: {market['arm']}")
    dc = import_from(market["engine_dir"], "dc.py", "daily_goals_dc")
    arms = import_from(market["engine_dir"], "arms.py", "daily_goals_arms")
    raw = list(csv.DictReader((ROOT / cfg["data"]["matches"]).open(encoding="utf-8")))
    # BA-PremierLeague is scores-only: its builder writes no
    # expected_goals_* columns, so the xG reads below use .get() (None
    # degrades to the goals-only observation exactly as the engines do
    # when xgh/xga are None). Leagues carrying the columns are
    # unchanged: .get() returns the same value. The same league opts
    # into exclude_awarded: its frozen prereg excludes the 4 awarded
    # matches from every fit, and its harness drops them in load();
    # the runner must do the same or the live fit would include
    # 3-0/0-3 scorelines that do not reflect play. Other goals leagues
    # (SCO, TR, KZ) do not opt in — their harnesses never excluded
    # awarded rows — so their fits are unchanged.
    exclude_awarded = bool(market.get("exclude_awarded", False))
    # TZ-PremierLeague opts into team_key: name — its frozen prereg keys
    # teams by name because FotMob ids are shared across club renames
    # (1396530 = Singida Big Stars / Fountain Gate FC; 1171766 = Ihefu
    # FC / Singida Black Stars), and the SHRINK arm's bite depends on
    # the renames NOT being merged. Keying history or fixtures by id
    # would silently change the gated method. Leagues without the key
    # key by id exactly as before.
    by_name = market.get("team_key") == "name"

    def num(value):
        return None if value in ("", None) else float(value)

    games = []
    for r in raw:
        if exclude_awarded and str(r.get("awarded", "")).strip().lower() in ("true", "1", "yes"):
            continue
        games.append({"match_id": str(r["match_id"]), "season": r["season"],
                      "date": date.fromisoformat(r["date"]),
                      "hi": r["home_team"] if by_name else int(r["home_team_id"]),
                      "ai": r["away_team"] if by_name else int(r["away_team_id"]),
                      "home": r["home_team"],
                      "away": r["away_team"], "yh": int(r["home_goals"]),
                      "ya": int(r["away_goals"]), "xgh": num(r.get("expected_goals_home")),
                      "xga": num(r.get("expected_goals_away")),
                      "oph": num(r.get("expected_goals_open_play_home")),
                      "opa": num(r.get("expected_goals_open_play_away")),
                      "sph": num(r.get("expected_goals_set_play_home")),
                      "spa": num(r.get("expected_goals_set_play_away"))})
    games.sort(key=lambda g: (g["date"], g["match_id"]))

    groups = {}
    for f in upcoming:
        groups.setdefault(date.fromisoformat(f["date"]), []).append(f)
    rows = []
    share = float(market["halves_share_1h"])
    # Some scores-only engines (KZ-PremierLeague) define
    # adjusted_lambdas(model, home, away, arm, counts) — five parameters,
    # no movers/multipliers — which neither call form below fits. Detect
    # that exact shape once and call it as written; every other engine
    # takes the existing path unchanged.
    _params = inspect.signature(arms.adjusted_lambdas).parameters
    five_arg_counts = (list(_params) == ["model", "home", "away", "arm", "counts"]
                       and _params["counts"].default is inspect.Parameter.empty)
    for cutoff in sorted(groups):
        group = sorted(groups[cutoff], key=lambda f: int(f["match_id"]))
        train = [g for g in games if g["date"] < cutoff]
        model = dc.DC().fit(train, cutoff)
        # Arm X3 layers the frozen set-play multipliers over the SHRINK
        # adjustment; Gate Zero keeps the empty multiplier map. Some
        # engines take the shrink counts as an argument (match_counts),
        # others read them from the fitted model (team_counts) and take
        # no counts argument — call each engine as it is written.
        multipliers = arms.x3_multipliers(train, cutoff) if market["arm"] == "x3" else {}
        counts = arms.match_counts(train) if hasattr(arms, "match_counts") else None
        for f in group:
            hi, ai = (f["home"], f["away"]) if by_name else (int(f["home_id"]), int(f["away_id"]))
            if five_arg_counts:
                lh, la = arms.adjusted_lambdas(model, hi, ai, market["arm"], counts)
            elif counts is None:
                lh, la = arms.adjusted_lambdas(model, hi, ai, market["arm"], set(), multipliers)
            else:
                lh, la = arms.adjusted_lambdas(model, hi, ai, market["arm"], set(), multipliers, counts)
            p = model.probs(lh, la)
            total = lh + la
            out = {"market": "goals", "arm": market["arm"], "match_id": int(f["match_id"]),
                   "date": f["date"], "home_team": f["home"], "away_team": f["away"],
                   "exp_total": total, "exp_1h": share * total,
                   "exp_2h": (1 - share) * total, "lambda_home": lh,
                   "lambda_away": la, "p_home": p["ph"], "p_draw": p["pd"],
                   "p_away": p["pa"], "p_btts": p["btts"]}
            out.update({f"p_over_{line}": model.over(lh, la, line) for line in market["ladder"]})
            out.update({f"p_1h_over_{line}": model.over(lh * share, la * share, line)
                        for line in market.get("ladder_1h", (0.5, 1.5, 2.5))})
            out.update({f"p_2h_over_{line}": model.over(lh * (1 - share), la * (1 - share), line)
                        for line in market.get("ladder_2h", (1.5, 2.5, 3.5))})
            rows.append(out)
    return rows


def _cards_history_rows(cfg, raw, include_referee=False):
    market = cfg["markets"]["cards"]
    # Referee identity is attached ONLY for the x8 arm. Several
    # gate_zero engines carry dormant referee branches that activate the
    # moment a row has a referee (KR-KLeague1's update() then requires
    # row["kickoff_utc"], which the runner never supplied) — attaching
    # it unconditionally breaks them, so gate_zero rows stay exactly as
    # before (no referee/key keys at all).
    # CN-SuperLeague's builder writes no yellow_home/yellow_away alias:
    # its frozen stats-feed target lives directly under
    # yellow_cards_home/yellow_cards_away (also the runner's settlement
    # default for cards). Fall back to those columns only when the
    # alias is absent from the CSV header, so leagues whose builders
    # write the alias are unchanged. A market may also opt into
    # exclude_seasons (CN's frozen cards harness fits on 2023+ only);
    # absent the key every season loads exactly as before.
    header = raw[0] if raw else {}
    ycol_h = "yellow_home" if "yellow_home" in header else "yellow_cards_home"
    ycol_a = "yellow_away" if "yellow_away" in header else "yellow_cards_away"
    # Opt-in frozen target (DK-1Division): its frozen cards target is the
    # stats feed's yellow+red, but its builder's yellow_home alias is
    # yellow only, so the default path would fit and grade the wrong
    # target. When a market opts into cards_target: yellow_plus_red,
    # read yellow_cards+red_cards on both sides instead; leagues without
    # the key are unchanged.
    ypr = market.get("cards_target") == "yellow_plus_red"
    ypr_cols = ("yellow_cards_home", "red_cards_home", "yellow_cards_away", "red_cards_away")
    # Opt-in frozen target (CO-PrimeraA): its frozen cards target is the
    # event-unified yellows (Yellow = 1, YellowRed = 1 additional), which
    # its builder writes under ev_yellow_inc2nd_home/away; the default
    # alias path would fit the stats feed, whose 2021-2022 level the
    # frozen prereg rejected. When a market opts into
    # cards_target: event_unified_yellows, read those columns instead;
    # leagues without the key are unchanged.
    eu = market.get("cards_target") == "event_unified_yellows"
    eu_cols = ("ev_yellow_inc2nd_home", "ev_yellow_inc2nd_away")
    exclude_seasons = set(cfg["markets"]["cards"].get("exclude_seasons", ()))
    # Opt-in excluded-row drop (FO-PremierLeague): its frozen cards
    # harness drops the builder's excluded=1 row (the awarded match)
    # from every pass. When a market opts into exclude_excluded, those
    # rows never enter the history; leagues without the key, and CSVs
    # without an excluded column, are unchanged.
    exclude_excluded = bool(market.get("exclude_excluded", False))
    # Opt-in per-league phase exclusion (default inert, mirroring the
    # corners precedent): ID-SuperLeague's frozen cards harness loads
    # only `regular` rows — its builder flags the 2023/2024 championship
    # series and a two-legged AFC playoff — so its market config
    # excludes those phases. Leagues without the key are unchanged,
    # including ones whose CSVs carry no phase column at all.
    exclude_phases = set(market.get("exclude_phases", ()))
    rows_hist = []
    for r in raw:
        if r["season"] in exclude_seasons:
            continue
        if exclude_excluded and str(r.get("excluded", "")).strip() == "1":
            continue
        if r.get("phase") in exclude_phases:
            continue
        if eu:
            if any(r.get(c, "") in ("", None) for c in eu_cols):
                continue
            yh, ya = int(float(r[eu_cols[0]])), int(float(r[eu_cols[1]]))
        elif ypr:
            if any(r.get(c, "") in ("", None) for c in ypr_cols):
                continue
            yh = int(float(r["yellow_cards_home"])) + int(float(r["red_cards_home"]))
            ya = int(float(r["yellow_cards_away"])) + int(float(r["red_cards_away"]))
        else:
            if r.get(ycol_h, "") in ("", None) or r.get(ycol_a, "") in ("", None):
                continue
            yh, ya = int(float(r[ycol_h])), int(float(r[ycol_a]))
        d = date.fromisoformat(r["date"])
        home_id = r.get("home_team_id") or r.get("home_id")
        away_id = r.get("away_team_id") or r.get("away_id")
        home = r.get("home_team") or r.get("home_name") or r.get("home")
        away = r.get("away_team") or r.get("away_name") or r.get("away")
        # kickoff_utc (date at 00:00Z, the frozen harness's own key
        # construction) rides along for x8 engines whose referee state
        # is keyed by it (CO-PrimeraA's J1-mechanics port); engines
        # keyed by "key" (AR-PrimeraBNacional) never read it.
        extra = {"referee": r.get("referee", ""), "key": (r["date"], r["match_id"]),
                 "kickoff_utc": r["date"] + "T00:00:00Z"} if include_referee else {}
        rows_hist.append({"match_id": r["match_id"], "date": r["date"], "day": d.toordinal(),
            "home_id": int(home_id), "away_id": int(away_id), "home": home, "away": away,
            "yh": yh, "ya": ya, "y": yh + ya, **extra})
    rows_hist.sort(key=lambda x: (x["date"], x["match_id"]))
    return rows_hist


def _cards_referees(upcoming):
    import httpx
    from stealth import proxy_url
    referees, failed = {}, []
    with httpx.Client(headers=world_pull.HEADERS, timeout=60, follow_redirects=True, proxy=proxy_url()) as client:
        for fixture in upcoming:
            mid = int(fixture["match_id"])
            if fixture.get("referee"):
                referees[mid] = str(fixture["referee"]).strip()
                continue
            try:
                payload = world_pull.get(client, "matchDetails", {"matchId": mid}, 0.0)
                box = (((payload.get("content") or {}).get("matchFacts") or {}).get("infoBox") or {})
                referees[mid] = str((box.get("Referee") or {}).get("text") or "").strip()
            except Exception:
                referees[mid] = ""
                failed.append(mid)
    if failed:
        print(f"warning: cards referee fetch failed for match ids: {', '.join(map(str, failed))}")
    return referees


def predict_cards(cfg, upcoming):
    market = cfg["markets"]["cards"]
    arm = market["arm"]
    if arm not in ("gate_zero", "x8", "shrink", "x5"):
        raise ValueError(f"unknown cards arm: {arm}")
    model = import_from(market["engine_dir"], "model.py", "daily_cards_model")
    raw = list(csv.DictReader((ROOT / cfg["data"]["matches"]).open(encoding="utf-8")))
    rows_hist = _cards_history_rows(cfg, raw, include_referee=(arm == "x8"))
    referee_map = _cards_referees(upcoming) if arm == "x8" else {}
    # FO-PremierLeague's frozen cards engine (the J1-seed harness
    # family) differs from the runner's usual cards interface in two
    # ways: its Online takes the shrinkage prior as a constructor
    # argument (Gate Zero K=8, SHRINK K=16), and its prediction entry
    # point is predict(row), not prediction(row, arm). Dispatch on
    # the engine's own signature/shape: engines whose Online takes
    # no constructor argument and that expose prediction(row, arm)
    # — every cards league already served — take exactly the old
    # path. The extra date/match_id keys on the prediction row below
    # are the keys FO's predict() uses for its causality assertion;
    # the other engines ignore them.
    if len(inspect.signature(model.Online.__init__).parameters) > 1:
        online = model.Online({"gate_zero": 8, "shrink": 16, "x8": 8}[arm])
    else:
        online = model.Online()
    def _predict(online, row):
        if hasattr(online, "prediction"):
            return online.prediction(row, arm)
        return online.predict(row)
    records = []
    for row in rows_hist:
        p = _predict(online, row)
        records.append({"y": row["y"], "model": p["model"], "base": p["base"], "naive": p["naive"]})
        online.update(row)
    if hasattr(model, "estimate_r"):
        r_model = model.estimate_r(records, "model")
        def nb_over(mu, line):
            return model.nb_over(mu, r_model, line)
    else:
        r_model = model.R
        def nb_over(mu, line):
            return model.nb_over(mu, line)
    share = market["halves_share_1h"]
    rows = []
    for f in sorted(upcoming, key=lambda x: (x["date"], x["match_id"])):
        d = date.fromisoformat(f["date"])
        prediction_row = {"home_id": int(f["home_id"]), "away_id": int(f["away_id"]), "day": d.toordinal(),
                          "date": f["date"], "match_id": str(f["match_id"])}
        if arm == "x8":
            prediction_row["referee"] = referee_map.get(int(f["match_id"]), "")
            # Same kickoff key the history rows carry, for x8 engines
            # whose referee prior is filtered strictly before kickoff
            # by timestamp (CO-PrimeraA); key-based engines ignore it.
            prediction_row["kickoff_utc"] = f["date"] + "T00:00:00Z"
        p = _predict(online, prediction_row)
        # X5 (ID-SuperLeague, Lane 1 L1-K-ID): the shipped arm blends
        # the model mean with the naive trailing-10 mean, scored with
        # the model's r exactly as in its frozen harness. Other arms
        # use the model mean unchanged.
        mu = 0.5 * p["model"] + 0.5 * p["naive"] if arm == "x5" else p["model"]
        out = {"market": "cards", "arm": arm, "match_id": int(f["match_id"]), "date": f["date"],
               "home_team": f["home"], "away_team": f["away"], "exp_total": mu,
               "exp_1h": share * mu, "exp_2h": (1 - share) * mu}
        out.update({f"p_over_{L}": nb_over(mu, L) for L in market["ladder"]})
        out.update({f"p_1h_over_{L}": nb_over(share * mu, L) for L in market.get("ladder_1h", (0.5, 1.5, 2.5))})
        out.update({f"p_2h_over_{L}": nb_over((1 - share) * mu, L) for L in market.get("ladder_2h", (1.5, 2.5, 3.5))})
        if arm == "x8":
            referee = prediction_row["referee"]
            # Engines report the referee state under ref_prior/ref_factor
            # (AR-PrimeraBNacional) or n_prior/multiplier (CO-PrimeraA's
            # J1-mechanics port); read whichever spelling the engine
            # ships, preferring the original one.
            n_prior = p.get("ref_prior", p.get("n_prior", 0))
            ref_factor = p.get("ref_factor", p.get("multiplier", 1.0))
            out.update({"referee": referee, "n_prior": n_prior, "multiplier": ref_factor,
                        "fallback": bool(not referee or n_prior < 8),
                        "fallback_reason": "unknown_identity" if not referee else ("thin_history" if n_prior < 8 else "")})
        rows.append(out)
    return rows


def predict_corners(cfg, upcoming):
    core = import_from(cfg["markets"]["corners"]["engine_dir"], "core.py", "daily_corners_core")
    market = cfg["markets"]["corners"]
    # HU-NBI's builder writes _h/_a names, which the frozen engine's
    # core.load reads; the runner's adapter reads the standard names,
    # so it maps them instead of renaming the feed.
    columns = market.get("columns", {})
    def column(name):
        return columns.get(name, name)
    corners_home = column("corners_home")
    corners_away = column("corners_away")
    total_shots_home = column("total_shots_home")
    total_shots_away = column("total_shots_away")
    home_team_id = column("home_team_id")
    away_team_id = column("away_team_id")
    possession_home = column("BallPossesion_home")
    possession_away = column("BallPossesion_away")
    big_chance_home = column("big_chance_home")
    big_chance_away = column("big_chance_away")
    touches_opp_box_home = column("touches_opp_box_home")
    touches_opp_box_away = column("touches_opp_box_away")
    path = ROOT / cfg["data"]["matches"]
    raw = list(csv.DictReader(path.open(encoding="utf-8")))
    unified = market.get("shots_target") == "unified"
    # Opt-in per-league season exclusion (default inert, mirroring the
    # total-shots arm-C precedent): IE-PremierDivision's frozen corners
    # harness loads only 2022+ — its 2021 corners exist in just 35 of 180
    # matches and its core.load cannot parse the empty rows — so its
    # market config excludes "2021". Leagues without the key are unchanged.
    exclude_seasons = set(market.get("exclude_seasons", ()))
    # Opt-in per-league phase exclusion (default inert, mirroring the
    # exclude_seasons precedent): US-USLLeagueOne's frozen phase rule
    # excludes playoff rows from every fitting/scoring window — its
    # core.load drops non-regular rows — so its market config excludes
    # "playoff". Leagues without the key are unchanged, including ones
    # whose CSVs carry no phase column at all (r.get("phase") is None).
    exclude_phases = set(market.get("exclude_phases", ()))
    # PE-Liga1 opts into the engine's unified shots and regular/non-awarded history.
    good = (raw if unified else [r for r in raw if r.get(corners_home, "") not in ("", None) and r.get(corners_away, "") not in ("", None)])
    good = [r for r in good if r.get("phase") not in exclude_phases]
    seasons = {r["block"] for r in good} if unified else {r["season"] for r in good}
    # Adapt core.load's small row shape in memory so incomplete corner rows
    # are dropped before its int(float(...)) conversions. The num helper
    # mirrors core.load's missing-value rule, including the "nan" string some
    # builders write instead of an empty field. Possession falls back to the
    # lower-case spelling: CO-PrimeraA's builder lower-cases every stat key
    # (its own core.load reads "ballpossesion_home"), while the other
    # builders keep FotMob's "BallPossesion" — the fallback only engages
    # when the capitalised column is absent, so existing leagues are
    # unchanged.
    def num(v):
        if v in ("", None, "nan", "NaN"):
            return None
        x = float(v)
        return None if math.isnan(x) else x
    rows_hist = []
    for r in good:
        if unified and (r.get("phase") != "regular" or r.get("awarded") != "0"):
            continue
        season = r["block"] if unified else r["season"]
        if season in exclude_seasons:
            continue
        if season not in seasons:
            continue
        ch = None if r.get(corners_home, "") in ("", None) else int(float(r[corners_home]))
        ca = None if r.get(corners_away, "") in ("", None) else int(float(r[corners_away]))
        if unified:
            sh = (num(r.get("shotsontarget_home")) + num(r.get("shotsofftarget_home"))
                  if r.get("has_rich_stats") == "1" and num(r.get("shotsofftarget_home")) is not None
                  else num(r.get(total_shots_home)))
            sa = (num(r.get("shotsontarget_away")) + num(r.get("shotsofftarget_away"))
                  if r.get("has_rich_stats") == "1" and num(r.get("shotsofftarget_away")) is not None
                  else num(r.get(total_shots_away)))
        else:
            sh, sa = num(r.get(total_shots_home)), num(r.get(total_shots_away))
        rows_hist.append({"match_id": r["match_id"], "season": season, "date": date.fromisoformat(r["date"]),
            "home_id": r[home_team_id], "away_id": r[away_team_id], "home": r["home_team"], "away": r["away_team"],
            "ch": ch, "ca": ca, "sh": sh, "sa": sa,
            "poss_h": num(r.get(possession_home, r.get("ballpossesion_home"))), "poss_a": num(r.get(possession_away, r.get("ballpossesion_away"))), "bc_h": num(r.get(big_chance_home)), "bc_a": num(r.get(big_chance_away)),
            "bt_h": num(r.get(touches_opp_box_home)), "bt_a": num(r.get(touches_opp_box_away))})
    rows_hist.sort(key=lambda r: (r["date"], r["match_id"]))
    feat_hist = core.FeatureBuilder(rows_hist).build()
    arm = market["arm"]
    # X5 is the trailing-rate blend defined in the league's own harness
    # (DK-1Division run_c_dk1.py): mu = 0.5*mu_GZ + 0.5*naive trailing-10
    # total, with Gate Zero's r. The engine core does not implement x5,
    # so the adapter fits Gate Zero's params and blends here; every other
    # arm takes the core's own fit/predict path exactly as before.
    params = core.fit_params([r for r in feat_hist if r["prior_n"] >= 10], "gate_zero" if arm == "x5" else arm)
    # FT-only presentation for leagues whose feed has no period splits
    # (RU-1Division); settlement reads only FT fields, so it is unaffected.
    ft_only = "halves_share_1h" in market and market["halves_share_1h"] in (None, "null")
    share = None if ft_only else market["halves_share_1h"]
    ladder = market["ladder"]
    fixture_rows = [{"match_id": str(f["match_id"]), "season": "current", "date": date.fromisoformat(f["date"]), "home_id": str(f.get("home_id") or ""), "away_id": str(f.get("away_id") or ""), "home": f["home"], "away": f["away"], "ch": 0, "ca": 0, "sh": None, "sa": None, "poss_h": None, "poss_a": None, "bc_h": None, "bc_a": None, "bt_h": None, "bt_a": None} for f in upcoming]
    rows = []
    by_date = {}
    for frow in fixture_rows: by_date.setdefault(frow["date"], []).append(frow)
    for d, group in sorted(by_date.items()):
        feats = core.FeatureBuilder(rows_hist + group).build()
        if arm == "x5":
            # attach_naive is date-grouped like every other state in
            # this engine, so same-date fixtures never see each other.
            feats = core.attach_naive(feats)
        wanted = {x["match_id"] for x in group}
        for row in feats:
            if row["match_id"] not in wanted: continue
            if arm == "x5":
                mu_gz, r = core.model_prediction(row, params, "gate_zero")
                mu = 0.5 * mu_gz + 0.5 * (row["naive_home"] + row["naive_away"]) / 2.0
            else:
                mu, r = core.model_prediction(row, params, arm)
            f = next(x for x in group if x["match_id"] == row["match_id"])
            out = {"market": "corners", "arm": arm, "match_id": int(f["match_id"]), "date": f["date"].isoformat(), "home_team": f["home"], "away_team": f["away"], "exp_total": mu, "exp_1h": "" if ft_only else share * mu, "exp_2h": "" if ft_only else (1 - share) * mu}
            out.update({f"p_over_{L}": core.over_prob(mu, r, L) for L in ladder})
            out.update({f"p_1h_over_{L}": "" if ft_only else core.over_prob(share * mu, r, L) for L in market.get("ladder_1h", (3.5, 4.5, 5.5))})
            out.update({f"p_2h_over_{L}": "" if ft_only else core.over_prob((1 - share) * mu, r, L) for L in market.get("ladder_2h", (4.5, 5.5, 6.5))})
            rows.append(out)
    return rows


def predict_total_shots(cfg, upcoming):
    market = cfg["markets"]["total_shots"]
    # FT-only presentation is for leagues with no period splits
    # (BG-FirstLeague is the first total-shots user); settlement remains FT-only.
    ft_only = "halves_share_1h" in market and market["halves_share_1h"] in (None, "null")
    arm = market["arm"]
    if arm == "C":
        return predict_total_shots_arm_c(cfg, upcoming)
    if arm == "B":
        return predict_total_shots_arm_b(cfg, upcoming)
    if arm == "x5":
        return predict_total_shots_arm_x5(cfg, upcoming)
    if arm != "A":
        raise ValueError(f"unknown total_shots arm: {arm}")
    model = import_from(market["engine_dir"], "model.py", "daily_ts_model")
    engine_dir = ROOT / market["engine_dir"]
    params = json.loads((engine_dir / "fitted_params.json").read_text(encoding="utf-8"))
    lam, r_a = params["lambda"], params["r_A"]
    ladder = tuple(params["ladder"])
    if ft_only:
        half_split = None
    elif "half_split" in params:
        half_split = tuple(params["half_split"])
    else:
        # CL-LigaDePrimera's frozen fitted_params.json carries no
        # half_split; its split is the market's frozen halves_share_1h
        # config. Every league whose fitted_params carries half_split,
        # and every FT-only league, is unchanged.
        share = float(market["halves_share_1h"])
        half_split = (share, 1.0 - share)
    raw = list(csv.DictReader((ROOT / cfg["data"]["matches"]).open(encoding="utf-8")))
    matches = []
    unified = cfg["markets"]["total_shots"].get("shots_target") == "unified"
    # PE-Liga1 opts into the engine's unified shots and regular/non-awarded history.
    for r in raw:
        if unified:
            if r.get("phase") != "regular" or r.get("awarded") != "0":
                continue
            shots_h = (float(r["shotsontarget_home"]) + float(r["shotsofftarget_home"])
                       if r.get("has_rich_stats") == "1" and r.get("shotsofftarget_home") != ""
                       else (float(r["total_shots_home"]) if r.get("total_shots_home") != "" else None))
            shots_a = (float(r["shotsontarget_away"]) + float(r["shotsofftarget_away"])
                       if r.get("has_rich_stats") == "1" and r.get("shotsofftarget_away") != ""
                       else (float(r["total_shots_away"]) if r.get("total_shots_away") != "" else None))
            if shots_h is None or shots_a is None:
                continue
        else:
            if r.get("total_shots_home", "") in ("", None) or r.get("total_shots_away", "") in ("", None):
                continue
            shots_h, shots_a = float(r["total_shots_home"]), float(r["total_shots_away"])
        d = date.fromisoformat(r["date"])
        matches.append({"match_id": str(r["match_id"]), "season": r["block"] if unified else r["season"], "date": r["date"],
                        "day": d.toordinal(), "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
                        "home": r["home_team"], "away": r["away_team"], "shots_h": shots_h,
                        "shots_a": shots_a})
    matches.sort(key=lambda x: (x["day"], int(x["match_id"])))
    reg = model.ShotsRegressionStore(matches, [lam])
    naive = model.NaiveTracker()
    for m in matches:
        naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
    rows = []
    for f in upcoming:
        day = date.fromisoformat(f["date"]).toordinal()
        home_id, away_id = int(f["home_id"]), int(f["away_id"])
        eh, ea = reg.predict(home_id, away_id, day, lam)
        lt = eh + ea
        rh, ra = reg.league_mu(day, lam)
        nh, na = naive.predict(home_id, away_id, rh, ra)
        ln = nh + na
        ens = (lt + ln) / 2.0
        exp_1h, exp_2h = ("", "") if ft_only else (half_split[0] * ens, half_split[1] * ens)
        out = {"market": "total_shots", "arm": "A", "match_id": f["match_id"], "date": f["date"],
               "home_team": f["home"], "away_team": f["away"], "exp_total": ens,
               "exp_1h": exp_1h, "exp_2h": exp_2h}
        out.update({f"p_over_{line}": 0.5 * model.nb_over(lt, r_a, line) + 0.5 * model.nb_over(ln, r_a, line)
                    for line in ladder})
        out.update({f"p_1h_over_{line}": "" if ft_only else model.nb_over(exp_1h, r_a, line) for line in market.get("ladder_1h", (10.5, 11.5, 12.5))})
        out.update({f"p_2h_over_{line}": "" if ft_only else model.nb_over(exp_2h, r_a, line) for line in market.get("ladder_2h", (12.5, 13.5, 14.5))})
        rows.append(out)
    return rows


def predict_total_shots_arm_x5(cfg, upcoming):
    # X5 is the trailing-rate blend defined in the league's own harness
    # (DK-1Division run_t_dk1.py): mu = 0.5*GZ total + 0.5*NaiveTracker
    # total, with the frozen NB r — a single NB on the blended mu, not
    # the arm-A 0.5/0.5 mixture of two NB probabilities. lambda and r come
    # from the league's fitted_params_virgin.json (there is no
    # fitted_params.json for this arm; the ladder lives in active.yaml).
    # The pointer walk mirrors arm C (strictly prior days only), minus
    # the base-rate/level/trailing-r layers X5 does not use.
    market = cfg["markets"]["total_shots"]
    ft_only = "halves_share_1h" in market and market["halves_share_1h"] in (None, "null")
    model = import_from(market["engine_dir"], "model.py", "daily_ts_model_x5")
    engine_dir = ROOT / market["engine_dir"]
    params = json.loads((engine_dir / "fitted_params_virgin.json").read_text(encoding="utf-8"))
    lam, r_a = params["lambda"], params["r"]
    ladder = tuple(market["ladder"])
    if ft_only:
        half_split = None
    elif "half_split" in params:
        half_split = tuple(params["half_split"])
    else:
        share = float(market["halves_share_1h"])
        half_split = (share, 1.0 - share)
    raw = list(csv.DictReader((ROOT / cfg["data"]["matches"]).open(encoding="utf-8")))
    matches = []
    for r in raw:
        if r.get("total_shots_home", "") in ("", None) or r.get("total_shots_away", "") in ("", None):
            continue
        d = date.fromisoformat(r["date"])
        matches.append({"match_id": str(r["match_id"]), "season": r["season"], "date": r["date"],
            "day": d.toordinal(), "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
            "home": r["home_team"], "away": r["away_team"], "shots_h": float(r["total_shots_home"]),
            "shots_a": float(r["total_shots_away"])})
    matches.sort(key=lambda x: (x["day"], int(x["match_id"])))
    reg = model.ShotsRegressionStore(matches, [lam])
    naive = model.NaiveTracker()
    fixture_dates = sorted({date.fromisoformat(f["date"]).toordinal() for f in upcoming})
    groups = {d: [] for d in fixture_dates}
    for f in upcoming:
        groups[date.fromisoformat(f["date"]).toordinal()].append(f)
    pointer = 0
    rows = []
    for day in fixture_dates:
        while pointer < len(matches) and matches[pointer]["day"] < day:
            m = matches[pointer]
            reg.predict(m["home_id"], m["away_id"], m["day"], lam)
            naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
            pointer += 1
        for f in groups[day]:
            hid, aid = int(f["home_id"]), int(f["away_id"])
            eh, ea = reg.predict(hid, aid, day, lam)
            lt = eh + ea
            rh, ra = reg.league_mu(day, lam)
            nh, na = naive.predict(hid, aid, rh, ra)
            mu = 0.5 * lt + 0.5 * (nh + na)
            exp_1h, exp_2h = ("", "") if ft_only else (half_split[0] * mu, half_split[1] * mu)
            out = {"market": "total_shots", "arm": "x5", "match_id": f["match_id"], "date": f["date"],
                   "home_team": f["home"], "away_team": f["away"], "exp_total": mu, "exp_1h": exp_1h, "exp_2h": exp_2h}
            out.update({f"p_over_{line}": model.nb_over(mu, r_a, line) for line in ladder})
            out.update({f"p_1h_over_{line}": "" if ft_only else model.nb_over(exp_1h, r_a, line) for line in market.get("ladder_1h", (10.5, 11.5, 12.5))})
            out.update({f"p_2h_over_{line}": "" if ft_only else model.nb_over(exp_2h, r_a, line) for line in market.get("ladder_2h", (12.5, 13.5, 14.5))})
            rows.append(out)
    return rows


def predict_total_shots_arm_c(cfg, upcoming):
    market = cfg["markets"]["total_shots"]
    ft_only = "halves_share_1h" in market and market["halves_share_1h"] in (None, "null")
    # Opt-in per-league season exclusion (default inert): GR-SuperLeague's
    # frozen T prereg excludes its 2021/2022 seed season from every fit
    # (that season's shots feed is a different measurement), and its
    # engine harness loads only the non-excluded seasons. Leagues whose
    # config does not set exclude_seasons are unchanged.
    exclude_seasons = set(market.get("exclude_seasons", ()))
    model = import_from(market["engine_dir"], "model.py", "daily_ts_model_c")
    engine_dir = ROOT / market["engine_dir"]
    params = json.loads((engine_dir / "fitted_params.json").read_text(encoding="utf-8"))
    lam, r_a = params["lambda"], params["r_A"]
    ladder = tuple(params["ladder"])
    if ft_only:
        half_split = None
    elif "half_split" in params:
        half_split = tuple(params["half_split"])
    else:
        # AE-ProLeague's frozen fitted_params.json carries no
        # half_split (the arm-A CL fallback, extended to arm C); its
        # split is the market's frozen halves_share_1h config. Every
        # league whose fitted_params carries half_split, and every
        # FT-only league, is unchanged.
        share = float(market["halves_share_1h"])
        half_split = (share, 1.0 - share)
    raw = list(csv.DictReader((ROOT / cfg["data"]["matches"]).open(encoding="utf-8")))
    matches = []
    for r in raw:
        if r["season"] in exclude_seasons:
            continue
        if r.get("total_shots_home", "") in ("", None) or r.get("total_shots_away", "") in ("", None):
            continue
        d = date.fromisoformat(r["date"])
        matches.append({"match_id": str(r["match_id"]), "season": r["season"], "date": r["date"],
            "day": d.toordinal(), "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
            "home": r["home_team"], "away": r["away_team"], "shots_h": float(r["total_shots_home"]),
            "shots_a": float(r["total_shots_away"])})
    matches.sort(key=lambda x: (x["day"], int(x["match_id"])))
    reg = model.ShotsRegressionStore(matches, [lam]); naive = model.NaiveTracker()
    base = model.BaseRateTracker(); layer = model.LevelLayer([tuple(params["level_cell"])])
    trailing = model.TrailingR(r_a, k=params.get("trailing_r_window", 200))
    fixture_dates = sorted({date.fromisoformat(f["date"]).toordinal() for f in upcoming})
    groups = {d: [] for d in fixture_dates}
    for f in upcoming: groups[date.fromisoformat(f["date"]).toordinal()].append(f)
    pointer = 0
    rows = []
    for day in fixture_dates:
        while pointer < len(matches) and matches[pointer]["day"] < day:
            m = matches[pointer]
            eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
            rh, ra = reg.league_mu(m["day"], lam)
            nh, na = naive.predict(m["home_id"], m["away_id"], rh, ra)
            ens = (eh + ea + nh + na) / 2.0
            naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
            base.update(m["day"], m["shots_h"], m["shots_a"])
            layer.update(0, m["day"], m["shots_h"] + m["shots_a"], ens)
            trailing.update(m["day"], m["shots_h"] + m["shots_a"])
            pointer += 1
        for f in groups[day]:
            d = day; hid, aid = int(f["home_id"]), int(f["away_id"])
            eh, ea = reg.predict(hid, aid, d, lam); lt = eh + ea
            rh, ra = reg.league_mu(d, lam); nh, na = naive.predict(hid, aid, rh, ra); ln = nh + na
            ens = (lt + ln) / 2.0; exp_1h, exp_2h = ("", "") if ft_only else (half_split[0] * ens, half_split[1] * ens)
            out = {"market": "total_shots", "arm": "C", "match_id": f["match_id"], "date": f["date"],
                "home_team": f["home"], "away_team": f["away"], "exp_total": ens, "exp_1h": exp_1h, "exp_2h": exp_2h}
            rc = trailing.value(d)
            out.update({f"p_over_{line}": 0.5 * model.nb_over(lt, rc, line) + 0.5 * model.nb_over(ln, rc, line) for line in ladder})
            out.update({f"p_1h_over_{line}": "" if ft_only else model.nb_over(exp_1h, rc, line) for line in market.get("ladder_1h", (10.5, 11.5, 12.5))})
            out.update({f"p_2h_over_{line}": "" if ft_only else model.nb_over(exp_2h, rc, line) for line in market.get("ladder_2h", (12.5, 13.5, 14.5))})
            rows.append(out)
    return rows


def predict_total_shots_arm_b(cfg, upcoming):
    market = cfg["markets"]["total_shots"]
    ft_only = "halves_share_1h" in market and market["halves_share_1h"] in (None, "null")
    model = import_from(market["engine_dir"], "model.py", "daily_ts_model_b")
    engine_dir = ROOT / market["engine_dir"]
    params = json.loads((engine_dir / "fitted_params.json").read_text(encoding="utf-8"))
    lam, r_a = params["lambda"], params["r_A"]
    ladder = tuple(params["ladder"])
    if ft_only:
        half_split = None
    elif "half_split" in params:
        half_split = tuple(params["half_split"])
    else:
        # CN-SuperLeague's frozen fitted_params.json carries no
        # half_split (the arm-A CL fallback, extended to arm B); its
        # split is the market's frozen halves_share_1h config. Every
        # league whose fitted_params carries half_split is unchanged.
        share = float(market["halves_share_1h"])
        half_split = (share, 1.0 - share)
    # Opt-in per-league season exclusion (default inert, as in arm C):
    # CN's frozen total-shots harness fits on 2023+ only.
    exclude_seasons = set(market.get("exclude_seasons", ()))
    # Opt-in per-league phase exclusion (default inert, mirroring the
    # exclude_seasons precedent): US-USLLeagueOne's frozen phase rule
    # excludes playoff rows from every fitting/scoring window — its
    # engine load drops non-regular rows — so its market config excludes
    # "playoff". Leagues without the key are unchanged.
    exclude_phases = set(market.get("exclude_phases", ()))
    raw = list(csv.DictReader((ROOT / cfg["data"]["matches"]).open(encoding="utf-8")))
    matches = []
    for r in raw:
        if r["season"] in exclude_seasons:
            continue
        if r.get("phase") in exclude_phases:
            continue
        if r.get("total_shots_home", "") in ("", None) or r.get("total_shots_away", "") in ("", None):
            continue
        d = date.fromisoformat(r["date"])
        matches.append({"match_id": str(r["match_id"]), "season": r["season"], "date": r["date"],
                        "day": d.toordinal(), "home_id": int(r["home_team_id"]), "away_id": int(r["away_team_id"]),
                        "home": r["home_team"], "away": r["away_team"], "shots_h": float(r["total_shots_home"]),
                        "shots_a": float(r["total_shots_away"])})
    matches.sort(key=lambda x: (x["day"], int(x["match_id"])))
    reg = model.ShotsRegressionStore(matches, [lam])
    naive = model.NaiveTracker()
    base = model.BaseRateTracker()
    layer = model.LevelLayer([tuple(params["level_cell"])])
    fixture_dates = sorted({date.fromisoformat(f["date"]).toordinal() for f in upcoming})
    groups = {d: [] for d in fixture_dates}
    for f in upcoming:
        groups[date.fromisoformat(f["date"]).toordinal()].append(f)
    pointer = 0
    rows = []
    for day in fixture_dates:
        while pointer < len(matches) and matches[pointer]["day"] < day:
            m = matches[pointer]
            eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], lam)
            rh, ra = reg.league_mu(m["day"], lam)
            nh, na = naive.predict(m["home_id"], m["away_id"], rh, ra)
            ens = (eh + ea + nh + na) / 2.0
            naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
            base.update(m["day"], m["shots_h"], m["shots_a"])
            layer.update(0, m["day"], m["shots_h"] + m["shots_a"], ens)
            pointer += 1
        for f in groups[day]:
            hid, aid = int(f["home_id"]), int(f["away_id"])
            eh, ea = reg.predict(hid, aid, day, lam); lt = eh + ea
            rh, ra = reg.league_mu(day, lam); nh, na = naive.predict(hid, aid, rh, ra); ln = nh + na
            ens = (lt + ln) / 2.0; factor = layer.factor(0, day); mu = ens * factor
            exp_1h, exp_2h = ("", "") if ft_only else (half_split[0] * mu, half_split[1] * mu)
            out = {"market": "total_shots", "arm": "B", "match_id": f["match_id"], "date": f["date"],
                   "home_team": f["home"], "away_team": f["away"], "exp_total": mu,
                   "exp_1h": exp_1h, "exp_2h": exp_2h}
            out.update({f"p_over_{line}": 0.5 * model.nb_over(lt * factor, r_a, line) +
                        0.5 * model.nb_over(ln * factor, r_a, line) for line in ladder})
            out.update({f"p_1h_over_{line}": "" if ft_only else model.nb_over(exp_1h, r_a, line)
                        for line in market.get("ladder_1h", (10.5, 11.5, 12.5))})
            out.update({f"p_2h_over_{line}": "" if ft_only else model.nb_over(exp_2h, r_a, line)
                        for line in market.get("ladder_2h", (12.5, 13.5, 14.5))})
            rows.append(out)
    return rows


def write_predictions(name, market, cfg, rows, run_date):
    pred_dir = ROOT / "league" / name / "predictions"; pred_dir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["market", "arm", "match_id", "date", "home_team", "away_team", "exp_total", "exp_1h", "exp_2h"]
    with (pred_dir / f"daily_{run_date}_{market}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(rows)
    ledger = pred_dir / "ledger.jsonl"; keys = set()
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if line.strip():
                x = json.loads(line); keys.add((x["market"], str(x["match_id"]), x["run_date"]))
    primary = cfg["markets"][market]["primary_line"]
    with ledger.open("a", encoding="utf-8") as fh:
        for r in rows:
            key = (market, str(r["match_id"]), run_date)
            if key in keys: continue
            ladder = cfg["markets"][market]["ladder"]
            entry = {"market": market, "arm": r["arm"], "match_id": r["match_id"], "date": r["date"], "home": r["home_team"], "away": r["away_team"], "exp_total": r["exp_total"], "p_over": {str(line): r[f"p_over_{line}"] for line in ladder}, "primary_line": primary, "p_over_primary": r[f"p_over_{primary}"], "run_date": run_date}
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def settle(name, market, cfg, rows, run_date):
    pred_dir = ROOT / "league" / name / "predictions"; sidecar = pred_dir / "settled_keys.json"
    settled = set(json.loads(sidecar.read_text()) if sidecar.exists() else [])
    csv_rows = {str(r["match_id"]): r for r in rows}; ledger = pred_dir / "ledger.jsonl"; added = []
    report = ROOT / "league" / name / "reports" / "grading_ledger.jsonl"; report.parent.mkdir(parents=True, exist_ok=True)
    actual_cols = {"goals": ("home_goals", "away_goals"),
                   "sot": ("ShotsOnTarget_home", "ShotsOnTarget_away"),
                   "corners": ("corners_home", "corners_away"),
                   "total_shots": ("total_shots_home", "total_shots_away"),
                   "cards": ("yellow_cards_home", "yellow_cards_away")}
    actual = actual_cols.get(market)
    if market == "cards":
        override = cfg["markets"][market].get("cards_actual")
        if override:
            actual = tuple(override)
    elif market == "corners":
        columns = cfg["markets"][market].get("columns", {})
        actual = tuple(columns.get(c, c) for c in actual)
    elif market == "sot":
        # AU-ALeagueWomen's builder writes home_ShotsOnTarget, so the
        # standard ShotsOnTarget_home actuals would resolve to the
        # lower-case fallback and settle nothing, ever. Honour the
        # market's `columns` mapping here exactly as the corners branch
        # does; leagues without the key are unchanged.
        columns = cfg["markets"][market].get("columns", {})
        actual = tuple(columns.get(c, c) for c in actual)
    if actual is not None and rows:
        # CO-PrimeraA's builder lower-cases every stat key, so its SOT
        # actuals live under "shotsontarget_home"/"shotsontarget_away".
        # Resolve each actual column to the lower-case spelling only when
        # the standard spelling is absent from the CSV header; leagues
        # whose builders keep the standard spelling are unchanged.
        header = rows[0]
        actual = tuple(c if c in header else c.lower() for c in actual)
    if actual is None:
        raise ValueError(f"unknown market: {market}")
    unified = market == "total_shots" and cfg["markets"][market].get("shots_target") == "unified"
    # PE-Liga1 opts into the engine's unified shots for settlement actuals.
    def unified_total(row):
        values = []
        for side in ("home", "away"):
            rich = row.get("has_rich_stats") == "1"
            off = row.get(f"shotsofftarget_{side}")
            if rich and off not in ("", None):
                value = float(row[f"shotsontarget_{side}"]) + float(off)
            elif row.get(f"total_shots_{side}") not in ("", None):
                value = float(row[f"total_shots_{side}"])
            else:
                return None
            values.append(value)
        return sum(values)
    primary = cfg["markets"][market]["primary_line"]
    if ledger.exists():
        canonical = {}
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            x = json.loads(line)
            if x["market"] != market or x["run_date"] > x["date"]: continue
            match_id = str(x["match_id"])
            current = canonical.get(match_id)
            if current is None or x["run_date"] >= current["run_date"]:
                canonical[match_id] = x
        with report.open("a", encoding="utf-8") as out:
            for x in canonical.values():
                key = f"{market}:{x['match_id']}"
                r = csv_rows.get(str(x["match_id"]))
                if key in settled or not r: continue
                if market == "cards" and cfg["markets"][market].get("cards_target") == "yellow_plus_red":
                    ypr_cols = ("yellow_cards_home", "red_cards_home", "yellow_cards_away", "red_cards_away")
                    if any(r.get(c, "") in ("", None) for c in ypr_cols): continue
                    total = sum(float(r[c]) for c in ypr_cols)
                elif unified:
                    total = unified_total(r)
                    if total is None: continue
                else:
                    if any(r.get(c, "") in ("", None) for c in actual): continue
                    total = float(r[actual[0]]) + float(r[actual[1]])
                y = int(total > primary); p = float(x["p_over_primary"]); pc = min(max(p, 1e-12), 1 - 1e-12)
                chosen = "over" if p >= .5 else "under"
                out.write(json.dumps({"market": market, "arm": x["arm"], "match_id": x["match_id"], "run_date": x["run_date"], "match_date": x["date"], "home": x["home"], "away": x["away"], "actual_total": total, "primary_line": primary, "p_over_primary": p, "chosen_side": chosen, "hit": (chosen == "over") == (y == 1), "log_loss": -(y * math.log(pc) + (1-y) * math.log(1-pc))}) + "\n")
                settled.add(key); added.append(key)
    atomic_json(sidecar, sorted(settled))
    return len(added)


def run():
    config = read_yaml_subset(RUNNER / "active.yaml"); run_date = date.today().isoformat()
    for name, cfg in config.get("leagues", {}).items():
        try:
            source = cfg.get("source", "jleague")
            if source == "jleague":
                upcoming, pull_errors = pull_and_fixtures(name, cfg)
                rebuild_csv(name, cfg)
            elif source == "world":
                upcoming, pull_errors = pull_and_fixtures_world(name, cfg)
                rebuild_csv_world(name, cfg)
            else:
                raise ValueError(f"unknown source: {source}")
            log_step(name, "data_refresh", {"errors": pull_errors})
            match_path = ROOT / cfg["data"]["matches"]
            match_rows = list(csv.DictReader(match_path.open(encoding="utf-8")))
            for market in cfg["markets"]:
                try:
                    if market == "sot":
                        pred = predict_sot(cfg, upcoming, run_date)
                    elif market == "goals":
                        pred = predict_goals(cfg, upcoming)
                    elif market == "cards":
                        pred = predict_cards(cfg, upcoming)
                    elif market == "corners":
                        pred = predict_corners(cfg, upcoming)
                    elif market == "total_shots":
                        pred = predict_total_shots(cfg, upcoming)
                    else:
                        raise ValueError(f"unknown market: {market}")
                    write_predictions(name, market, cfg, pred, run_date)
                    log_step(name, "predict", {"predicted": len(pred)}, market)
                except Exception as exc:
                    log_step(name, "predict", {"errors": [repr(exc)]}, market)
                try:
                    settled = settle(name, market, cfg, match_rows, run_date)
                    log_step(name, "settle", {"settled": settled}, market)
                except Exception as exc:
                    log_step(name, "settle", {"errors": [repr(exc)]}, market)
            log_step(name, "summary", {"fixtures_upcoming": len(upcoming), "errors": pull_errors})
        except Exception as exc:
            log_step(name, "league", {"errors": [repr(exc)]})


if __name__ == "__main__":
    run()
