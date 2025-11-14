@echo off
REM AutoPilot IDE - Cleanup Script
REM This script removes virtual environment and cache files

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   AutoPilot IDE - Cleanup
echo ========================================
echo.

echo [*] This will remove:
echo     - Virtual environment (venv/)
echo     - Python cache files (__pycache__/)
echo     - Compiled Python files (*.pyc)
echo.

set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo [*] Cleanup cancelled
    exit /b 0
)

echo.
echo [*] Removing virtual environment...
if exist "venv" (
    rmdir /s /q venv
    echo [OK] Virtual environment removed
) else (
    echo [*] Virtual environment not found
)

echo [*] Removing Python cache files...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
    )
)
echo [OK] Cache files removed

echo [*] Removing .pyc files...
for /r . %%f in (*.pyc) do (
    if exist "%%f" del /q "%%f"
)
echo [OK] .pyc files removed

echo.
echo ========================================
echo   Cleanup Complete!
echo ========================================
echo.
echo You can now safely delete this folder or reinstall.
echo.

pause
