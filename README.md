# Slacker 🧑‍💻☕

> **Want to take a break from work but don't want your boss to think you're slacking?**  
> Slacker is the bot that's always "working" — keeping your status green and your
> screen alive — while you're actually on a well-deserved coffee break.

---

## Features

| Feature | Description |
|---------|-------------|
| 🖱️ **Mouse jitter** | Tiny random mouse movements every N seconds keep your status green in Slack, Teams & more |
| 📜 **Scroll nudge** | A subtle one-tick scroll prevents the screensaver |
| ⌨️ **Shift key press** *(optional)* | Resets stubborn idle timers on some platforms |
| 🪟 **Stealth Widget** | Always-on-top, semi-transparent overlay showing live fake productivity metrics |
| ⚙️ **Fully configurable** | Tweak everything via `config.json` or CLI flags |

---

## Stealth Widget 🕵️

The stealth widget is a **tiny floating overlay** that sits in the corner of your
screen. It shows convincing, auto-updating "productivity" stats so anyone glancing
at your monitor sees an active worker:

```
┌─────────────────────────────┐
│ ● ProductivityBot           │
├─────────────────────────────┤
│ 📧 Emails        14         │
│ ✅ Tasks          6         │
│ 💬 Messages      22         │
│ 🔀 Commits        3         │
│                             │
│ ⟳ Deploying to staging..   │
│                    14:32:05 │
└─────────────────────────────┘
```

- **Semi-transparent** (88% opacity by default — configurable)
- **Always on top** of every other window
- **No title bar** — blends right in
- **Draggable** — click and drag to reposition anywhere
- **Right-click** to hide or quit
- Metrics **slowly increment** at random intervals
- Status line **cycles** through realistic-sounding activities with a typing-dot animation
- Live **clock** in the bottom-right corner

---

## Requirements

- Python 3.8+
- A graphical desktop environment (macOS, Windows, Linux with X11/Wayland)
- `tkinter` — included with most Python installations (the widget uses it)

```bash
pip install -r requirements.txt
```

---

## Quick start

```bash
# Run activity bot with defaults (60-second interval)
python slacker.py

# Run with the stealth widget too — the full "always working" experience
python slacker.py --widget

# 30-second interval, widget anchored to the top-right corner
python slacker.py --interval 30 --widget --widget-position top-right

# Just the widget, no mouse/keyboard automation
python widget.py

# Widget with custom opacity and position
python widget.py --alpha 0.75 --position top-left

# Full help
python slacker.py --help
python widget.py --help
```

---

## Configuration (`config.json`)

### Activity bot

| Key | Default | Description |
|-----|---------|-------------|
| `interval_seconds` | `60` | Seconds between each activity burst |
| `jitter_pixels` | `10` | Max pixels the mouse is nudged in any direction |
| `enable_mouse_movement` | `true` | Move the mouse on each tick |
| `enable_scroll` | `true` | Nudge the scroll wheel on each tick |
| `enable_key_press` | `false` | Press Shift on each tick |
| `log_level` | `"INFO"` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`) |

### Stealth widget

| Key | Default | Description |
|-----|---------|-------------|
| `stealth_widget.enabled` | `false` | Auto-launch widget when running `slacker.py` |
| `stealth_widget.alpha` | `0.88` | Window opacity (0.0 invisible → 1.0 fully opaque) |
| `stealth_widget.position` | `"bottom-right"` | Screen corner: `bottom-right`, `bottom-left`, `top-right`, `top-left` |

Example `config.json` with the widget always enabled:

```json
{
    "interval_seconds": 45,
    "jitter_pixels": 8,
    "enable_mouse_movement": true,
    "enable_scroll": true,
    "enable_key_press": false,
    "log_level": "INFO",
    "stealth_widget": {
        "enabled": true,
        "alpha": 0.80,
        "position": "bottom-right"
    }
}
```

---

## Emergency stop

- Move your mouse to the **top-left corner** of your screen — pyautogui's built-in
  fail-safe will immediately raise an exception and stop Slacker.
- Press **Ctrl+C** in the terminal where Slacker is running.
- **Right-click** the stealth widget and choose **Quit Slacker**.

---

## Disclaimer

Slacker is a fun productivity experiment. Please use it responsibly and in
accordance with your employer's policies. The authors are not responsible for
any workplace consequences arising from its use. 😅
