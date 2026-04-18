import ast

class PrintRemover(ast.NodeTransformer):

    def visit_Expr(self, node: ast.Expr):
        if isinstance(node.value, ast.Call) and hasattr(node.value.func, 'id'):
            if node.value.func.id == 'print':
                return None
        return node

    def _ensure_pass(self, body_list):
        if not body_list:
            return [ast.Pass()]
        return body_list

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_AsyncFunctionDef(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_If(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        if node.orelse:
            pass
            if not node.orelse:
                pass
        return node

    def visit_For(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_AsyncFor(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_While(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_With(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_AsyncWith(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

    def visit_Try(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        if node.finalbody:
            node.finalbody = self._ensure_pass(node.finalbody)
        return node

    def visit_ExceptHandler(self, node):
        self.generic_visit(node)
        node.body = self._ensure_pass(node.body)
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = PrintRemover().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError('ast.unparse required (Python 3.9+)')
    return new_source