import sys
from pathlib import Path
from importlib import util

try:
    from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, yes_no_dialog, message_dialog
except ImportError:
    print("[!] prompt_toolkit is required for arrow-key menu. Install via: pip install prompt_toolkit")
    sys.exit(1)

BASE = Path(__file__).resolve().parent.parent
OBF_DIR = BASE / "obsufucators"
RESULT_DIR = BASE.parent / "result"
if not RESULT_DIR.exists():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

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

def start_menu():
    choices = [
        ("base64", "Base64"),
        ("hash", "Hash"),
        ("marshall", "Marshall"),
        ("zlib", "Zlib"),
        ("all", "All (recommended)")
    ]

    result = radiolist_dialog(
        title="Sheesh - Encrypt Menu",
        text="Select encrypt method:",
        values=choices,
        ok_text="Select",
        cancel_text="Exit"
    ).run()
    if result is None:
        return

    file_path = input_dialog(title="Input", text="Path to .py file to obfuscate:").run()
    if not file_path:
        return

    try:
        fp = Path(file_path).expanduser().resolve()
    except Exception:
        message_dialog(title="Error", text="Invalid path").run()
        return
    if not fp.exists() or fp.suffix.lower() != ".py":
        message_dialog(title="Error", text="File must exist and be a .py file").run()
        return
    try:
        src = fp.read_text(encoding="utf-8")
    except Exception as e:
        message_dialog(title="Error", text=f"Cannot read file: {e}").run()
        return

    # Default pipeline
    pipeline = [
        "comment_remover",
        "variable_randomizer",
        "class_randomizer",
        "comment_adder"
    ]
    data = src
    for mod in pipeline:
        data = apply_module_safe(data, mod)

    # Encrypt methods
    encrypt_order = []
    if result == "all":
        encrypt_order = ["base64", "hash", "marshall", "zlib"]
    else:
        encrypt_order = [result]

    for enc in encrypt_order:
        data = apply_module_safe(data, enc)

    # Optional print remover
    yn = yes_no_dialog(title="Print Remove", text="Remove all print() calls?").run()
    if yn:
        data = apply_module_safe(data, "print_hider")

    out_name = f"{fp.stem}_enc.py"
    out_path = RESULT_DIR / out_name
    try:
        out_path.write_text(data, encoding="utf-8")
    except Exception as e:
        message_dialog(title="Error", text=f"Cannot write result: {e}").run()
        return
    message_dialog(title="Done", text=f"Obfuscated file written to:\n{out_path}").run()