import ast
import random
from typing import Optional

class StrXorTransformer(ast.NodeTransformer):

    def __init__(self, func_name='_d'):
        super().__init__()
        self.func_name = func_name

    def _obf_call(self, s: str) -> ast.AST:
        key = random.randint(1, 255)
        if isinstance(s, bytes):
            b = s
        else:
            b = str(s).encode('utf-8')
        obf = bytes([c ^ key for c in b])
        return ast.Call(func=ast.Name(id=self.func_name, ctx=ast.Load()), args=[ast.Constant(value=obf), ast.Constant(value=key)], keywords=[])

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, (str, bytes)) and node.value:
            return self._obf_call(node.value)
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    func_name = f'_dx{random.randint(1000, 9999)}'
    helper_src = f"def {func_name}(b,k):\n    return bytes([c ^ k for c in b]).decode('utf-8', errors='ignore')\n"
    helper_node = ast.parse(helper_src)
    transformer = StrXorTransformer(func_name)
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    
    # Bug fix: place helper after __future__ imports
    future_idx = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            future_idx = i + 1
        else:
            break
            
    tree.body = tree.body[:future_idx] + helper_node.body + tree.body[future_idx:]
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError('ast.unparse is required (Python 3.9+)')
    return new_source