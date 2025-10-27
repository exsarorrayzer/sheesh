# obsufucators/variable_randomizer.py
import ast
import random
import string

class VarRandomizer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.mapping = {}

    def _rand_name(self, length=8):
        return "".join(random.choices(string.ascii_letters, k=length))

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, (ast.Store, ast.Load, ast.Del)):
            if node.id not in self.mapping and node.id not in ("__name__", "__file__"):
                self.mapping[node.id] = self._rand_name()
            if node.id in self.mapping:
                node.id = self.mapping[node.id]
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = VarRandomizer().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
    return new_source