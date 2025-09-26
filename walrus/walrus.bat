@echo off
REM Walrus CLI Batch Script for Windows
REM This script provides easy access to walrus push/pull commands

setlocal enabledelayedexpansion

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and add it to your PATH
    pause
    exit /b 1
)

REM Check if walrus_cli.py exists
if not exist "%~dp0walrus_cli.py" (
    echo Error: walrus_cli.py not found
    echo Please make sure this script is in the same directory as walrus_cli.py
    pause
    exit /b 1
)

REM Check if walrus command is available
walrus --help >nul 2>&1
if errorlevel 1 (
    echo Warning: 'walrus' command not found in PATH
    echo Make sure Walrus CLI is installed and configured
    echo.
)

if "%1"=="" (
    echo Walrus CLI - Git-like storage using Walrus
    echo.
    echo Usage:
    echo   %0 push [directory]     - Push directory to Walrus storage
    echo   %0 pull [directory]     - Pull directory from Walrus storage  
    echo   %0 list                 - List all tracked repositories
    echo   %0 example              - Run example demonstration
    echo.
    echo Examples:
    echo   %0 push                 - Push current directory
    echo   %0 push C:\MyProject    - Push specific directory
    echo   %0 pull                 - Pull to current directory
    echo   %0 pull C:\Restored     - Pull to specific directory
    pause
    exit /b 0
)

if "%1"=="example" (
    echo Running example demonstration...
    python "%~dp0example_usage.py"
    pause
    exit /b 0
)

REM Run the walrus CLI with all arguments
python "%~dp0walrus_cli.py" %*

REM Pause to show output if running from file explorer
if "%2"=="" pause