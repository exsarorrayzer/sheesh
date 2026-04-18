import ast
import random

class OpaquePredicateInjector(ast.NodeTransformer):
    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        
        # We only inject into functions with a real body
        if not node.body:
            return node
            
        body_start = 0
        if isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
            body_start = 1
            
        real_body = node.body[body_start:]
        if not real_body:
            return node
            
        # Opaque predicate: if (v * v + v) % 2 == 0:
        var = random.randint(10, 100)
        test = ast.Compare(
            left=ast.BinOp(
                left=ast.BinOp(
                    left=ast.BinOp(left=ast.Constant(value=var), op=ast.Mult(), right=ast.Constant(value=var)),
                    op=ast.Add(),
                    right=ast.Constant(value=var)
                ),
                op=ast.Mod(),
                right=ast.Constant(value=2)
            ),
            ops=[ast.Eq()],
            comparators=[ast.Constant(value=0)]
        )
        
        if_node = ast.If(test=test, body=real_body, orelse=[ast.Pass()])
        node.body = node.body[:body_start] + [if_node]
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = OpaquePredicateInjector().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except Exception:
        return source
