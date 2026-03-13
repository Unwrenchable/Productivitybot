"""
Slacker — the bot that keeps you looking busy while you take a break.

Features
--------
* Moves the mouse in small random jitters so your status stays "Active" in
  Slack, Teams, and similar tools.
* Optionally scrolls or presses a harmless key (Shift) to prevent screen savers
  and OS idle timers.
* --widget: launches the Stealth Widget, a tiny always-on-top dashboard
  showing fake-but-convincing productivity metrics.
* Fully configurable via config.json.

Usage
-----
    python slacker.py                 # run with defaults from config.json
    python slacker.py --interval 30   # override interval (seconds)
    python slacker.py --widget        # also show the stealth widget
    python slacker.py --help
"""

import argparse
import json
import logging
import os
import random
import signal
import sys
import threading
import time

try:
    import pyautogui
except ImportError:
    print(
        "pyautogui is not installed. Run:  pip install pyautogui",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    import schedule
except ImportError:
    print(
        "schedule is not installed. Run:  pip install schedule",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Defaults (overridden by config.json, then by CLI flags)
# ---------------------------------------------------------------------------
DEFAULTS = {
    "interval_seconds": 60,
    "jitter_pixels": 10,
    "enable_mouse_movement": True,
    "enable_scroll": True,
    "enable_key_press": False,
    "log_level": "INFO",
    "stealth_widget": {
        "enabled": False,
        "alpha": 0.88,
        "position": "bottom-right",
    },
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    """Load and merge config.json with DEFAULTS."""
    cfg = dict(DEFAULTS)
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fh:
            file_cfg = json.load(fh)
        cfg.update(file_cfg)
    return cfg


def setup_logging(level_name: str) -> None:
    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        level=level,
    )


# ---------------------------------------------------------------------------
# Activity actions
# ---------------------------------------------------------------------------

def jitter_mouse(pixels: int) -> None:
    """Move the mouse by a tiny random offset and then back."""
    dx = random.randint(-pixels, pixels)
    dy = random.randint(-pixels, pixels)
    current_x, current_y = pyautogui.position()
    pyautogui.moveRel(dx, dy, duration=0.2)
    time.sleep(0.1)
    pyautogui.moveTo(current_x, current_y, duration=0.2)
    logging.debug("Mouse jitter: dx=%d, dy=%d", dx, dy)


def scroll_nudge() -> None:
    """Scroll the mouse wheel one tick up then back down."""
    pyautogui.scroll(1)
    time.sleep(0.05)
    pyautogui.scroll(-1)
    logging.debug("Scroll nudge applied.")


def press_shift() -> None:
    """Press the Shift key — harmless and resets most idle timers."""
    pyautogui.press("shift")
    logging.debug("Shift key pressed.")


# ---------------------------------------------------------------------------
# Scheduled job
# ---------------------------------------------------------------------------

def activity_tick(cfg: dict) -> None:
    """Perform one round of simulated activity based on the current config."""
    logging.info("Slacker is active — keeping things looking busy…")

    if cfg["enable_mouse_movement"]:
        jitter_mouse(cfg["jitter_pixels"])

    if cfg["enable_scroll"]:
        scroll_nudge()

    if cfg["enable_key_press"]:
        press_shift()


# ---------------------------------------------------------------------------
# Signal handling for clean exit
# ---------------------------------------------------------------------------

_running = True


def _handle_signal(signum, frame):  # noqa: ARG001
    global _running
    logging.info("Signal %d received — shutting down Slacker. Goodbye!", signum)
    _running = False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Slacker — look busy while you take a well-deserved break."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=None,
        metavar="SECONDS",
        help="Override the activity interval in seconds (default: from config.json).",
    )
    parser.add_argument(
        "--jitter",
        type=int,
        default=None,
        metavar="PIXELS",
        help="Override the mouse-jitter range in pixels (default: from config.json).",
    )
    parser.add_argument(
        "--no-mouse",
        action="store_true",
        default=False,
        help="Disable mouse movement.",
    )
    parser.add_argument(
        "--no-scroll",
        action="store_true",
        default=False,
        help="Disable scroll nudges.",
    )
    parser.add_argument(
        "--key-press",
        action="store_true",
        default=False,
        help="Enable Shift key presses (disabled by default).",
    )
    parser.add_argument(
        "--config",
        default=CONFIG_PATH,
        metavar="FILE",
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--widget",
        action="store_true",
        default=False,
        help="Show the stealth productivity widget (always-on-top overlay).",
    )
    parser.add_argument(
        "--widget-alpha",
        type=float,
        default=None,
        metavar="0.0-1.0",
        help="Widget opacity override (0.0 invisible → 1.0 opaque). Default: from config.json.",
    )
    parser.add_argument(
        "--widget-position",
        choices=["bottom-right", "bottom-left", "top-right", "top-left"],
        default=None,
        help="Screen corner for the widget. Default: from config.json.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    cfg = load_config(args.config)

    # Apply CLI overrides
    if args.interval is not None:
        cfg["interval_seconds"] = args.interval
    if args.jitter is not None:
        cfg["jitter_pixels"] = args.jitter
    if args.no_mouse:
        cfg["enable_mouse_movement"] = False
    if args.no_scroll:
        cfg["enable_scroll"] = False
    if args.key_press:
        cfg["enable_key_press"] = True

    widget_cfg = cfg.setdefault("stealth_widget", dict(DEFAULTS["stealth_widget"]))
    if args.widget:
        widget_cfg["enabled"] = True
    if args.widget_alpha is not None:
        widget_cfg["alpha"] = args.widget_alpha
    if args.widget_position is not None:
        widget_cfg["position"] = args.widget_position

    setup_logging(cfg.get("log_level", "INFO"))

    pyautogui.FAILSAFE = True  # keep it on so the user can still emergency-stop

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    logging.info(
        "Slacker started. Interval: %ss | Jitter: %dpx | Mouse: %s | Scroll: %s | Key: %s | Widget: %s",
        cfg["interval_seconds"],
        cfg["jitter_pixels"],
        cfg["enable_mouse_movement"],
        cfg["enable_scroll"],
        cfg["enable_key_press"],
        widget_cfg["enabled"],
    )
    logging.info("Move your mouse to the top-left corner to emergency-stop.")

    # Launch the stealth widget in a background thread (tkinter must own its thread)
    if widget_cfg["enabled"]:
        try:
            from widget import run_widget  # noqa: PLC0415
        except ImportError:
            logging.warning("widget.py not found — skipping stealth widget.")
        else:
            t = threading.Thread(
                target=run_widget,
                kwargs={
                    "alpha": widget_cfg.get("alpha", 0.88),
                    "position": widget_cfg.get("position", "bottom-right"),
                },
                daemon=True,
            )
            t.start()

    # Run once immediately, then on schedule
    activity_tick(cfg)
    schedule.every(cfg["interval_seconds"]).seconds.do(activity_tick, cfg)

    while _running:
        schedule.run_pending()
        time.sleep(1)

    logging.info("Slacker stopped.")


if __name__ == "__main__":
    main()
