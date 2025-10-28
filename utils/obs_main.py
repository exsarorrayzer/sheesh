import sys
import os
from pathlib import Path
from importlib import util

try:
    from pick import pick
except Exception:
    print("[!] 'pick' is required for arrow-key menu. Install via: pip install pick")
    sys.exit(1)

try:
    from colorama import init as _cinit, Style
    _cinit()
except Exception:
    Style = None

BASE = Path(__file__).resolve().parent.parent
OBF_DIR = BASE / "obsufucators"
RESULT_DIR = BASE.parent / "result"
if not RESULT_DIR.exists():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = [
    (255, 10, 10),
    (235, 30, 30),
    (210, 20, 20),
    (255, 40, 20),
    (240, 5, 5),
    (255, 80, 20)
]

def _ansi_rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def _color_text(text, idx):
    if Style is None:
        return text
    r, g, b = PALETTE[idx % len(PALETTE)]
    return f"{_ansi_rgb(r,g,b)}{text}{Style.RESET_ALL}"

def discover_module(name):
    path = OBF_DIR / f"{name}.py"
    if not path.exists():
        return None
    spec = util.spec_from_file_location(f"sheesh.obsufucators.{name}", str(path))
    if spec is None:
        return None
    m = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)  # type: ignore
        return m
    except Exception:
        return None

def apply_module_safe(source, module_name):
    m = discover_module(module_name)
    if m is None:
        print(f"[!] missing module: {module_name}")
        return source
    fn = getattr(m, "obfuscate", None)
    if not callable(fn):
        print(f"[!] module has no obfuscate(): {module_name}")
        return source
    try:
        return fn(source)
    except Exception as e:
        print(f"[!] error in {module_name}: {e}")
        return source

def choose_encrypt_method():
    options = [
        ("base64", "Base64"),
        ("hash", "Hash"),
        ("marshall", "Marshall"),
        ("zlib", "Zlib"),
        ("all", "All (recommended)")
    ]
    display = []
    for i, (_, label) in enumerate(options):
        display.append(_color_text(label, i))
    try:
        _, index = pick(display, "Select encrypt method:", indicator="=>")
    except Exception as e:
        print(f"[!] pick failed: {e}")
        return None
    return options[index][0]

def yes_no_prompt(prompt_text):
    labels = ["Yes", "No"]
    display = [_color_text("Yes", 0), _color_text("No", 1)]
    try:
        _, idx = pick(display, prompt_text, indicator="=>")
    except Exception:
        # fallback to simple input if pick unexpectedly fails
        while True:
            try:
                r = input(f"{prompt_text} (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return False
            if r in ("y","yes"):
                return True
            if r in ("n","no"):
                return False
    return idx == 0

def start_menu():
    method = choose_encrypt_method()
    if method is None:
        return
    try:
        file_path = input("Path to .py file to obfuscate: ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not file_path:
        return
    file_path = os.path.expanduser(file_path)
    try:
        fp = Path(file_path).resolve()
    except Exception:
        print("Invalid path")
        return
    if not fp.exists() or fp.suffix.lower() != ".py":
        print("File must exist and be a .py file")
        return
    try:
        src = fp.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Cannot read file: {e}")
        return

    data = src
    data = apply_module_safe(data, "comment_remover")
    yn = yes_no_prompt("Remove all print() calls?")
    if yn:
        data = apply_module_safe(data, "print_hider")
    data = apply_module_safe(data, "variable_randomizer")
    data = apply_module_safe(data, "class_randomizer")

    encrypt_order = []
    if method == "all":
        encrypt_order = ["base64", "hash", "marshall", "zlib"]
    else:
        encrypt_order = [method]

    for enc in encrypt_order:
        data = apply_module_safe(data, enc)

    data = apply_module_safe(data, "comment_adder")

    out_name = f"{fp.stem}_enc.py"
    out_path = RESULT_DIR / out_name
    try:
        out_path.write_text(data, encoding="utf-8")
    except Exception as e:
        print(f"Cannot write result: {e}")
        return

    final_msg = _color_text(f"Obfuscated file written to: {out_path}", 0) if Style else f"Obfuscated file written to: {out_path}"
    print(final_msg)