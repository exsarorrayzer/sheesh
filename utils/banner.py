import os
import sys
import time
import json
from pathlib import Path
import pyfiglet
from colorama import init, Style

init()

def rgb_escape(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def clear_lines(n):
    for _ in range(n):
        sys.stdout.write("\033[F\033[K")

def show_banner():
    base = Path(__file__).resolve().parent
    data_path = base / "data.json"
    version = "v1.0"
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            version = data.get("version", version)
    except Exception:
        pass

    text = "SHEESH"
    fig = pyfiglet.Figlet(font="bloody")
    banner = fig.renderText(text)
    lines = banner.splitlines()
    line_count = len(lines) + 3

    shades = [
        (255, 10, 10),
        (235, 30, 30),
        (210, 20, 20),
        (255, 40, 20),
        (240, 5, 5),
        (255, 80, 20)
    ]

    try:
        cols = os.get_terminal_size().columns
    except Exception:
        cols = 80

    cycles = 4
    delay = 0.08
    for cycle in range(cycles):
        r, g, b = shades[cycle % len(shades)]
        esc = rgb_escape(r, g, b)
        for shift in range(0, max(1, min(10, cols//20))):
            prefix = " " * shift
            for ln in lines:
                sys.stdout.write(esc + prefix + ln + Style.RESET_ALL + "\n")
            sys.stdout.write(esc + prefix + "      ───────────────────────────────" + Style.RESET_ALL + "\n")
            sys.stdout.write(esc + prefix + f"           Sheesh Obfuscator {version}" + Style.RESET_ALL + "\n")
            sys.stdout.flush()
            time.sleep(delay)
            clear_lines(line_count)
    esc = rgb_escape(255, 20, 20)
    for ln in lines:
        sys.stdout.write(esc + ln + Style.RESET_ALL + "\n")
    sys.stdout.write(esc + "      ───────────────────────────────" + Style.RESET_ALL + "\n")
    sys.stdout.write(esc + f"           Sheesh Obfuscator {version}" + Style.RESET_ALL + "\n")
    sys.stdout.flush()
    time.sleep(0.5)