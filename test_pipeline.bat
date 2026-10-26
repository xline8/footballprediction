@echo off
REM Full pipeline end-to-end test
REM Jalankan: test_pipeline.bat

echo === 1. Corner Model (--predict) ===
python model_corners_v3.py --predict
if errorlevel 1 goto error

echo === 2. DC/BTTS Model ===
python predict_upcoming.py
if errorlevel 1 goto error

echo === 3. TA Model ===
python ta_model.py --run
if errorlevel 1 goto error

echo === 4. Best Picks ===
python best_picks.py
if errorlevel 1 goto error

echo === 5. Validation ===
python -c "import csv; bp=list(csv.DictReader(open('best_picks.csv'))); bpd=[r for r in bp if not r.get('ev_model')]; print(f'Best picks: {len(bp)} rows, {len(bpd)} without ev_model'); assert len(bp)>0; print('✅ All outputs generated successfully')"
if errorlevel 1 goto error

echo === Pipeline test complete ===
goto end

:error
echo ❌ Pipeline failed at step above
exit /b 1

:end
