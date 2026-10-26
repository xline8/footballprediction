"""paths.py — lokasi file terpusat (hindari hardcode path per skrip).

Semua modul sebaiknya mengimpor konstanta ini daripada meng-hardcode
`C:/Users/...` atau `os.path.expanduser("~")/football-data`.
"""

import os

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE, "raw")
XGRAW = os.path.join(BASE, "xg_raw")
CACHE_DIR = os.path.join(BASE, ".cache")
MODEL_CACHE = os.path.join(CACHE_DIR, "models")
LEDGER_DIR = os.path.join(BASE, "ledger")
TA_DIR = os.path.join(BASE, "ta")

DATA_RAW = os.path.join(BASE, "all_matches.csv")
DATA_CLEAN = os.path.join(BASE, "all_matches_clean.csv")

CONFIG = os.path.join(BASE, "v2_config.json")
