@echo off
title Launching Loan Strategy Calculator
echo Starting Multi-Prepayment Loan Strategy Web App...
echo.

:: Check if Python is available to launch a local server
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo Python detected. Starting local server at http://localhost:8000
    start http://localhost:8000
    python -m http.server 8000
) else (
    echo Opening index.html directly in your default web browser...
    start "" "%~dp0index.html"
)