#!/bin/bash
# Full pipeline end-to-end test
# Jalankan: bash test_pipeline.sh
set -e

echo "=== 1. Corner Model (--predict) ==="
python model_corners_v3.py --predict

echo "=== 2. DC/BTTS Model ==="
python predict_upcoming.py

echo "=== 3. TA Model ==="
python ta_model.py --run

echo "=== 4. Best Picks ==="
python best_picks.py

echo "=== 5. Validation ==="
python -c "
import csv
bp = list(csv.DictReader(open('best_picks.csv')))
bpd = [r for r in bp if not r.get('ev_model')]
print(f'Best picks: {len(bp)} rows, {len(bpd)} without ev_model')
assert len(bp) > 0
print('✅ All outputs generated successfully')
"

echo "=== Pipeline test complete ==="
