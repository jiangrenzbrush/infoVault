@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0dist\信息管家.exe" (
    start "" "%~dp0dist\信息管家.exe"
    exit /b
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0main.py"
    exit /b
)

where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw -3 "%~dp0main.py"
    exit /b
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0main.py"
    exit /b
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0main.py"
    exit /b
)

echo.
echo 没有找到可用的 Python，请先安装 Python 3。
pause
