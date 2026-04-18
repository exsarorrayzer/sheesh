import ast
import random
import string

class ControlFlowFlattener(ast.NodeTransformer):

    def __init__(self):
        super().__init__()
        self.counter = 0

    def _rand_name(self, prefix='_cf'):
        self.counter += 1
        suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
        return f'{prefix}{self.counter}_{suffix}'

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        if len(node.body) < 3:
            return node
        has_return = False
        for stmt in ast.walk(node):
            if isinstance(stmt, (ast.Return, ast.Yield, ast.YieldFrom)):
                has_return = True
                break
        if has_return:
            return node
        state_var = self._rand_name('_st')
        loop_var = self._rand_name('_run')
        cases = []
        for i, stmt in enumerate(node.body):
            cases.append((i, stmt))
        order = list(range(len(cases)))
        new_body = []
        init_state = ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=order[0]), lineno=0)
        init_loop = ast.Assign(targets=[ast.Name(id=loop_var, ctx=ast.Store())], value=ast.Constant(value=True), lineno=0)
        new_body.append(init_state)
        new_body.append(init_loop)
        if_chain = None
        for idx in reversed(order):
            real_stmt = cases[idx][1]
            next_val = idx + 1 if idx + 1 < len(order) else -1
            block = [real_stmt]
            if next_val == -1:
                block.append(ast.Assign(targets=[ast.Name(id=loop_var, ctx=ast.Store())], value=ast.Constant(value=False), lineno=0))
            else:
                block.append(ast.Assign(targets=[ast.Name(id=state_var, ctx=ast.Store())], value=ast.Constant(value=next_val), lineno=0))
            test = ast.Compare(left=ast.Name(id=state_var, ctx=ast.Load()), ops=[ast.Eq()], comparators=[ast.Constant(value=idx)])
            if if_chain is None:
                if_chain = ast.If(test=test, body=block, orelse=[])
            else:
                if_chain = ast.If(test=test, body=block, orelse=[if_chain])
        while_loop = ast.While(test=ast.Name(id=loop_var, ctx=ast.Load()), body=[if_chain], orelse=[])
        new_body.append(while_loop)
        node.body = new_body
        return node

    def visit_AsyncFunctionDef(self, node):
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    tree = ControlFlowFlattener().visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except AttributeError:
        raise RuntimeError('ast.unparse required (Python 3.9+)')