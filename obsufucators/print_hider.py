# obsufucators/print_hider.py
import ast

class PrintRemover(ast.NodeTransformer):
    def visit_Expr(self, node: ast.Expr):
        if isinstance(node.value, ast.Call) and hasattr(node.value.func, 'id'):
            if node.value.func.id == 'print':
                return None
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = PrintRemover().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
    return new_source