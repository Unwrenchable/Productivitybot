"""
Slacker Stealth Widget — a tiny always-on-top productivity dashboard
that quietly "proves" you're working while you enjoy your break.

The widget shows live-updating fake metrics (emails, tasks, messages, commits),
a rotating status line with a typing-dot animation, and a live clock.
It is semi-transparent, has no title bar, and stays on top of every other window.

Run standalone:
    python widget.py [--alpha 0.88] [--position bottom-right]

Or launch together with the activity bot via slacker.py:
    python slacker.py --widget
"""

import argparse
import random
import sys
import time
import tkinter as tk
from itertools import cycle

# ---------------------------------------------------------------------------
# Fake content pools
# ---------------------------------------------------------------------------

_STATUSES = [
    "Syncing workspace",
    "Processing pipeline",
    "Resolving dependencies",
    "Compiling changes",
    "Running test suite",
    "Fetching updates",
    "Optimizing queries",
    "Pushing to remote",
    "Reviewing pull request",
    "Deploying to staging",
    "Analyzing metrics",
    "Merging branches",
    "Rebuilding indexes",
    "Refreshing cache",
    "Generating report",
]

_METRIC_KEYS = ["Emails", "Tasks", "Messages", "Commits"]

_METRIC_ICONS = {
    "Emails": "📧",
    "Tasks": "✅",
    "Messages": "💬",
    "Commits": "🔀",
}

# (min_delta, max_delta) added per update tick
_METRIC_DELTAS = {
    "Emails": (0, 2),
    "Tasks": (0, 1),
    "Messages": (0, 3),
    "Commits": (0, 1),
}

# ---------------------------------------------------------------------------
# Widget
# ---------------------------------------------------------------------------

_POSITIONS = ("bottom-right", "bottom-left", "top-right", "top-left")


class StealthWidget:
    """The stealth productivity dashboard window."""

    # Theme colours (Catppuccin-inspired dark palette)
    BG = "#1e1e2e"
    HEADER_BG = "#313244"
    FG = "#cdd6f4"
    ACCENT = "#a6e3a1"
    ACCENT_BLUE = "#89b4fa"
    DIM = "#6c7086"

    FONT_MONO = ("Courier New", 9)
    FONT_MONO_BOLD = ("Courier New", 9, "bold")
    FONT_TITLE = ("Courier New", 10, "bold")

    WIDTH = 215
    HEIGHT = 178
    MARGIN = 20  # distance from screen edge

    def __init__(self, root: tk.Tk, alpha: float = 0.88, position: str = "bottom-right"):
        self.root = root
        self._alpha = max(0.1, min(1.0, alpha))
        self._position = position if position in _POSITIONS else "bottom-right"

        # Initialise fake metric counters
        self._metrics: dict[str, int] = {
            k: random.randint(3, 18) for k in _METRIC_KEYS
        }
        # Shuffle status list for variety each run
        shuffled = random.sample(_STATUSES, len(_STATUSES))
        self._status_cycle = cycle(shuffled)
        self._current_status = next(self._status_cycle)
        self._dot_count = 0

        # Drag state
        self._drag_x = 0
        self._drag_y = 0

        self._setup_window()
        self._build_ui()
        self._schedule_updates()

    # ------------------------------------------------------------------
    # Window setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        root = self.root
        root.overrideredirect(True)          # no title bar / decorations
        root.attributes("-topmost", True)    # always on top
        root.attributes("-alpha", self._alpha)
        root.configure(bg=self.BG)
        root.resizable(False, False)

        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        w, h, m = self.WIDTH, self.HEIGHT, self.MARGIN
        positions = {
            "bottom-right": (sw - w - m, sh - h - 60),
            "bottom-left":  (m, sh - h - 60),
            "top-right":    (sw - w - m, m),
            "top-left":     (m, m),
        }
        x, y = positions[self._position]
        root.geometry(f"{w}x{h}+{x}+{y}")

        # Drag support (bind to root so the whole window is draggable)
        root.bind("<Button-1>", self._drag_start)
        root.bind("<B1-Motion>", self._drag_move)

        # Right-click context menu
        self._ctx_menu = tk.Menu(
            root,
            tearoff=0,
            bg=self.HEADER_BG,
            fg=self.FG,
            activebackground="#45475a",
            activeforeground=self.FG,
            bd=0,
            font=self.FONT_MONO,
        )
        self._ctx_menu.add_command(label="Hide widget", command=root.withdraw)
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(label="Quit Slacker", command=root.destroy)
        root.bind("<Button-3>", self._show_menu)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Header bar ──────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=self.HEADER_BG, height=24)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        header.bind("<Button-1>", self._drag_start)
        header.bind("<B1-Motion>", self._drag_move)

        tk.Label(
            header,
            text="● ProductivityBot",
            bg=self.HEADER_BG,
            fg=self.ACCENT,
            font=self.FONT_TITLE,
            anchor="w",
            padx=8,
        ).pack(side=tk.LEFT, fill=tk.Y)

        # ── Metrics ─────────────────────────────────────────────────────
        metrics_frame = tk.Frame(self.root, bg=self.BG, padx=10, pady=5)
        metrics_frame.pack(fill=tk.X)

        self._metric_labels: dict[str, tk.Label] = {}
        for key in _METRIC_KEYS:
            row = tk.Frame(metrics_frame, bg=self.BG)
            row.pack(fill=tk.X, pady=1)

            tk.Label(
                row,
                text=_METRIC_ICONS[key],
                bg=self.BG,
                fg=self.FG,
                font=self.FONT_MONO,
                width=2,
                anchor="w",
            ).pack(side=tk.LEFT)

            tk.Label(
                row,
                text=f"{key:<10}",
                bg=self.BG,
                fg=self.DIM,
                font=self.FONT_MONO,
                anchor="w",
            ).pack(side=tk.LEFT)

            val_lbl = tk.Label(
                row,
                text=str(self._metrics[key]),
                bg=self.BG,
                fg=self.ACCENT,
                font=self.FONT_MONO_BOLD,
                anchor="e",
                width=4,
            )
            val_lbl.pack(side=tk.RIGHT)
            self._metric_labels[key] = val_lbl

        # ── Divider ─────────────────────────────────────────────────────
        tk.Frame(self.root, bg=self.HEADER_BG, height=1).pack(fill=tk.X, padx=8)

        # ── Status line ─────────────────────────────────────────────────
        status_frame = tk.Frame(self.root, bg=self.BG, padx=10, pady=4)
        status_frame.pack(fill=tk.X)

        self._status_lbl = tk.Label(
            status_frame,
            text="",
            bg=self.BG,
            fg=self.ACCENT_BLUE,
            font=self.FONT_MONO,
            anchor="w",
            wraplength=self.WIDTH - 20,
            justify=tk.LEFT,
        )
        self._status_lbl.pack(fill=tk.X)

        # ── Clock ────────────────────────────────────────────────────────
        clock_frame = tk.Frame(self.root, bg=self.BG, padx=10)
        clock_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 5))

        self._clock_lbl = tk.Label(
            clock_frame,
            text="",
            bg=self.BG,
            fg=self.DIM,
            font=self.FONT_MONO,
            anchor="e",
        )
        self._clock_lbl.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Drag handlers
    # ------------------------------------------------------------------

    def _drag_start(self, event: tk.Event) -> None:
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _drag_move(self, event: tk.Event) -> None:
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _show_menu(self, event: tk.Event) -> None:
        self._ctx_menu.tk_popup(event.x_root, event.y_root)

    # ------------------------------------------------------------------
    # Periodic update helpers
    # ------------------------------------------------------------------

    def _schedule_updates(self) -> None:
        """Kick off all recurring update loops."""
        self._update_clock()
        self._update_status()
        self._update_metrics()

    def _update_clock(self) -> None:
        self._clock_lbl.config(text=time.strftime("%H:%M:%S"))
        self.root.after(1000, self._update_clock)

    def _update_status(self) -> None:
        """Animate a typing-dot suffix; advance status every 4 seconds."""
        self._dot_count = (self._dot_count + 1) % 4
        dots = "." * self._dot_count
        self._status_lbl.config(text=f"⟳ {self._current_status}{dots}")
        if self._dot_count == 0:
            self._current_status = next(self._status_cycle)
        self.root.after(1000, self._update_status)

    def _update_metrics(self) -> None:
        """Randomly increment one metric and reschedule."""
        key = random.choice(_METRIC_KEYS)
        lo, hi = _METRIC_DELTAS[key]
        self._metrics[key] += random.randint(lo, hi)
        self._metric_labels[key].config(text=str(self._metrics[key]))
        self.root.after(random.randint(5000, 15000), self._update_metrics)


# ---------------------------------------------------------------------------
# Public launcher
# ---------------------------------------------------------------------------

def run_widget(alpha: float = 0.88, position: str = "bottom-right") -> None:
    """Launch the stealth widget (blocking — run in main thread or dedicated thread)."""
    root = tk.Tk()
    StealthWidget(root, alpha=alpha, position=position)
    root.mainloop()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Slacker Stealth Widget — look busy while you take a break."
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.88,
        metavar="0.0-1.0",
        help="Window opacity (0.0 = invisible, 1.0 = fully opaque). Default: 0.88",
    )
    parser.add_argument(
        "--position",
        choices=_POSITIONS,
        default="bottom-right",
        help="Corner of the screen to anchor the widget. Default: bottom-right",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = _parse_args()
    run_widget(alpha=args.alpha, position=args.position)
