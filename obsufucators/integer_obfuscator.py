import ast
import random

class IntegerObfuscator(ast.NodeTransformer):

    def _make_expression(self, value):
        if value == 0:
            a = random.randint(1, 1000)
            return ast.BinOp(left=ast.Constant(value=a), op=ast.Sub(), right=ast.Constant(value=a))
        if abs(value) < 2:
            return None
        method = random.randint(0, 3)
        if method == 0:
            a = random.randint(1, 10000)
            b = value + a
            return ast.BinOp(left=ast.Constant(value=b), op=ast.Sub(), right=ast.Constant(value=a))
        elif method == 1:
            a = random.randint(1, 10000)
            b = value - a
            return ast.BinOp(left=ast.Constant(value=a), op=ast.Add(), right=ast.Constant(value=b))
        elif method == 2:
            shift = random.randint(1, 4)
            if value >= 0 and value % (1 << shift) == 0:
                base = value >> shift
                return ast.BinOp(left=ast.Constant(value=base), op=ast.LShift(), right=ast.Constant(value=shift))
            a = random.randint(1, 5000)
            b = value ^ a
            return ast.BinOp(left=ast.Constant(value=b), op=ast.BitXor(), right=ast.Constant(value=a))
        else:
            a = random.randint(1, 5000)
            b = value ^ a
            return ast.BinOp(left=ast.Constant(value=b), op=ast.BitXor(), right=ast.Constant(value=a))

    def visit_Constant(self, node):
        if isinstance(node.value, int) and (not isinstance(node.value, bool)):
            expr = self._make_expression(node.value)
            if expr is not None:
                return expr
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = IntegerObfuscator().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except AttributeError:
        raise RuntimeError('ast.unparse required (Python 3.9+)')