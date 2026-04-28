@echo off
title PERSONAL ADVICE AI Assistant
cd /d "%~dp0"
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Could not start. Make sure Python is installed.
    echo Download Python from https://www.python.org/downloads/
    pause
)
