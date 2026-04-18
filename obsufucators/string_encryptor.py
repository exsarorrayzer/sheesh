import ast
import random
import struct

class StringEncryptor(ast.NodeTransformer):

    def __init__(self):
        super().__init__()
        self.key_var = f'_k{random.randint(1000, 9999)}'
        self.dec_var = f'_s{random.randint(1000, 9999)}'
        self.key = random.randint(65536, 16777215)
        self._in_joined_str = False

    def _encrypt_string(self, s):
        key_bytes = struct.pack('>I', self.key)
        encoded = s.encode('utf-8')
        result = bytearray()
        for i, b in enumerate(encoded):
            result.append(b ^ key_bytes[i % len(key_bytes)])
        return bytes(result)

    def _make_decrypt_call(self, s):
        encrypted = self._encrypt_string(s)
        return ast.Call(func=ast.Name(id=self.dec_var, ctx=ast.Load()), args=[ast.Constant(value=encrypted), ast.Constant(value=self.key)], keywords=[])

    def visit_Module(self, node):
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            doc = node.body[0]
            rest = [self.visit(n) for n in node.body[1:]]
            node.body = [doc] + rest
            return node
        node.body = [self.visit(n) for n in node.body]
        return node

    def visit_ClassDef(self, node):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            doc = node.body[0]
            rest = [self.visit(n) for n in node.body[1:]]
            node.body = [doc] + rest
            return node
        node.body = [self.visit(n) for n in node.body]
        return node

    def visit_JoinedStr(self, node):
        old = self._in_joined_str
        self._in_joined_str = True
        self.generic_visit(node)
        self._in_joined_str = old
        return node

    def visit_FormattedValue(self, node):
        old = self._in_joined_str
        self._in_joined_str = False
        self.visit(node.value)
        self._in_joined_str = old
        if node.format_spec:
            self.visit(node.format_spec)
        return node

    def visit_Constant(self, node):
        if self._in_joined_str:
            return node
        if isinstance(node.value, str) and len(node.value) > 0:
            return self._make_decrypt_call(node.value)
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    enc = StringEncryptor()
    tree = enc.visit(tree)
    ast.fix_missing_locations(tree)
    helper = f"import struct as _st\ndef {enc.dec_var}(_b, _k):\n    _kb = _st.pack('>I', _k)\n    return bytes([c ^ _kb[i % len(_kb)] for i, c in enumerate(_b)]).decode('utf-8', errors='ignore')\n"
    helper_tree = ast.parse(helper)
    
    # Bug fix: place helper after __future__ imports
    future_idx = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            future_idx = i + 1
        else:
            break
            
    tree.body = tree.body[:future_idx] + helper_tree.body + tree.body[future_idx:]
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except AttributeError:
        raise RuntimeError('ast.unparse required (Python 3.9+)')