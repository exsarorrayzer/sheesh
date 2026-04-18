import random
import string
import time
import hashlib

def _rand(k=20):
    return ''.join(random.choices(string.ascii_letters, k=k))

def obfuscate(source: str) -> str:
    timestamp = int(time.time())
    uid = hashlib.md5(f'{timestamp}{random.random()}'.encode()).hexdigest()[:16]
    marker_var = _rand(30)
    watermark_line = f"{marker_var} = '{uid}'\n"
    if '__future__' in source:
        lines = source.splitlines()
        future_lines = []
        other_lines = []
        for line in lines:
            if '__future__' in line and ('import' in line or 'from' in line):
                future_lines.append(line)
            else:
                other_lines.append(line)
        if future_lines:
            return '\n'.join(future_lines) + '\n' + watermark_line + '\n' + '\n'.join(other_lines)
    return watermark_line + source