#!/usr/bin/env bash
# ============================================================
#  Slacker USB Launcher — Linux
#  Run from a terminal:  ./START.sh
# ============================================================

# Change to the directory that contains this script (the USB root)
cd "$(dirname "$0")" || exit 1

# Add bundled ./lib/ packages to PYTHONPATH
export PYTHONPATH="$(pwd)/lib:${PYTHONPATH}"

# Find Python 3
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        VERSION=$("$candidate" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        if [ "$VERSION" = "3" ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3 not found."
    echo "Install it with your package manager, e.g.:"
    echo "  sudo apt install python3   (Debian/Ubuntu)"
    echo "  sudo dnf install python3   (Fedora)"
    exit 1
fi

echo "Starting Slacker..."
"$PYTHON" slacker.py --widget

if [ $? -ne 0 ]; then
    echo ""
    echo "Slacker exited with an error. If dependencies are missing, run:"
    echo "  python3 setup_usb.py"
    echo "from the USB drive to download them."
fi
