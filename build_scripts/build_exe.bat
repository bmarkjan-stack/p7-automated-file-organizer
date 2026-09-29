@echo off
REM Build a standalone Windows .exe for the Automated File Organizer.
REM Run this on Windows, from anywhere, with Python 3.10+ and pip on your PATH.

setlocal
cd /d "%~dp0\.."

echo Installing build dependencies (PyInstaller)...
pip install -r requirements-dev.txt
if errorlevel 1 goto :error

echo.
echo Building FileOrganizer.exe (this can take a minute)...
pyinstaller build_scripts\organizer.spec --distpath dist --workpath build_scripts\work --noconfirm
if errorlevel 1 goto :error

echo.
echo Done. Your app is at dist\FileOrganizer.exe
echo Double-click it to launch the GUI, or run it from a terminal with
echo arguments to use it as a command-line tool (see README.md).
pause
exit /b 0

:error
echo.
echo Build failed - see the output above for details.
pause
exit /b 1
