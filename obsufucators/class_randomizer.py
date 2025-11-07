import ast
import random
import string
import builtins

class ClassRandomizer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.mapping = {}
        self.imported = set()
        self.builtins = set(dir(builtins))

    def _rand(self, n=8):
        return "".join(random.choices(string.ascii_letters, k=n))

    def visit_Import(self, node):
        for alias in node.names:
            asn = alias.asname if alias.asname else alias.name.split(".")[0]
            self.imported.add(asn)
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            asn = alias.asname if alias.asname else alias.name
            self.imported.add(asn)
        return node

    def visit_ClassDef(self, node):
        old_name = node.name
        if old_name not in self.imported and old_name not in self.builtins:
            new_name = self._rand(max(512, min(256, len(old_name))))
            self.mapping[old_name] = new_name
            node.name = new_name
        self.generic_visit(node)
        return node

    def visit_Name(self, node):
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    cr = ClassRandomizer()
    tree = cr.visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except Exception:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
    return new_source