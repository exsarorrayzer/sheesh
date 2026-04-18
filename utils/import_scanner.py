import ast

def scan_imports(source_code):
    """
    Scans Python source code for imported modules.
    Returns a list of module names that might need to be hidden-imported.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return []
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_level = alias.name.split('.')[0]
                imports.add(top_level)
                if top_level != alias.name:
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top_level = node.module.split('.')[0]
                imports.add(top_level)
                if top_level != node.module:
                    imports.add(node.module)
    return sorted([i for i in imports if i])