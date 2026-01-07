@echo off
REM Launcher for Oracle <-> Azure SQL Query Converter GUI
REM Double-click this file to start the GUI application

echo Starting Oracle to Azure SQL Query Converter GUI...
echo.

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    echo Using virtual environment...
    .venv\Scripts\python.exe run_gui.py
) else (
    echo Using system Python...
    python run_gui.py
)

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause >nul
)
