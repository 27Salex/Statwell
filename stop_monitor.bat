@echo off
REM Read the port from the configuration file
set "port="
for /f "tokens=1,* delims==" %%a in ('findstr /i "port" config.ini') do (
    set "port=%%b"
)

if not defined port (
    echo [ERROR] Could not find the port in config.ini. Assuming default port 80.
    set "port=80"
)

echo Searching for the server process on port %port%...

REM Find the PID (Process ID) that is using the specified port
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%port%" ^| findstr "LISTENING"') do (
    set "PID=%%a"
    goto :found
)

echo Server does not appear to be running.
goto :eof

:found
if "%PID%"=="0" (
    echo Server does not appear to be running.
    goto :eof
)

echo Server process found with PID: %PID%.
echo Stopping the server...

REM Stop the process by its PID
taskkill /F /PID %PID%

echo.
echo Server stopped successfully.
pause

