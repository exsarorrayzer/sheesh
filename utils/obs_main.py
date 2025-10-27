# sheesh/utils/obs_main.py
import os
import sys
import json
from pathlib import Path
from importlib import util
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog
from prompt_toolkit.application import run_in_terminal

BASE = Path(__file__).resolve().parent.parent
OBF_DIR = BASE / "obsufucators"
RESULT_DIR = BASE.parent / "result"
if not RESULT_DIR.exists():
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

def _discover_obfuscators():
    modules = []
    if not OBF_DIR.exists():
        return modules
    for p in sorted(OBF_DIR.iterdir()):
        if p.is_file() and p.suffix == ".py":
            name = p.stem
            modules.append((name, p))
    return modules

def _load_module_from_path(name, path):
    spec = util.spec_from_file_location(f"sheesh.obsufucators.{name}", str(path))
    if spec is None:
        return None
    m = util.module_from_spec(spec)
    try:
        spec.loader.exec_module(m)  # type: ignore
        return m
    except Exception:
        return None

def _apply_obfuscators(source, modules_to_apply):
    data = source
    for name, path in modules_to_apply:
        m = _load_module_from_path(name, path)
        if m is None:
            run_in_terminal(lambda: print(f"[!] Module load failed: {name}"))
            continue
        fn = getattr(m, "obfuscate", None)
        if not callable(fn):
            run_in_terminal(lambda: print(f"[!] Module missing 'obfuscate' func: {name}"))
            continue
        try:
            data = fn(data)
        except Exception as e:
            run_in_terminal(lambda: print(f"[!] Module error ({name}): {e}"))
    return data

def start_menu():
    mods = _discover_obfuscators()
    if not mods:
        message_dialog(title="Error", text="No obfuscators found in obsufucators/").run()
        return
    choices = [("all", "All (apply every obfuscator in sequence)")]
    for name, _ in mods:
        choices.append((name, name))
    result = radiolist_dialog(
        title="Sheesh - Obfuscator Menu",
        text="Select mode:",
        values=choices,
        ok_text="Select",
        cancel_text="Exit",
    ).run()
    if result is None:
        return
    if result == "all":
        selection = mods
    else:
        selection = [(name, path) for (name, path) in mods if name == result]
    file_path = input_dialog(title="Input", text="Path to .py file to obfuscate:").run()
    if not file_path:
        return
    fp = Path(file_path).expanduser().resolve()
    if not fp.exists() or fp.suffix.lower() != ".py":
        message_dialog(title="Error", text="File must exist and be a .py file").run()
        return
    try:
        src = fp.read_text(encoding="utf-8")
    except Exception as e:
        message_dialog(title="Error", text=f"Cannot read file: {e}").run()
        return
    obf_src = _apply_obfuscators(src, selection)
    out_name = f"{fp.stem}_enc.py"
    out_path = RESULT_DIR / out_name
    try:
        out_path.write_text(obf_src, encoding="utf-8")
    except Exception as e:
        message_dialog(title="Error", text=f"Cannot write result: {e}").run()
        return
    message_dialog(title="Done", text=f"Obfuscated file written to:\n{out_path}").run()