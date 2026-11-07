"""Opt-in 1xBet full-market snapshots via explicit authorized proxies.

The adapter treats the page state as inert data: it never executes downloaded
JavaScript. Configure ``XBET_MANIFEST`` with CSV rows ``game_id,url,event_id``
and ``XBET_PROXIES`` with comma-separated proxy URLs when direct access is not
available. Failed refreshes never replace an existing snapshot.
"""
from __future__ import annotations

import argparse
import csv
import ipaddress
import json
import math
import os
import re
import tempfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import requests

MAX_RESPONSE_BYTES = 8 * 1024 * 1024
MAX_AST_NODES = 100_000
MAX_AST_DEPTH = 40
REQUEST_TIMEOUT = (8, 20)
ALLOWED_HOST_SUFFIX = ".1xbet.com"
SNAPSHOT_COLS = [
    "captured_at", "game_id", "market", "line", "selection", "bookmaker",
    "odds", "url",
]
INVENTORY_COLS = [
    "captured_at", "game_id", "event_id", "context_id", "period", "market",
    "selection", "line", "bookmaker", "odds", "blocked", "group_id",
    "outcome_type", "url",
]


class BlockedResponse(RuntimeError):
    """The server returned a challenge, login page, or unusable document."""


class DecoderLimitError(ValueError):
    """The serialized page state exceeds the safe decoder limits."""


class _ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.scripts: list[str] = []
        self._inside = False
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self._inside = True
            self._parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self._inside:
            self.scripts.append("".join(self._parts))
            self._inside = False

    def handle_data(self, data: str) -> None:
        if self._inside:
            self._parts.append(data)


class ProxyPool:
    """Round-robin over explicitly configured proxies only."""

    def __init__(self, proxies: list[str] | tuple[str, ...]) -> None:
        self._proxies = tuple(dict.fromkeys(self._validate(p) for p in proxies if p.strip()))
        self._index = 0

    @classmethod
    def from_environment(cls) -> "ProxyPool":
        raw = os.environ.get("XBET_PROXIES", os.environ.get("XBET_PROXY", ""))
        return cls([item.strip() for item in re.split(r"[,;\n]", raw) if item.strip()])

    @staticmethod
    def _validate(value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError(f"proxy URL tidak valid: {value!r}")
        if parsed.username or parsed.password or parsed.path not in {"", "/"} \
                or parsed.query or parsed.fragment:
            raise ValueError("proxy harus berupa URL host:port tanpa kredensial/path")
        if parsed.port is None or not 1 <= parsed.port <= 65535:
            raise ValueError("proxy membutuhkan port 1..65535")
        try:
            ip = ipaddress.ip_address(parsed.hostname)
        except ValueError:
            ip = None
        if ip is not None and (ip.is_private or ip.is_loopback or ip.is_link_local
                               or ip.is_multicast or ip.is_unspecified or ip.is_reserved):
            raise ValueError("proxy IP non-publik ditolak")
        return value

    def urls(self) -> list[str]:
        return list(self._proxies)

    def next(self) -> str | None:
        if not self._proxies:
            return None
        value = self._proxies[self._index % len(self._proxies)]
        self._index += 1
        return value


def _target_url(url: str) -> str:
    parsed = urlsplit(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not (host == "1xbet.com" or host.endswith(ALLOWED_HOST_SUFFIX)):
        raise ValueError("URL target harus HTTPS pada domain 1xbet.com")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("URL target tidak boleh memuat kredensial/query/fragment")
    return url


def response_body(response: Any) -> str:
    if response.status_code != 200:
        raise BlockedResponse(f"HTTP {response.status_code}")
    content = bytes(response.content)
    if len(content) > MAX_RESPONSE_BYTES:
        raise BlockedResponse("respons melebihi batas ukuran")
    text = content.decode(response.encoding or "utf-8", errors="replace")
    if "window.__V3_HOST_APP__=" not in text or "window.__BETTING_APP__=" not in text:
        raise BlockedResponse("respons bukan halaman betting state yang valid")
    return text


def _serialized_app(html: str) -> str:
    parser = _ScriptParser()
    parser.feed(html)
    for script in parser.scripts:
        marker = "codeToEval:"
        start = script.find(marker)
        if start < 0:
            continue
        encoded, _ = json.JSONDecoder().raw_decode(script[start + len(marker):])
        if isinstance(encoded, str) and encoded.startswith("window.__BETTING_APP__="):
            return encoded
    raise BlockedResponse("serialized betting app tidak ditemukan")


def _data(node: dict[str, Any], scope: dict[str, Any], depth: int, count: list[int]) -> Any:
    count[0] += 1
    if count[0] > MAX_AST_NODES or depth > MAX_AST_DEPTH:
        raise DecoderLimitError("serialized state terlalu besar/dalam")
    kind = node.get("type")
    if kind == "Literal":
        return node.get("value")
    if kind == "Identifier":
        if node.get("name") in {"Infinity", "NaN", "undefined"}:
            return None
        if node.get("name") not in scope:
            raise ValueError("identifier serialized tidak dikenal")
        return scope[node["name"]]
    if kind == "ArrayExpression":
        return [_data(item, scope, depth + 1, count) if item else None
                for item in node.get("elements", [])]
    if kind == "ObjectExpression":
        result = {}
        for prop in node.get("properties", []):
            if prop.get("type") != "Property" or prop.get("kind") != "init" \
                    or prop.get("method"):
                raise ValueError("object serialized tidak didukung")
            key_node = prop.get("key", {})
            key = key_node.get("name", key_node.get("value"))
            result[key] = _data(prop["value"], scope, depth + 1, count)
        return result
    if kind == "UnaryExpression" and node.get("operator") == "void":
        return None
    if kind == "UnaryExpression" and node.get("operator") == "-":
        value = _data(node["argument"], scope, depth + 1, count)
        if isinstance(value, (float, int)) and not isinstance(value, bool):
            return -value
    if kind == "CallExpression":
        callee = node.get("callee", {})
        if callee.get("type") == "Identifier" and callee.get("name") == "Array":
            args = [_data(item, scope, depth + 1, count) for item in node.get("arguments", [])]
            if len(args) == 1 and isinstance(args[0], int) and 0 <= args[0] <= 100_000:
                return [None] * args[0]
    if kind == "NewExpression":
        callee = node.get("callee", {})
        if callee.get("type") == "Identifier" and callee.get("name") == "Set":
            args = [_data(item, scope, depth + 1, count) for item in node.get("arguments", [])]
            if args == [[]]:
                return []
    if kind == "AssignmentExpression" and node.get("operator") == "=":
        left = node.get("left", {})
        if left.get("type") != "MemberExpression":
            raise ValueError("assignment serialized tidak didukung")
        target = _data(left["object"], scope, depth + 1, count)
        key = (_data(left["property"], scope, depth + 1, count)
               if left.get("computed") else left.get("property", {}).get("name"))
        if not isinstance(target, (dict, list)):
            raise ValueError("target assignment serialized tidak valid")
        value = _data(node["right"], scope, depth + 1, count)
        target[key] = value
        return value
    raise ValueError(f"node serialized tidak didukung: {kind}")


def decode_state(page_html: str) -> dict[str, Any]:
    encoded = _serialized_app(page_html)
    try:
        import esprima
    except ImportError as exc:
        raise RuntimeError("install esprima untuk membaca state 1xBet") from exc
    ast = esprima.parseScript(encoded).toDict()
    call = ast["body"][0]["expression"]["right"]
    if call.get("type") != "CallExpression" \
            or call.get("callee", {}).get("type") != "FunctionExpression":
        raise ValueError("wrapper serialized tidak valid")
    function = call["callee"]
    arguments = [_data(item, {}, 0, [0]) for item in call.get("arguments", [])]
    params = [item["name"] for item in function.get("params", [])]
    if len(arguments) != len(params):
        raise ValueError("jumlah argumen serialized tidak cocok")
    scope = dict(zip(params, arguments))
    for statement in function["body"]["body"]:
        if statement.get("type") == "ExpressionStatement":
            _data(statement["expression"], scope, 0, [0])
        elif statement.get("type") == "ReturnStatement":
            value = _data(statement["argument"], scope, 0, [0])
            if not isinstance(value, dict):
                raise ValueError("state serialized bukan object")
            return value
        else:
            raise ValueError("statement serialized tidak didukung")
    raise ValueError("state serialized tidak memiliki return")


def extract_game(state: dict[str, Any], event_id: int | str) -> dict[str, Any]:
    try:
        store = state["pinia"]["game"]
        current = str(store["currentGameId"])
        game = store["gamesById"][current]
        if int(game.get("permanentId")) != int(event_id):
            raise ValueError("event identity tidak cocok")
        if game.get("isSubGame") or game.get("gamePeriodId", 0) != 0:
            raise ValueError("state bukan pertandingan utama")
        return game
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("game state tidak valid") from exc


def _odds(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and result > 1.0 else None


def _contexts(game: dict[str, Any]) -> list[tuple[str, int, list[dict[str, Any]]]]:
    contexts = [(str(game.get("id", "main")), 0,
                 game.get("unparsedEventGroups") or [])]
    for subgame in game.get("baseSubGames") or []:
        contexts.append((str(subgame.get("id", game.get("id", "main"))),
                         int(subgame.get("period", 0)),
                         subgame.get("eventGroups") or []))
    return contexts


def normalize_game(game: dict[str, Any], url: str,
                   captured_at: str | None = None) -> list[dict[str, Any]]:
    captured_at = captured_at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    output = []
    mapping = {
        (1, 1): ("1X2", "1"), (1, 2): ("1X2", "X"), (1, 3): ("1X2", "2"),
        (8, 4): ("DC", "1X"), (8, 5): ("DC", "12"), (8, 6): ("DC", "X2"),
        (17, 9): ("OU", "Over"), (17, 10): ("OU", "Under"),
        (19, 180): ("BTS", "Yes"), (19, 181): ("BTS", "No"),
    }
    for context_id, period, groups in _contexts(game):
        for group in groups:
            group_id = int(group.get("groupId", -1))
            for events in group.get("events") or []:
                for event in events or []:
                    if not isinstance(event, dict):
                        continue
                    outcome_type = event.get("type")
                    market, selection = mapping.get((group_id, outcome_type), ("raw", ""))
                    line = event.get("parameter", "")
                    line = "" if line is None else str(line)
                    output.append({
                        "captured_at": captured_at,
                        "game_id": str(game.get("permanentId", "")),
                        "event_id": str(game.get("permanentId", "")),
                        "context_id": context_id, "period": period,
                        "market": market, "selection": selection, "line": line,
                        "bookmaker": "1xbet", "odds": _odds(event.get("cf")),
                        "blocked": bool(event.get("blocked")),
                        "group_id": group_id, "outcome_type": outcome_type, "url": url,
                    })
    return output


def _fetch(url: str, pool: ProxyPool) -> str:
    _target_url(url)
    if not pool.urls():
        raise RuntimeError("XBET_PROXIES/XBET_PROXY belum diset")
    attempts = len(pool.urls())
    last: Exception | None = None
    for _ in range(attempts):
        proxy = pool.next()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        try:
            with requests.Session() as client:
                client.trust_env = False
                response = client.get(url, headers={"User-Agent": "Mozilla/5.0"},
                                       proxies=proxies, timeout=REQUEST_TIMEOUT,
                                       allow_redirects=False)
                return response_body(response)
        except (requests.RequestException, BlockedResponse) as exc:
            last = exc
            if isinstance(exc, BlockedResponse):
                raise
    raise RuntimeError(f"1xBet fetch gagal setelah {attempts} proxy") from last


def scrape_job(job: dict[str, str], pool: ProxyPool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    captured = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    page = _fetch(job["url"], pool)
    game = extract_game(decode_state(page), job["event_id"])
    if game.get("hasScores") or game.get("startUnixTimestamp", 0) <= datetime.now(timezone.utc).timestamp():
        raise ValueError("fixture bukan lagi pre-match")
    rows = normalize_game(game, job["url"], captured)
    return ([row for row in rows if row["market"] != "raw" and row["period"] == 0
             and row["odds"] is not None and not row["blocked"]], rows)


def _append_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def _write_csv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(fd)
    try:
        with open(temp, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run_manifest(manifest: Path, output_dir: Path, pool: ProxyPool) -> dict[str, Any]:
    with manifest.open(encoding="utf-8", newline="") as handle:
        jobs = [row for row in csv.DictReader(handle) if row.get("url") and row.get("event_id")]
    snapshots, inventory, failures = [], [], []
    for job in jobs:
        try:
            rows, all_rows = scrape_job(job, pool)
            snapshots.extend([{**row, "game_id": job.get("game_id") or row["game_id"]}
                              for row in rows])
            inventory.extend(all_rows)
        except (OSError, ValueError, RuntimeError, requests.RequestException) as exc:
            failures.append({"event_id": job.get("event_id"), "error": str(exc)})
    if snapshots:
        _append_csv(output_dir / "odds_1xbet_snapshots.csv", SNAPSHOT_COLS, snapshots)
    if inventory:
        _append_csv(output_dir / "odds_1xbet_all_outcomes.csv", INVENTORY_COLS, inventory)
    return {"status": "success" if not failures else "partial", "jobs": len(jobs),
            "snapshots": len(snapshots), "inventory": len(inventory), "failures": failures}


def run_configured() -> dict[str, Any]:
    manifest = os.environ.get("XBET_MANIFEST")
    if not manifest:
        return {"status": "disabled", "reason": "XBET_MANIFEST belum diset"}
    output = Path(os.environ.get("XBET_OUTPUT", Path(__file__).resolve().parent / "ta"))
    return run_manifest(Path(manifest), output, ProxyPool.from_environment())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "ta")
    parser.add_argument("--proxy", action="append", default=[])
    args = parser.parse_args()
    result = run_manifest(args.manifest, args.output,
                          ProxyPool(args.proxy) if args.proxy else ProxyPool.from_environment())
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] in {"success", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
