import ast
import random
from typing import Optional

class StrXorTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()

    def _obf_call(self, s: str) -> ast.AST:
        key = random.randint(1, 255)
        b = s.encode("utf-8")
        obf = bytes([c ^ key for c in b])
        return ast.Call(func=ast.Name(id="_d", ctx=ast.Load()), args=[ast.Constant(value=obf), ast.Constant(value=key)], keywords=[])

    def visit_Module(self, node: ast.Module) -> ast.AST:
        new_body = []
        for i, stmt in enumerate(node.body):
            if i == 0 and isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                new_body.append(stmt)
            else:
                new_body.append(self.visit(stmt))
        node.body = new_body
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            doc = node.body[0]
            rest = [self.visit(n) for n in node.body[1:]]
            node.body = [doc] + rest
            return node
        node.body = [self.visit(n) for n in node.body]
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            doc = node.body[0]
            rest = [self.visit(n) for n in node.body[1:]]
            node.body = [doc] + rest
            return node
        node.body = [self.visit(n) for n in node.body]
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str):
            return self._obf_call(node.value)
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    helper_src = "def _d(b,k):\n    return bytes([c ^ k for c in b]).decode('utf-8', errors='ignore')\n"
    helper_node = ast.parse(helper_src)
    transformer = StrXorTransformer()
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    tree.body = helper_node.body + tree.body
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError("ast.unparse is required (Python 3.9+)")
    return new_source