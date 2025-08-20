# LuminaIQ Unified Installer Creation Script
# This script creates a unified installer that includes both frontend and backend

param(
    [string]$OutputDir = ".\dist-unified",
    [switch]$Clean = $false
)

Write-Host "=== LuminaIQ Unified Installer Creator ===" -ForegroundColor Cyan
Write-Host "Creating unified Windows installer package..." -ForegroundColor Green

# Define paths
$FrontendExe = ".\frontend\src-tauri\target\release\app.exe"
$FrontendMsi = ".\frontend\src-tauri\target\release\bundle\msi\LuminaIQ_1.0.0_x64_en-US.msi"
$FrontendNsis = ".\frontend\src-tauri\target\release\bundle\nsis\LuminaIQ_1.0.0_x64-setup.exe"
$BackendExe = ".\backend\dist\luminaiq-backend.exe"

# Clean output directory if requested
if ($Clean -and (Test-Path $OutputDir)) {
    Write-Host "Cleaning output directory..." -ForegroundColor Yellow
    Remove-Item $OutputDir -Recurse -Force
}

# Create output directory
if (!(Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

Write-Host "Output directory: $OutputDir" -ForegroundColor Blue

# Verify all required files exist
$RequiredFiles = @(
    @{Path = $FrontendExe; Name = "Frontend Executable"},
    @{Path = $FrontendMsi; Name = "Frontend MSI Installer"},
    @{Path = $FrontendNsis; Name = "Frontend NSIS Installer"},
    @{Path = $BackendExe; Name = "Backend Executable"}
)

$AllFilesExist = $true
foreach ($File in $RequiredFiles) {
    if (Test-Path $File.Path) {
        Write-Host "Found: $($File.Name)" -ForegroundColor Green
    } else {
        Write-Host "Missing: $($File.Name) at $($File.Path)" -ForegroundColor Red
        $AllFilesExist = $false
    }
}

if (!$AllFilesExist) {
    Write-Host "Error: Some required files are missing. Please build both frontend and backend first." -ForegroundColor Red
    exit 1
}

# Copy files to unified directory
Write-Host "`nCopying files to unified package..." -ForegroundColor Blue

# Create subdirectories
$Dirs = @("executables", "installers", "backend")
foreach ($Dir in $Dirs) {
    $DirPath = Join-Path $OutputDir $Dir
    if (!(Test-Path $DirPath)) {
        New-Item -ItemType Directory -Path $DirPath | Out-Null
    }
}

# Copy frontend files
Copy-Item $FrontendExe -Destination (Join-Path $OutputDir "executables\LuminaIQ.exe")
Copy-Item $FrontendMsi -Destination (Join-Path $OutputDir "installers\")
Copy-Item $FrontendNsis -Destination (Join-Path $OutputDir "installers\")

# Copy backend files
Copy-Item $BackendExe -Destination (Join-Path $OutputDir "backend\")

Write-Host "Files copied successfully" -ForegroundColor Green

# Create installation script
$InstallScript = @"
@echo off
echo =================================
echo LuminaIQ Installation Script
echo =================================
echo.

echo Installing LuminaIQ Desktop Application...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges.
) else (
    echo Warning: Not running as administrator. Some features may not work properly.
    echo Please run as administrator for best experience.
    echo.
)

REM Create application directory
set "INSTALL_DIR=%PROGRAMFILES%\LuminaIQ"
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Created installation directory: %INSTALL_DIR%
)

REM Copy backend executable
echo Copying backend executable...
copy /Y "backend\luminaiq-backend.exe" "%INSTALL_DIR%\"
if %errorLevel% == 0 (
    echo ✓ Backend installed successfully
) else (
    echo ✗ Failed to install backend
    pause
    exit /b 1
)

REM Install frontend using MSI
echo.
echo Installing frontend application...
echo This will open the MSI installer. Please follow the installation wizard.
echo.
pause

start /wait msiexec /i "installers\LuminaIQ_1.0.0_x64_en-US.msi" /qb

if %errorLevel% == 0 (
    echo ✓ Frontend installed successfully
) else (
    echo ✗ Frontend installation failed or was cancelled
    pause
    exit /b 1
)

echo.
echo =================================
echo Installation completed!
echo =================================
echo.
echo LuminaIQ has been installed successfully.
echo.
echo To start the application:
echo 1. The desktop application should be available in your Start Menu
echo 2. The backend service is installed at: %INSTALL_DIR%\luminaiq-backend.exe
echo.
echo Note: You may need to start the backend manually before using the application.
echo.
pause
"@

$InstallScript | Out-File -FilePath (Join-Path $OutputDir "install.bat") -Encoding ASCII

# Create uninstall script
$UninstallScript = @"
@echo off
echo =================================
echo LuminaIQ Uninstallation Script
echo =================================
echo.

echo This will remove LuminaIQ from your system.
echo.
set /p confirm="Are you sure you want to continue? (y/N): "
if /i not "%confirm%"=="y" (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo Uninstalling LuminaIQ...

REM Stop any running backend processes
taskkill /f /im luminaiq-backend.exe >nul 2>&1

REM Remove installation directory
set "INSTALL_DIR=%PROGRAMFILES%\LuminaIQ"
if exist "%INSTALL_DIR%" (
    echo Removing installation directory...
    rmdir /s /q "%INSTALL_DIR%"
    echo ✓ Installation directory removed
)

REM Uninstall frontend using Windows Programs and Features
echo.
echo Please use Windows "Programs and Features" to uninstall the LuminaIQ desktop application.
echo You can access it through Control Panel > Programs > Programs and Features
echo Look for "LuminaIQ" in the list and click "Uninstall"
echo.

echo Uninstallation completed!
pause
"@

$UninstallScript | Out-File -FilePath (Join-Path $OutputDir "uninstall.bat") -Encoding ASCII

# Create README file
$ReadmeContent = @"
# LuminaIQ Unified Installation Package

This package contains everything needed to install LuminaIQ on Windows.

## Contents

- `executables/LuminaIQ.exe` - Standalone frontend application
- `installers/LuminaIQ_1.0.0_x64_en-US.msi` - Frontend MSI installer
- `installers/LuminaIQ_1.0.0_x64-setup.exe` - Frontend NSIS installer
- `backend/luminaiq-backend.exe` - Backend API server
- `install.bat` - Automated installation script
- `uninstall.bat` - Uninstallation script

## Installation Options

### Option 1: Automated Installation (Recommended)
1. Right-click on `install.bat` and select "Run as administrator"
2. Follow the prompts to complete installation

### Option 2: Manual Installation
1. Run one of the frontend installers:
   - Double-click `installers/LuminaIQ_1.0.0_x64_en-US.msi` (MSI installer)
   - OR double-click `installers/LuminaIQ_1.0.0_x64-setup.exe` (NSIS installer)
2. Copy `backend/luminaiq-backend.exe` to a permanent location
3. Start the backend before using the frontend application

### Option 3: Portable Mode
1. Copy `executables/LuminaIQ.exe` to your desired location
2. Copy `backend/luminaiq-backend.exe` to the same or nearby location
3. Start the backend first, then run the frontend

## Usage

1. Start the backend: Run `luminaiq-backend.exe`
2. Start the frontend: Launch LuminaIQ from Start Menu or run the executable
3. The frontend will connect to the backend automatically

## System Requirements

- Windows 10 or later (64-bit)
- .NET Framework (usually pre-installed)
- Administrator privileges for installation

## Troubleshooting

- If the frontend cannot connect to the backend, ensure the backend is running
- Check Windows Firewall settings if connection issues persist
- Run both applications as administrator if needed

## Uninstallation

Run `uninstall.bat` as administrator to remove the application.

---
Generated by LuminaIQ Build System
"@

$ReadmeContent | Out-File -FilePath (Join-Path $OutputDir "README.md") -Encoding UTF8

Write-Host "`n=== Package Creation Complete ===" -ForegroundColor Cyan
Write-Host "Unified installer package created at: $OutputDir" -ForegroundColor Green
Write-Host "`nPackage contents:" -ForegroundColor Blue
Get-ChildItem $OutputDir -Recurse | ForEach-Object {
    $RelativePath = $_.FullName.Substring($OutputDir.Length + 1)
    if ($_.PSIsContainer) {
        Write-Host "  [DIR] $RelativePath/" -ForegroundColor Yellow
    } else {
        $Size = [math]::Round($_.Length / 1MB, 2)
        Write-Host "  [FILE] $RelativePath ($Size MB)" -ForegroundColor White
    }
}

Write-Host "`nReady for distribution!" -ForegroundColor Green
Write-Host "To install: Run 'install.bat' as administrator from the package directory" -ForegroundColor Cyan
