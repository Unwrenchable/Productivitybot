#!/usr/bin/env bash
# ============================================================
#  Slacker USB Launcher — macOS
#  Double-click this file in Finder to start Slacker.
#  (If macOS asks, choose "Open with Terminal".)
# ============================================================

# Change to the directory that contains this script (the USB root)
cd "$(dirname "$0")" || exit 1

# Add bundled ./lib/ packages to PYTHONPATH
export PYTHONPATH="$(pwd)/lib:${PYTHONPATH}"

# Find Python 3
PYTHON=""
for candidate in python3 python py; do
    if command -v "$candidate" >/dev/null 2>&1; then
        VERSION=$("$candidate" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        if [ "$VERSION" = "3" ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    osascript -e 'display dialog "Slacker could not find Python 3 on this Mac.\n\nPlease install Python 3.8+ from https://www.python.org and try again." with title "Slacker" buttons {"OK"} default button "OK" with icon caution' 2>/dev/null \
        || echo "ERROR: Python 3 not found. Install it from https://www.python.org"
    exit 1
fi

echo "Starting Slacker..."
"$PYTHON" slacker.py --widget

if [ $? -ne 0 ]; then
    echo ""
    echo "Slacker exited with an error. If dependencies are missing, run:"
    echo "  python3 setup_usb.py"
    echo "from the USB drive to download them."
    read -r -p "Press Enter to close..."
fi
