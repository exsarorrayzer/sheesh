import random
import string
import os

def _rand(k=12):
    return ''.join(random.choices(string.ascii_letters, k=k))

TEMPLATE = """
import subprocess as {subp}, sys as {sys}, ctypes as {ct}
def {check}():
    try:
        {out} = {subp}.check_output('getmac', shell=True).decode().lower()
        {bad} = {mac_list}
        if any(m in {out} for m in {bad}): {sys}.exit(1)
        if hasattr({ct}, 'windll'):
            {w} = {ct}.windll.user32.GetSystemMetrics(0)
            {h} = {ct}.windll.user32.GetSystemMetrics(1)
            if {w} <= 800 or {h} <= 600: {sys}.exit(1)
    except: pass
{check}()
"""

def get_mac_blacklist():
    default_macs = ['08:00:27', '00:05:69', '00:0c:29', '00:1c:14', '00:50:56', '00:16:3e']
    try:
        # Ana dizindeki mac_blacklist.txt dosyasini bulmaya calis
        # obsufucators klasorunun bir ust dizinine bakar
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        txt_path = os.path.join(base_dir, 'mac_blacklist.txt')
        
        if os.path.exists(txt_path):
            with open(txt_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                macs = [line.strip().lower() for line in lines if line.strip() and not line.startswith('#')]
                if macs:
                    return macs
    except Exception:
        pass
    
    return default_macs

def obfuscate(source: str) -> str:
    mac_list_str = str(get_mac_blacklist())
    
    code = TEMPLATE.format(
        subp=_rand(), sys=_rand(), ct=_rand(), check=_rand(),
        out=_rand(), bad=_rand(), w=_rand(), h=_rand(),
        mac_list=mac_list_str
    ).strip()
    
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
            return '\n'.join(future_lines) + '\n' + code + '\n' + '\n'.join(other_lines)
            
    return code + '\n' + source
