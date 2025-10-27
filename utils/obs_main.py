import sys
from pathlib import Path
from importlib import util

try:
    from pick import pick
except Exception:
    print("[!] 'pick' is required for arrow-key menu. Install via: pip install pick")
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

def choose_encrypt_method():
    options = [
        ("base64", "Base64"),
        ("hash", "Hash"),
        ("marshall", "Marshall"),
        ("zlib", "Zlib"),
        ("all", "All (recommended)")
    ]
    labels = [lbl for _, lbl in options]
    option, index = pick(labels, "Select encrypt method:", indicator="=>")
    return options[index][0]

def yes_no_prompt(prompt_text):
    labels = ["Yes", "No"]
    _, idx = pick(labels, prompt_text, indicator="=>")
    return idx == 0

def start_menu():
    method = choose_encrypt_method()
    try:
        file_path = input("Path to .py file to obfuscate: ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not file_path:
        return
    try:
        fp = Path(file_path).expanduser().resolve()
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
    if method == "all":
        encrypt_order = ["base64", "hash", "marshall", "zlib"]
    else:
        encrypt_order = [method]

    for enc in encrypt_order:
        data = apply_module_safe(data, enc)

    yn = yes_no_prompt("Remove all print() calls?")
    if yn:
        data = apply_module_safe(data, "print_hider")

    out_name = f"{fp.stem}_enc.py"
    out_path = RESULT_DIR / out_name
    try:
        out_path.write_text(data, encoding="utf-8")
    except Exception as e:
        print(f"Cannot write result: {e}")
        return
    print(f"Obfuscated file written to: {out_path}")