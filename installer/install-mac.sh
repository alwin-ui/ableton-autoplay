#!/bin/bash
# Installs the AutoPlay control surface script into every Ableton Live
# User Library found on this Mac.
#
# Works from the release zip (double-click "Install AutoPlay (Mac).command"),
# from a clone of the repo, or straight from GitHub:
#   curl -fsSL https://raw.githubusercontent.com/alwin-ui/ableton-autoplay/main/installer/install-mac.sh | bash
set -euo pipefail

REPO_TARBALL="https://github.com/alwin-ui/ableton-autoplay/archive/refs/heads/main.tar.gz"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || pwd)"

# ---- find the script files ----------------------------------------------------
if [ -f "$HERE/AutoPlay/__init__.py" ]; then
    SRC="$HERE/AutoPlay"                      # release zip
elif [ -f "$HERE/../__init__.py" ]; then
    SRC="$(cd "$HERE/.." && pwd)"             # repo clone
else
    TMP="$(mktemp -d)"
    trap 'rm -rf "$TMP"' EXIT
    echo "Downloading AutoPlay..."
    curl -fsSL "$REPO_TARBALL" | tar -xz -C "$TMP"
    SRC="$(find "$TMP" -maxdepth 1 -mindepth 1 -type d | head -1)"
fi

# ---- find Live's User Library (it can be moved in Settings > Library) --------
LIBS=()
for cfg in "$HOME"/Library/Preferences/Ableton/Live*/Library.cfg; do
    [ -f "$cfg" ] || continue
    block="$(sed -n '/<UserLibrary>/,/<\/UserLibrary>/p' "$cfg")"
    path="$(printf '%s\n' "$block" | sed -n 's/.*<ProjectPath Value="\([^"]*\)".*/\1/p' | head -1)"
    name="$(printf '%s\n' "$block" | sed -n 's/.*<ProjectName Value="\([^"]*\)".*/\1/p' | head -1)"
    path="${path//&amp;/&}"
    name="${name//&amp;/&}"
    [ -n "$path" ] && LIBS+=("$path/${name:-User Library}")
done
[ ${#LIBS[@]} -eq 0 ] && LIBS+=("$HOME/Music/Ableton/User Library")

# ---- install -------------------------------------------------------------------
installed=0
while IFS= read -r lib; do
    [ -n "$lib" ] || continue
    dest="$lib/Remote Scripts/AutoPlay"
    if mkdir -p "$dest" 2>/dev/null; then
        cp -f "$SRC/__init__.py" "$SRC/AutoPlay.py" "$dest/"
        rm -rf "$dest/__pycache__"
        echo "Installed to: $dest"
        installed=1
    else
        echo "Could not write to: $dest"
    fi
done < <(printf '%s\n' "${LIBS[@]}" | sort -u)

echo
if [ "$installed" = 1 ]; then
    echo "Done! Now:"
    echo "  1. Restart Ableton Live."
    echo "  2. Settings > Link, Tempo & MIDI > pick 'AutoPlay' in an empty Control Surface slot."
    echo "  3. Launch a scene - the rest plays automatically."
else
    echo "Install failed - see messages above."
    exit 1
fi
