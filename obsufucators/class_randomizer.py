# obsufucators/class_randomizer.py
import ast
import random
import string

class ClassRandomizer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.mapping = {}

    def _rand_name(self, length=10):
        return ''.join(random.choices(string.ascii_letters, k=length))

    def visit_ClassDef(self, node: ast.ClassDef):
        if node.name not in self.mapping:
            self.mapping[node.name] = self._rand_name()
        node.name = self.mapping[node.name]
        self.generic_visit(node)
        return node

    def visit_Name(self, node: ast.Name):
        if node.id in self.mapping:
            node.id = self.mapping[node.id]
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = ClassRandomizer().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
    return new_source