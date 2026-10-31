@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if /I "%~1"=="--help" goto :help

echo.
echo ================================================
echo  Football Prediction - Start
echo ================================================
echo Project folder: %CD%
echo.

REM Find Python first. Python 3.11 or newer is required.
py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "BOOTSTRAP_PYTHON=py -3"
) else (
    python --version >nul 2>&1
    if errorlevel 1 goto :no_python
    set "BOOTSTRAP_PYTHON=python"
)

%BOOTSTRAP_PYTHON% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 goto :old_python

REM Create an isolated environment on first use so project packages do not
REM mix with Python packages used by other applications.
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creating the Python environment for the first time...
    %BOOTSTRAP_PYTHON% -m venv .venv
    if errorlevel 1 goto :failed
)

set "PYTHON=.venv\Scripts\python.exe"
echo [2/3] Checking application requirements...
%PYTHON% -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :failed

echo [3/3] Opening the Control Center...
%PYTHON% football_cli.py
if errorlevel 1 goto :failed

echo.
echo Control Center closed.
goto :end

:no_python
echo.
echo Python was not found.
echo Install Python 3.11 or newer from https://www.python.org/downloads/
echo During installation, select "Add Python to PATH".
goto :end

:old_python
echo.
echo The installed Python version is too old. This project requires Python 3.11 or newer.
echo Download a newer version from https://www.python.org/downloads/ and run start.bat again.
goto :end

:failed
echo.
echo The process stopped because a step failed.
echo Copy the error message above if you need help.

:end
echo.
pause
exit /b

:help
echo Double-click start.bat to run this project.
echo The script creates .venv when needed, installs requirements, and opens the Control Center.
exit /b 0
