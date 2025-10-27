import os
import sys
from pathlib import Path
from importlib import util

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

def fallback_menu(choices):
    print("Select encrypt method:")
    for i, (_, label) in enumerate(choices, 1):
        print(f"  {i}) {label}")
    while True:
        try:
            sel = input("Choice number (or empty to exit): ").strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if sel == "":
            return None
        if not sel.isdigit():
            print("Enter a number")
            continue
        idx = int(sel) - 1
        if 0 <= idx < len(choices):
            return choices[idx][0]
        print("Invalid choice")

def prompt_yes_no(text):
    try:
        from prompt_toolkit.shortcuts import yes_no_dialog
        return yes_no_dialog(title="Print Remove", text=text).run()
    except Exception:
        while True:
            try:
                r = input(f"{text} (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                return False
            if r in ("y", "yes"):
                return True
            if r in ("n", "no"):
                return False

def start_menu():
    choices = [
        ("base64", "Base64"),
        ("hash", "Hash"),
        ("marshall", "Marshall"),
        ("zlib", "Zlib"),
        ("all", "All (recommended)")
    ]

    use_prompt = True
    try:
        from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog
    except Exception:
        use_prompt = False

    if use_prompt:
        result = radiolist_dialog(
            title="Sheesh - Encrypt Menu",
            text="Select encrypt method:",
            values=choices,
            ok_text="Select",
            cancel_text="Exit"
        ).run()
    else:
        result = fallback_menu(choices)
    if result is None:
        return

    if use_prompt:
        fp_input = input_dialog(title="Input", text="Path to .py file to obfuscate:").run()
        if not fp_input:
            return
        file_path = fp_input
    else:
        try:
            file_path = input("Path to .py file to obfuscate: ").strip()
        except (EOFError, KeyboardInterrupt):
            return
        if not file_path:
            return

    try:
        fp = Path(file_path).expanduser().resolve()
    except Exception:
        if use_prompt:
            from prompt_toolkit.shortcuts import message_dialog
            message_dialog(title="Error", text="Invalid path").run()
        else:
            print("Invalid path")
        return
    if not fp.exists() or fp.suffix.lower() != ".py":
        if use_prompt:
            from prompt_toolkit.shortcuts import message_dialog
            message_dialog(title="Error", text="File must exist and be a .py file").run()
        else:
            print("File must exist and be a .py file")
        return
    try:
        src = fp.read_text(encoding="utf-8")
    except Exception as e:
        if use_prompt:
            from prompt_toolkit.shortcuts import message_dialog
            message_dialog(title="Error", text=f"Cannot read file: {e}").run()
        else:
            print(f"Cannot read file: {e}")
        return

    pipeline = [
        "comment_remover",
        "variable_randomizer",
        "class_randomizer",
        "comment_adder"
    ]
    data = src
    for mod in pipeline:
        data = apply_module_safe(data, mod)

    encrypt_order = []
    if result == "all":
        encrypt_order = ["base64", "hash", "marshall", "zlib"]
    else:
        encrypt_order = [result]

    for enc in encrypt_order:
        data = apply_module_safe(data, enc)

    yn = prompt_yes_no("Remove all print() calls?")
    if yn:
        data = apply_module_safe(data, "print_hider")

    out_name = f"{fp.stem}_enc.py"
    out_path = RESULT_DIR / out_name
    try:
        out_path.write_text(data, encoding="utf-8")
    except Exception as e:
        if use_prompt:
            from prompt_toolkit.shortcuts import message_dialog
            message_dialog(title="Error", text=f"Cannot write result: {e}").run()
        else:
            print(f"Cannot write result: {e}")
        return
    if use_prompt:
        from prompt_toolkit.shortcuts import message_dialog
        message_dialog(title="Done", text=f"Obfuscated file written to:\n{out_path}").run()
    else:
        print(f"Obfuscated file written to: {out_path}")