import random
import string

def _rand(k=12):
    return ''.join(random.choices(string.ascii_letters, k=k))
ANTI_DEBUG_TEMPLATE = "\nimport sys as {sys_alias}\nimport os as {os_alias}\n\ndef {check_func}():\n    try:\n        if {sys_alias}.gettrace() is not None:\n            {os_alias}._exit(1)\n    except Exception:\n        pass\n    try:\n        import ctypes as {ct_alias}\n        {k_alias} = {ct_alias}.windll.kernel32\n        if {k_alias}.IsDebuggerPresent():\n            {os_alias}._exit(1)\n    except Exception:\n        pass\n    {dbg_mods} = ['pydevd', 'pdb', 'debugpy', 'pydevd_tracing']\n    for {m_var} in {dbg_mods}:\n        if {m_var} in {sys_alias}.modules:\n            {os_alias}._exit(1)\n    try:\n        import platform as {plat_alias}\n        {hostname} = {plat_alias}.node().lower()\n        {bad_hosts} = ['sandbox', 'malware', 'virus', 'analysis', 'cuckoo', 'threat']\n        for {bh_var} in {bad_hosts}:\n            if {bh_var} in {hostname}:\n                {os_alias}._exit(1)\n    except Exception:\n        pass\n\n{check_func}()\n"

def obfuscate(source: str) -> str:
    vars_map = {'sys_alias': _rand(15), 'os_alias': _rand(15), 'check_func': _rand(20), 'ct_alias': _rand(10), 'k_alias': _rand(10), 'dbg_mods': _rand(12), 'm_var': _rand(8), 'plat_alias': _rand(12), 'hostname': _rand(10), 'bad_hosts': _rand(12), 'bh_var': _rand(8)}
    anti_debug_code = ANTI_DEBUG_TEMPLATE.format(**vars_map).strip()
    
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
            return '\n'.join(future_lines) + '\n' + anti_debug_code + '\n' + '\n'.join(other_lines)
            
    return anti_debug_code + '\n' + source