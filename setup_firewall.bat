@echo off
REM Setup Windows Firewall for Learning App Backend
REM This script must be run as Administrator

echo ========================================
echo Learning App - Firewall Setup
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ This script must be run as Administrator
    echo.
    echo Right-click on this file and select "Run as administrator"
    pause
    exit /b 1
)

echo.
echo 🔧 Configuring Windows Firewall...
echo.

REM Add inbound rule for port 8000
netsh advfirewall firewall add rule name="Learning App Backend - Port 8000" dir=in action=allow protocol=TCP localport=8000
if %errorLevel% == 0 (
    echo ✅ Inbound rule added for port 8000
) else (
    echo ❌ Failed to add inbound rule
)

REM Add outbound rule for port 8000 (optional, usually not needed)
netsh advfirewall firewall add rule name="Learning App Backend - Port 8000 Outbound" dir=out action=allow protocol=TCP localport=8000
if %errorLevel% == 0 (
    echo ✅ Outbound rule added for port 8000
) else (
    echo ❌ Failed to add outbound rule
)

echo.
echo 📋 Firewall rules added:
netsh advfirewall firewall show rule name="Learning App Backend - Port 8000"

echo.
echo 🎉 Firewall setup completed!
echo.
echo 📝 Next steps:
echo    1. Start your backend server: python backend/run.py
echo    2. Find your IP address: ipconfig
echo    3. Test from another computer: http://YOUR-IP:8000
echo.
pause
