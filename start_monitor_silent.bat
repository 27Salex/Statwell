@echo off
REM Move to this .bat directory
cd /d "%~dp0"

REM Execute in background
start "Statwell" /B pythonw.exe server.py
