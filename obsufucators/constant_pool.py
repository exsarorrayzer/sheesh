import ast
import random
import string
import marshal
import zlib
import base64

class ConstantPoolTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.pool = []
        self.pool_name = "_P_" + "".join(random.choices(string.ascii_letters, k=8))
        self.in_joined = False

    def visit_JoinedStr(self, node):
        self.in_joined = True
        self.generic_visit(node)
        self.in_joined = False
        return node
        
    def visit_Module(self, node):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            doc = node.body[0]
            rest = [self.visit(n) for n in node.body[1:]]
            node.body = [doc] + rest
            return node
        self.generic_visit(node)
        return node

    def visit_FunctionDef(self, node):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            doc = node.body[0]
            rest = [self.visit(n) for n in node.body[1:]]
            node.body = [doc] + rest
            return node
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        if node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
            doc = node.body[0]
            rest = [self.visit(n) for n in node.body[1:]]
            node.body = [doc] + rest
            return node
        self.generic_visit(node)
        return node

    def visit_Constant(self, node):
        if self.in_joined:
            return node
            
        if isinstance(node.value, (str, int)) and not isinstance(node.value, bool):
            if isinstance(node.value, str) and len(node.value) == 0:
                return node
                
            val = node.value
            if val not in self.pool:
                self.pool.append(val)
            idx = self.pool.index(val)
            
            return ast.Subscript(
                value=ast.Name(id=self.pool_name, ctx=ast.Load()),
                slice=ast.Constant(value=idx),
                ctx=ast.Load()
            )
        return node

def obfuscate(source: str) -> str:
    try:
        tree = ast.parse(source)
    except Exception:
        return source
        
    pooler = ConstantPoolTransformer()
    tree = pooler.visit(tree)
    
    if not pooler.pool:
        return source
        
    marshalled = marshal.dumps(pooler.pool)
    compressed = zlib.compress(marshalled)
    b64 = base64.b64encode(compressed).decode('ascii')
    
    helper_code = f"import marshal as _m, zlib as _z, base64 as _b\n{pooler.pool_name} = _m.loads(_z.decompress(_b.b64decode('{b64}')))\n"
    
    try:
        helper_node = ast.parse(helper_code)
    except Exception:
        return source
        
    future_idx = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            future_idx = i + 1
        else:
            break
            
    tree.body = tree.body[:future_idx] + helper_node.body + tree.body[future_idx:]
    ast.fix_missing_locations(tree)
    
    try:
        return ast.unparse(tree)
    except Exception:
        return source
