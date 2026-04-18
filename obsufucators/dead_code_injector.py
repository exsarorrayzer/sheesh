import ast
import random
import string

def _rand_name(k=12):
    return ''.join(random.choices(string.ascii_lowercase, k=k))

def _make_dead_func():
    fname = _rand_name(15)
    args_count = random.randint(0, 4)
    arg_names = [_rand_name(8) for _ in range(args_count)]
    body_stmts = []

    for _ in range(random.randint(2, 6)):
        vname = _rand_name(10)
        val = random.choice([
            ast.Constant(value=random.randint(-999, 999)),
            ast.Constant(value=_rand_name(20)),
            ast.Constant(value=random.random()),
            ast.List(elts=[ast.Constant(value=random.randint(0, 100)) for _ in range(random.randint(1, 5))], ctx=ast.Load()),
        ])
        body_stmts.append(ast.Assign(
            targets=[ast.Name(id=vname, ctx=ast.Store())],
            value=val, lineno=0
        ))

    cond_var = _rand_name(8)
    body_stmts.append(ast.Assign(
        targets=[ast.Name(id=cond_var, ctx=ast.Store())],
        value=ast.Constant(value=False), lineno=0
    ))
    body_stmts.append(ast.If(
        test=ast.Name(id=cond_var, ctx=ast.Load()),
        body=[ast.Pass()],
        orelse=[ast.Pass()]
    ))
    body_stmts.append(ast.Return(value=ast.Constant(value=None)))

    func = ast.FunctionDef(
        name=fname,
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=a) for a in arg_names],
            vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]
        ),
        body=body_stmts,
        decorator_list=[],
        returns=None, lineno=0
    )
    return func

def _make_dead_class():
    cname = _rand_name(15)
    methods = []
    for _ in range(random.randint(1, 3)):
        methods.append(_make_dead_func())
    cls = ast.ClassDef(
        name=cname,
        bases=[],
        keywords=[],
        body=methods if methods else [ast.Pass()],
        decorator_list=[], lineno=0
    )
    return cls

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    inject_count = random.randint(5, 15)
    new_stmts = []
    for _ in range(inject_count):
        if random.random() < 0.6:
            new_stmts.append(_make_dead_func())
        else:
            new_stmts.append(_make_dead_class())

    insertion_points = sorted(random.sample(
        range(len(tree.body) + 1),
        min(len(new_stmts), len(tree.body) + 1)
    ), reverse=True)

    remaining = list(new_stmts)
    for idx in insertion_points:
        if remaining:
            tree.body.insert(idx, remaining.pop())

    for leftover in remaining:
        tree.body.append(leftover)

    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except AttributeError:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
