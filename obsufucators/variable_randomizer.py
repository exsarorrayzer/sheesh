import ast
import random
import string
import builtins

class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.mapping = {}
        self.declared = set()
    def find(self, name):
        s = self
        while s:
            if name in s.mapping:
                return s.mapping[name]
            s = s.parent
        return None
    def set_mapping(self, name, new):
        self.mapping[name] = new
        self.declared.add(name)

class VarRandomizer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.imported = set()
        self.builtins = set(dir(builtins))
        self.module_scope = Scope(parent=None)
        self.scope = self.module_scope
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
    def visit_Module(self, node):
        self.scope = self.module_scope
        self.generic_visit(node)
        return node
    def visit_FunctionDef(self, node):
        old_scope = self.scope
        new_scope = Scope(parent=old_scope)
        self.scope = new_scope
        for arg in node.args.args:
            if arg.arg and arg.arg not in self.imported and arg.arg not in self.builtins and arg.arg not in ("__name__", "__file__"):
                new_name = self._rand(max(4, min(12, len(arg.arg))))
                new_scope.set_mapping(arg.arg, new_name)
                arg.arg = new_name
        if node.args.kwonlyargs:
            for arg in node.args.kwonlyargs:
                if arg.arg and arg.arg not in self.imported and arg.arg not in self.builtins:
                    new_name = self._rand(max(4, min(12, len(arg.arg))))
                    new_scope.set_mapping(arg.arg, new_name)
                    arg.arg = new_name
        if node.args.vararg and node.args.vararg.arg:
            a = node.args.vararg
            if a.arg not in self.imported and a.arg not in self.builtins:
                new_name = self._rand()
                new_scope.set_mapping(a.arg, new_name)
                a.arg = new_name
        if node.args.kwarg and node.args.kwarg.arg:
            a = node.args.kwarg
            if a.arg not in self.imported and a.arg not in self.builtins:
                new_name = self._rand()
                new_scope.set_mapping(a.arg, new_name)
                a.arg = new_name
        self.generic_visit(node)
        self.scope = old_scope
        return node
    def visit_ClassDef(self, node):
        old_scope = self.scope
        new_scope = Scope(parent=old_scope)
        self.scope = new_scope
        self.generic_visit(node)
        self.scope = old_scope
        return node
    def visit_Global(self, node):
        for name in node.names:
            if name not in self.module_scope.mapping and name not in self.imported and name not in self.builtins:
                new_name = self._rand(max(4, min(12, len(name))))
                self.module_scope.set_mapping(name, new_name)
        return node
    def visit_Nonlocal(self, node):
        for name in node.names:
            s = self.scope.parent
            found = False
            while s and s is not None:
                if name in s.mapping or name in s.declared:
                    found = True
                    break
                s = s.parent
            if not found and self.module_scope is not None:
                if name not in self.module_scope.mapping and name not in self.imported and name not in self.builtins:
                    new_name = self._rand(max(4, min(12, len(name))))
                    self.scope.parent.set_mapping(name, new_name)
        return node
    def _should_rename(self, name):
        if not name:
            return False
        if name in self.imported:
            return False
        if name in ("__name__", "__file__"):
            return False
        if name in self.builtins:
            return False
        return True
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            if self._should_rename(node.id):
                if self.scope.find(node.id) is None:
                    new_name = self._rand(max(4, min(12, len(node.id))))
                    self.scope.set_mapping(node.id, new_name)
                    node.id = new_name
                else:
                    mapped = self.scope.find(node.id)
                    if mapped:
                        node.id = mapped
        elif isinstance(node.ctx, ast.Load) or isinstance(node.ctx, ast.Del):
            mapped = self.scope.find(node.id)
            if mapped:
                node.id = mapped
        return node
    def visit_arg(self, node):
        return node
    def visit_Assign(self, node):
        self.generic_visit(node.value)
        for t in node.targets:
            self._visit_target(t)
        return node
    def _visit_target(self, node):
        if isinstance(node, ast.Name):
            if self._should_rename(node.id):
                if self.scope.find(node.id) is None:
                    new_name = self._rand(max(4, min(12, len(node.id))))
                    self.scope.set_mapping(node.id, new_name)
                    node.id = new_name
                else:
                    node.id = self.scope.find(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for el in node.elts:
                self._visit_target(el)
        else:
            self.visit(node)
    def visit_AugAssign(self, node):
        self._visit_target(node.target)
        self.generic_visit(node.value)
        return node
    def visit_For(self, node):
        self._visit_target(node.target)
        self.generic_visit(node.iter)
        for n in node.body:
            self.visit(n)
        for n in node.orelse:
            self.visit(n)
        return node
    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars:
                self._visit_target(item.optional_vars)
            self.visit(item.context_expr)
        for n in node.body:
            self.visit(n)
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    vr = VarRandomizer()
    tree = vr.visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except Exception:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
    return new_source