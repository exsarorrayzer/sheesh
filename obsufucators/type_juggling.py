import ast
import random

class TypeJuggler(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, int) and not isinstance(node.value, bool):
            val = node.value
            if 0 < val < 100000:
                mask = random.randint(10000, 90000)
                obf_val = val ^ mask
                return ast.BinOp(left=ast.Constant(value=obf_val), op=ast.BitXor(), right=ast.Constant(value=mask))
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = TypeJuggler().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return source
