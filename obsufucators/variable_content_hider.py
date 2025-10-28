import ast
import base64

class ContentHider(ast.NodeTransformer):
    def visit_Assign(self, node):
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                if isinstance(node.value, ast.Constant):
                    val = node.value.value
                    if isinstance(val, str):
                        b = val.encode("utf-8")
                        b64 = base64.b64encode(b).decode("ascii")
                        new_node = ast.Call(
                            func=ast.Attribute(
                                value=ast.Call(func=ast.Name(id="__import__", ctx=ast.Load()),
                                               args=[ast.Constant(value="base64")],
                                               keywords=[]),
                                attr="b64decode",
                                ctx=ast.Load()
                            ),
                            args=[ast.Constant(value=b64)],
                            keywords=[]
                        )
                        new_node = ast.Call(func=ast.Attribute(value=new_node, attr="decode", ctx=ast.Load()),
                                            args=[ast.Constant(value="utf-8")],
                                            keywords=[])
                        node.value = new_node
                    elif isinstance(val, (bytes, bytearray)):
                        b = bytes(val)
                        b64 = base64.b64encode(b).decode("ascii")
                        new_node = ast.Call(
                            func=ast.Attribute(
                                value=ast.Call(func=ast.Name(id="__import__", ctx=ast.Load()),
                                               args=[ast.Constant(value="base64")],
                                               keywords=[]),
                                attr="b64decode",
                                ctx=ast.Load()
                            ),
                            args=[ast.Constant(value=b64)],
                            keywords=[]
                        )
                        node.value = new_node
        return self.generic_visit(node)

def obfuscate(source: str) -> str:
    tree = ast.parse(source)
    ch = ContentHider()
    tree = ch.visit(tree)
    ast.fix_missing_locations(tree)
    try:
        new_source = ast.unparse(tree)
    except Exception:
        raise RuntimeError("ast.unparse required (Python 3.9+)")
    return new_source 