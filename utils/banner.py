import os
import sys
import time
import json
from pathlib import Path
import pyfiglet
from colorama import init, Style

init(autoreset=True)

def rgb(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}{Style.RESET_ALL}"

def glide_print(lines, delay=0.02):
    term_width = os.get_terminal_size().columns
    for offset in range(term_width):
        sys.stdout.write("\r" + " " * offset + lines)
        sys.stdout.flush()
        time.sleep(delay / 5)
    print()

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

    shades = [
        (255, 0, 0),
        (235, 20, 20),
        (210, 10, 10),
        (255, 40, 40),
        (240, 5, 5),
        (255, 80, 20)
    ]

    os.system("cls" if os.name == "nt" else "clear")

    for i in range(4):
        r, g, b = shades[i % len(shades)]
        colored = "\n".join([rgb(r, g, b, line) for line in lines])
        glide_print(colored, delay=0.01)
        time.sleep(0.18)
        os.system("cls" if os.name == "nt" else "clear")

    final_banner = "\n".join([rgb(255, 30, 30, line) for line in lines])
    print(final_banner)
    print(rgb(255, 60, 60, "      ───────────────────────────────"))
    print(rgb(255, 30, 30, f"           Sheesh Obfuscator {version}"))
    print(rgb(255, 60, 60, "      ───────────────────────────────"))
    time.sleep(0.5)