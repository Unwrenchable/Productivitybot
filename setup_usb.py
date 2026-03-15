"""
Slacker USB Setup — run this once on any computer that has Python + internet
access to download all dependencies into the ./lib/ folder on the USB drive.

After running this, the USB is self-contained and Slacker can launch on any
computer that has Python installed — no internet or pip required on the host.

Usage:
    python setup_usb.py
"""

import os
import subprocess
import sys


# Dependencies are downloaded here, next to this script (i.e. on the USB).
LIB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
REQ_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")


def main() -> None:
    print("=" * 50)
    print("  Slacker USB Setup")
    print("=" * 50)
    print()

    if not os.path.isfile(REQ_FILE):
        print(f"ERROR: requirements.txt not found at {REQ_FILE}", file=sys.stderr)
        sys.exit(1)

    print(f"Downloading dependencies into:\n  {LIB_DIR}\n")
    os.makedirs(LIB_DIR, exist_ok=True)

    result = subprocess.run(
        [
            sys.executable, "-m", "pip", "install",
            "--target", LIB_DIR,
            "--upgrade",
            "-r", REQ_FILE,
        ],
        check=False,
    )

    if result.returncode == 0:
        print()
        print("=" * 50)
        print("  Setup complete! Your USB is ready.")
        print("=" * 50)
        print()
        print("To launch Slacker on any computer with Python:")
        print("  Windows : double-click START.bat  (or plug in — AutoPlay will prompt)")
        print("  macOS   : double-click START.command")
        print("  Linux   : run ./START.sh in a terminal")
    else:
        print("\nSetup failed. Check your internet connection and try again.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
