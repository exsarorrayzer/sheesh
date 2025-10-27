import json
from pathlib import Path
from time import sleep
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.box import ROUNDED

def show_creds():
    base = Path(__file__).resolve().parent
    data_path = base / "data.json"
    console = Console()
    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        console.print("[bold red]Error:[/bold red] Cannot read data.json")
        return

    name = data.get("name", "Unknown")
    info_lines = []
    for k, v in data.items():
        if k.lower() != "name":
            info_lines.append(f"[bold]{k.capitalize()}:[/bold] {v}")
    body = "\n".join(info_lines)

    panel = Panel(Align.center(body), title=Text(name, style="bold red"), box=ROUNDED, border_style="red")
    console.print(panel)
    sleep(0.6)