@echo off
:: ============================================================
::  Slacker USB Launcher — Windows
::  Double-click this file or let AutoPlay run it automatically
::  when the USB drive is inserted.
:: ============================================================
setlocal

:: Change to the directory that contains this script (the USB root)
cd /d "%~dp0"

:: Set PYTHONPATH so the bundled ./lib/ packages are found first
set "PYTHONPATH=%~dp0lib;%PYTHONPATH%"

:: Try to find Python 3 (prefer py launcher, then python, then python3)
set PYTHON=
where py >nul 2>&1 && set PYTHON=py -3
if not defined PYTHON (
    where python >nul 2>&1 && set PYTHON=python
)
if not defined PYTHON (
    where python3 >nul 2>&1 && set PYTHON=python3
)

if not defined PYTHON (
    echo.
    echo  Slacker could not find Python on this computer.
    echo  Please install Python 3.8 or later from https://www.python.org
    echo  and try again.
    echo.
    pause
    exit /b 1
)

echo Starting Slacker...
%PYTHON% slacker.py --widget

if %ERRORLEVEL% neq 0 (
    echo.
    echo  Slacker exited with an error. If dependencies are missing, run:
    echo    python setup_usb.py
    echo  from the USB drive to download them.
    echo.
    pause
)

endlocal
