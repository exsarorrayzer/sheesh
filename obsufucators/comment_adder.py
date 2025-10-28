import random
import string
import time

random.seed(time.time_ns())

def _rand128():
    return ''.join(random.choices(string.ascii_letters, k=128))

def obfuscate(source: str) -> str:
    out_lines = []
    for line in source.splitlines():
        out_lines.append(line)
        if not line.strip():
            continue
        block = _rand128()
        chunk_size = 8
        chunks = [block[i:i+chunk_size] for i in range(0, 128, chunk_size)]
        for ch in chunks:
            out_lines.append(f"# {ch}")
    return "\n".join(out_lines)