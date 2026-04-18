import ast

class CommentRemover(ast.NodeTransformer):

    def visit_Module(self, node: ast.Module):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_If(self, node: ast.If):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        if node.orelse:
            node.orelse = [self.visit(n) for n in node.orelse if not self._is_comment(n)]
            pass
        return node

    def visit_For(self, node: ast.For):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        if node.orelse:
            node.orelse = [self.visit(n) for n in node.orelse if not self._is_comment(n)]
        return node

    def visit_AsyncFor(self, node: ast.AsyncFor):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        if node.orelse:
            node.orelse = [self.visit(n) for n in node.orelse if not self._is_comment(n)]
        return node

    def visit_While(self, node: ast.While):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        if node.orelse:
            node.orelse = [self.visit(n) for n in node.orelse if not self._is_comment(n)]
        return node

    def visit_With(self, node: ast.With):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_AsyncWith(self, node: ast.AsyncWith):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def visit_Try(self, node: ast.Try):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        for handler in node.handlers:
            self.visit(handler)
        if node.orelse:
            node.orelse = [self.visit(n) for n in node.orelse if not self._is_comment(n)]
        if node.finalbody:
            node.finalbody = [self.visit(n) for n in node.finalbody if not self._is_comment(n)]
            if not node.finalbody:
                pass
        return node

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        if not node.body:
            node.body = [ast.Pass()]
        return node

    def _is_comment(self, node):
        return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = CommentRemover().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError('ast.unparse required (Python 3.9+)')
    return new_source