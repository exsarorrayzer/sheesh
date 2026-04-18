import ast
import random
import string

STDLIB_SAFE = {
    'os', 'sys', 'json', 'time', 'math', 'random', 'string', 'hashlib',
    'base64', 'struct', 'io', 'collections', 'itertools', 'functools',
    'pathlib', 'subprocess', 'threading', 'socket', 'http', 'urllib',
    're', 'datetime', 'shutil', 'tempfile', 'glob', 'csv', 'logging',
    'platform', 'ctypes', 'zlib', 'gzip', 'bz2', 'lzma', 'zipfile',
    'tarfile', 'configparser', 'argparse', 'textwrap', 'copy',
    'pickle', 'shelve', 'sqlite3', 'hmac', 'secrets', 'uuid',
    'typing', 'enum', 'dataclasses', 'abc', 'contextlib',
    'signal', 'multiprocessing', 'concurrent', 'asyncio',
    'ssl', 'email', 'smtplib', 'ftplib', 'xmlrpc',
    'tkinter', 'turtle', 'webbrowser',
}

def _rand(k=15):
    return ''.join(random.choices(string.ascii_letters, k=k))

class DynamicImportTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.aliases = {}

    def visit_Import(self, node):
        new_stmts = []
        for alias in node.names:
            mod_name = alias.name
            local_name = alias.asname if alias.asname else mod_name.split('.')[0]

            if mod_name.split('.')[0] in STDLIB_SAFE:
                rand_alias = _rand(18)
                self.aliases[local_name] = rand_alias

                assign = ast.Assign(
                    targets=[ast.Name(id=rand_alias, ctx=ast.Store())],
                    value=ast.Call(
                        func=ast.Name(id='__import__', ctx=ast.Load()),
                        args=[ast.Constant(value=mod_name)],
                        keywords=[]
                    ),
                    lineno=0
                )
                new_stmts.append(assign)
            else:
                new_stmts.append(node)

        return new_stmts if new_stmts else node

    def visit_Name(self, node):
        if node.id in self.aliases:
            node.id = self.aliases[node.id]
        return node

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    transformer = DynamicImportTransformer()
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    try:
        return ast.unparse(tree)
    except AttributeError:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
