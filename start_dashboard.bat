@echo off
title Ascenta LinkedIn Content Agent
echo ============================================================
echo   Ascenta - Autonomous LinkedIn Content Agent
echo   Operator: Muhammad Rayyan
echo   Opening Dashboard at http://localhost:5050
echo ============================================================
start "" "http://localhost:5050"
python dashboard.py
pause
