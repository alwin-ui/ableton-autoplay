#!/bin/bash
# Builds dist/AutoPlay.zip: the script folder plus double-click installers.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAGE="$(mktemp -d)/AutoPlay-Installer"
mkdir -p "$STAGE/AutoPlay" "$ROOT/dist"

cp "$ROOT/__init__.py" "$ROOT/AutoPlay.py" "$STAGE/AutoPlay/"
cp "$ROOT/installer/install-mac.sh" "$STAGE/Install AutoPlay (Mac).command"
cp "$ROOT/installer/install-windows.ps1" "$STAGE/install-windows.ps1"
printf '@echo off\r\npowershell -NoProfile -ExecutionPolicy Bypass -File "%%~dp0install-windows.ps1"\r\npause\r\n' \
    > "$STAGE/Install AutoPlay (Windows).bat"
chmod +x "$STAGE/Install AutoPlay (Mac).command"
cp "$ROOT/README.md" "$STAGE/README.md"

rm -f "$ROOT/dist/AutoPlay.zip"
(cd "$(dirname "$STAGE")" && zip -qrX "$ROOT/dist/AutoPlay.zip" "$(basename "$STAGE")")
echo "Built $ROOT/dist/AutoPlay.zip"
