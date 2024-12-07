@echo off
(echo.set sh=CreateObject^("Wscript.Shell"^)
echo.sh.Run """%~nx0"" 1", 0)>launch.vbs
if "%~1"=="" (start "" "launch.vbs"&exit /b)

del /q launch.vbs

if %errorlevel% equ 0 (
    TASKKILL /F /IM python.exe /T
    python -m pip install -r "requirements.txt" > "DATA\log\preinstallLog.txt" 2>&1
    start /b python main.py > "DATA\log\runLog.txt" 2>&1
) else (
    powershell -Command "Add-Type -AssemblyName 'System.Windows.Forms'; [System.Windows.Forms.MessageBox]::Show('Install Python >= 3.10', 'Python not installed')
)