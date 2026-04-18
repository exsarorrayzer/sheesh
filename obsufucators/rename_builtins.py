import random
import string
BUILTINS_TO_ALIAS = ['print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'tuple', 'set', 'bool', 'type', 'isinstance', 'hasattr', 'getattr', 'setattr', 'delattr', 'input', 'open', 'sorted', 'reversed', 'enumerate', 'zip', 'map', 'filter', 'sum', 'min', 'max', 'abs', 'round', 'hex', 'oct', 'bin', 'chr', 'ord', 'repr', 'hash', 'id', 'dir', 'vars', 'any', 'all', 'format', 'iter', 'next', 'super', 'property', 'staticmethod', 'classmethod']

def _rand(k=20):
    return ''.join(random.choices(string.ascii_letters, k=k))

def obfuscate(source: str) -> str:
    used_builtins = []
    for b in BUILTINS_TO_ALIAS:
        if b in source:
            used_builtins.append(b)
    if not used_builtins:
        return source
    aliases = {}
    header_lines = []
    for b in used_builtins:
        alias = _rand(25)
        aliases[b] = alias
        header_lines.append(f'{alias} = {b}')
    for original, alias in aliases.items():
        parts = source.split(original)
        new_parts = []
        for i, part in enumerate(parts):
            new_parts.append(part)
            if i < len(parts) - 1:
                before = parts[i][-1:] if parts[i] else ''
                after = parts[i + 1][:1] if parts[i + 1] else ''
                is_word_boundary_before = not before.isalnum() and before != '_'
                is_word_boundary_after = not after.isalnum() and after != '_'
                if (not before or is_word_boundary_before) and (not after or is_word_boundary_after):
                    new_parts.append(alias)
                else:
                    new_parts.append(original)
        source = ''.join(new_parts)
    header = '\n'.join(header_lines) + '\n'
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
            return '\n'.join(future_lines) + '\n' + header + '\n' + '\n'.join(other_lines)
    return header + source