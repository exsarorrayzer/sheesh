# obsufucators/comment_adder.py
import hashlib
import random
import string
import time

random.seed(time.time_ns())

def _random_str(min_len=16, max_len=32):
    length = random.randint(min_len, max_len)
    return ''.join(random.choices(string.ascii_letters, k=length))

def obfuscate(source: str) -> str:
    new_lines = []
    for line in source.splitlines():
        if not line.strip():
            new_lines.append(line)
            continue
        rand_text = _random_str()
        md5_hash = hashlib.md5(rand_text.encode()).hexdigest()
        new_lines.append(f"{line}  # {md5_hash}")
    return "\n".join(new_lines)