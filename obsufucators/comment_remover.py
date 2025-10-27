# obsufucators/comment_remover.py
import ast

class CommentRemover(ast.NodeTransformer):
    def visit_Module(self, node: ast.Module):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        return node

    def visit_ClassDef(self, node: ast.ClassDef):
        node.body = [self.visit(n) for n in node.body if not self._is_comment(n)]
        return node

    def _is_comment(self, node):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            v = node.value.value
            if isinstance(v, str) and v.strip().startswith(('"', "'")):
                return True
        return False

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = CommentRemover().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
    return new_source