import ast
import random
import string

class Outliner(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.funcs = []

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if random.random() > 0.4:  # Outline ~60% of binops
            return node
            
        fname = "_outl_" + "".join(random.choices(string.ascii_letters, k=8))
        op_map = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/', ast.FloorDiv: '//', ast.Mod: '%', ast.Pow: '**', ast.BitAnd: '&', ast.BitOr: '|', ast.BitXor: '^', ast.LShift: '<<', ast.RShift: '>>'}
        op_type = type(node.op)
        if op_type not in op_map:
            return node
            
        func_code = f"def {fname}(a, b): return a {op_map[op_type]} b"
        try:
            func_node = ast.parse(func_code).body[0]
            self.funcs.append(func_node)
            return ast.Call(func=ast.Name(id=fname, ctx=ast.Load()), args=[node.left, node.right], keywords=[])
        except Exception:
            return node

def obfuscate(source: str) -> str:
    try:
        tree = ast.parse(source)
    except Exception:
        return source
        
    outliner = Outliner()
    tree = outliner.visit(tree)
    
    if not outliner.funcs:
        return source
        
    future_idx = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            future_idx = i + 1
        else:
            break
            
    tree.body = tree.body[:future_idx] + outliner.funcs + tree.body[future_idx:]
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return source
