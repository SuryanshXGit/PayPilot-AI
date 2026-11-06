@echo off
title PayPilot AI 2.0 - Demo & Test Launcher
cls
echo ======================================================================
echo  PAYPILOT AI 2.0 - HACKATHON DEMO LAUNCHER
echo  Built by PayPilot AI Team (Akashdeep, Jaskaran, Suryansh)
echo ======================================================================
echo.
echo [1/2] Running automated scenario and guardrail tests...
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0tests\run_tests.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Test suite failed. Please review output above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Opening Interactive PayPilot AI Web Demo in your browser...
start "" "%~dp0frontend\index.html"
echo.
echo Demo launched successfully! You can interact with the app in your browser.
echo Press any key to exit this launcher window.
pause >nul
