#!/usr/bin/env bash
# Build a standalone app for the Automated File Organizer on macOS/Linux.
#
# NOTE: PyInstaller builds for whatever OS it runs on - running this script
# will NOT produce a Windows .exe. To get a Windows .exe, run
# build_scripts\build_exe.bat on an actual Windows machine (or Windows VM).
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Installing build dependencies (PyInstaller)..."
pip3 install -r requirements-dev.txt

echo
echo "Building FileOrganizer..."
pyinstaller build_scripts/organizer.spec --distpath dist --workpath build_scripts/work --noconfirm

echo
echo "Done. Your app is at dist/FileOrganizer"
