@echo off
REM CardForge Windows Launcher
REM Double-click this file to start CardForge with everything initialized

echo.
echo ====================================================================
echo   CardForge - MTG Collection Manager
echo   Auto-initializing all dependencies...
echo ====================================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then run: .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if setup has been run
if not exist "data\cardforge.db" (
    echo.
    echo [SETUP] First time setup detected
    echo.
    python setup_wizard.py
    if errorlevel 1 (
        echo.
        echo [ERROR] Setup failed
        pause
        exit /b 1
    )
)

REM Run CardForge launcher
python cardforge.py %*

REM If no arguments, show menu
if "%~1"=="" (
    echo.
    echo What would you like to do?
    echo.
    echo 1. Import collection
    echo 2. View statistics
    echo 3. Search cards
    echo 4. Ask AI agent
    echo 5. Start web interface
    echo 6. Start desktop GUI
    echo 7. Exit
    echo.
    
    set /p choice="Enter choice (1-7): "
    
    if "%choice%"=="1" (
        set /p file="Enter CSV file path: "
        python cardforge.py import "%file%"
    )
    if "%choice%"=="2" python cardforge.py stats
    if "%choice%"=="3" (
        set /p query="Enter search query: "
        python cardforge.py search "%query%"
    )
    if "%choice%"=="4" (
        set /p query="Enter AI query: "
        python cardforge.py ai "%query%"
    )
    if "%choice%"=="5" python cardforge.py web
    if "%choice%"=="6" python cardforge.py gui
    if "%choice%"=="7" exit /b 0
)

pause
