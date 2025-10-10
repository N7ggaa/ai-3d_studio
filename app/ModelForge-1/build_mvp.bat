@echo off
echo Building ModelForge MVP Desktop App

REM Install dependencies
cd electron
npm install

REM Build the Electron app
npm run dist

REM Copy Python files to dist
xcopy /E /I /Y ".." "dist\resources\app\python"

echo Build complete. Check electron\dist for the installer.
pause