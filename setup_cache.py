#!/usr/bin/env python3
"""setup_cache.py — Inisialisasi dan verifikasi cache sistem.

Menyiapkan:
1. Cache directory (.cache/models/)
2. Match cache (all_matches_clean.csv → .cache/matches.pkl)
3. Model state templates for TOP5 leagues
4. Verifikasi integritas

Usage:
    python setup_cache.py          # Build/maintain all caches
    python setup_cache.py --clean  # Hapus semua cache (fresh start)
    python setup_cache.py --check  # Cek status cache
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Pastikan kita bisa import modul lokal
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from football_etl import MatchCache
from model_state import (ModelState, CACHE_DIR, clear_model_cache,
                          get_model_cache_info)

CACHE_BASE = os.path.join(BASE_DIR, ".cache")


def ensure_cache_dirs():
    """Buat directory cache yang diperlukan."""
    os.makedirs(CACHE_BASE, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(os.path.join(CACHE_BASE, "predictions"), exist_ok=True)
    os.makedirs(os.path.join(CACHE_BASE, "tmp"), exist_ok=True)


def build_match_cache(force_rebuild: bool = False) -> dict:
    """Build atau refresh match cache."""
    print("Building match cache...")

    cache = MatchCache(force_reload=force_rebuild)
    n_matches = len(cache.matches)

    # Show summary
    div_counts = {}
    season_counts = {}

    for m in cache.matches:
        div = m.get('div', '?')
        div_counts[div] = div_counts.get(div, 0) + 1

        season = m.get('season', '?')
        season_counts[season] = season_counts.get(season, 0) + 1

    print(f"  Total matches cached: {n_matches:,}")
    print(f"  Divisions: {sorted(div_counts.keys())}")
    print(f"  Seasons: {sorted(season_counts.keys())}")

    result = {
        "status": "success",
        "total_matches": n_matches,
        "divisions": sorted(div_counts.keys()),
        "seasons": sorted(season_counts.keys()),
        "cache_file": cache._cache_file,
        "cache_size_mb": round(
            os.path.getsize(cache._cache_file) / (1024*1024), 2
        ) if os.path.exists(cache._cache_file) else 0
    }

    return result


def init_model_states() -> dict:
    """Inisialisasi template model state untuk semua divisi TOP5."""
    print("Initializing model state templates...")

    TOP5 = ["E0", "D1", "I1", "SP1", "F1"]
    created = []

    for div in TOP5:
        state = ModelState(div)
        if state.load():
            print(f"  {div}: Existing model state found (teams: {len(state.get_known_teams())})")
            created.append({
                "div": div,
                "status": "loaded",
                "teams": len(state.get_known_teams()),
                "last_fit": state.last_fit_date.isoformat() if state.last_fit_date else None
            })
        else:
            state.save(force=True)
            created.append({
                "div": div,
                "status": "initialized",
                "teams": 0,
                "last_fit": None
            })
            print(f"  {div}: Created new model state template")

    return {"model_states": created}


def check_cache_status() -> dict:
    """Cek status semua cache."""
    print("Checking cache status...")

    status = {
        "timestamp": datetime.now().isoformat(),
        "cache_base": CACHE_BASE,
        "directories": {},
        "files": {}
    }

    # Check directories
    dirs = [
        ".cache",
        os.path.join(".cache", "models"),
        os.path.join(".cache", "predictions"),
        os.path.join(".cache", "tmp")
    ]

    for d in dirs:
        full_path = os.path.join(BASE_DIR, d)
        exists = os.path.exists(full_path)
        size = get_dir_size(full_path) if exists else 0

        status["directories"][d] = {
            "exists": exists,
            "size_mb": round(size / (1024*1024), 2)
        }

    # Check match cache file
    match_cache_file = os.path.join(CACHE_BASE, "matches.pkl")
    if os.path.exists(match_cache_file):
        status["files"]["matches.pkl"] = {
            "exists": True,
            "size_mb": round(os.path.getsize(match_cache_file) / (1024*1024), 2),
            "modified": datetime.fromtimestamp(
                os.path.getmtime(match_cache_file)
            ).isoformat()
        }
    else:
        status["files"]["matches.pkl"] = {"exists": False}

    # Check model states
    status["model_states"] = get_model_cache_info()

    # Data files check
    data_files = [
        "all_matches_clean.csv",
        "all_matches.csv",
        "predictions_upcoming.csv",
        "v2_config.json"
    ]

    status["data_files"] = {}
    for f in data_files:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            status["data_files"][f] = {
                "exists": True,
                "size_mb": round(os.path.getsize(path) / (1024*1024), 2)
            }
        else:
            status["data_files"][f] = {"exists": False}

    return status


def clean_cache():
    """Hapus semua cache."""
    print("Cleaning all cache files...")

    if os.path.exists(CACHE_BASE):
        # Clear model states
        clear_model_cache()  # Hapus semua model state
        print("  Cleared model states")

        # Clear match cache
        if os.path.exists(CACHE_BASE):
            shutil.rmtree(CACHE_BASE)
            print(f"  Removed {CACHE_BASE}")

        # Recreate directories
        ensure_cache_dirs()
        print("  Recreated cache directories")

    print("Cache cleaned successfully.")


def get_dir_size(path):
    """Dapatkan total ukuran directory."""
    if not os.path.exists(path):
        return 0

    total = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except OSError:
                pass
    return total


def main():
    args = sys.argv[1:]

    if "--clean" in args:
        clean_cache()
        if "--check" in args:
            print("\n" + "="*60)
        else:
            return

    if "--check" in args:
        status = check_cache_status()
        print("\nCache Status:")
        print(json.dumps(status, indent=2, default=str))
        return

    # Default: setup all caches
    print("="*60)
    print("Setting up prediction pipeline cache system")
    print("="*60)
    print()

    ensure_cache_dirs()

    # Build match cache
    print("\n[1/3] Building match cache...")
    match_result = build_match_cache(force_rebuild=False)

    # Initialize model states
    print("\n[2/3] Initializing model states...")
    model_result = init_model_states()

    # Final cache check
    print("\n[3/3] Final cache status...")
    status = check_cache_status()

    # Summary
    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print(f"Match cache: {match_result['total_matches']:,} matches")
    print(f"Model states: {len(model_result['model_states'])} initialized")

    print("\nCache files:")
    for name, info in status["files"].items():
        if info.get("exists"):
            print(f"  {name}: {info.get('size_mb', 0)} MB")

    print("\nData files ready:")
    for name, info in status["data_files"].items():
        if info.get("exists"):
            print(f"  {name}: {info.get('size_mb', 0)} MB")

    print("\nNext steps:")
    print("  1. Run: python pipeline_orchestrator.py --run-all")
    print("  2. Check: tail -f ledger/picks.jsonl")


if __name__ == "__main__":
    main()
