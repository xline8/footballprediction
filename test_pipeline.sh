#!/bin/bash
# Full pipeline end-to-end test
# Jalankan: bash test_pipeline.sh
set -e
PY=.venv/bin/python

echo "=== 1. Corner Model (--predict) ==="
$PY model_corners_v3.py --predict

echo "=== 2. DC/BTTS Model ==="
$PY predict_upcoming_refactored.py

echo "=== 3. TA Model ==="
$PY ta_model.py --run

echo "=== 4. Best Picks ==="
$PY best_picks.py

echo "=== 5. Validation ==="
$PY -c "
import csv
bp = list(csv.DictReader(open('best_picks.csv')))
bpd = [r for r in bp if not r.get('ev_model')]
print(f'Best picks: {len(bp)} rows, {len(bpd)} without ev_model')
assert len(bp) > 0
print('✅ All outputs generated successfully')
"

echo "=== Pipeline test complete ==="
