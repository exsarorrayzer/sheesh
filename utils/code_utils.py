import ast

def prepend_code(source: str, code_to_prepend: str) -> str:
    """
    Prepends code to source while preserving __future__ imports at the top.
    """
    try:
        tree = ast.parse(source)
    except Exception:
        # If it cannot be parsed, just prepend it and hope for the best
        return code_to_prepend + "\n" + source

    future_imports = []
    other_body = []
    
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            future_imports.append(node)
        else:
            other_body.append(node)
            
    if not future_imports:
        return code_to_prepend + "\n" + source
        
    # Reconstruct the source with future imports at the top
    try:
        future_code = "\n".join(ast.unparse(n) for n in future_imports)
        # Note: we don't use other_body here because unparsing the whole tree might change formatting.
        # Instead, we find where the last future import ends in the original source.
        
        # A simpler way:
        new_source = future_code + "\n" + code_to_prepend + "\n"
        
        # Find the end of the last future import line in original source
        lines = source.splitlines()
        last_future_idx = 0
        for i, line in enumerate(lines):
            if "__future__" in line and "import" in line:
                last_future_idx = i + 1
        
        new_source += "\n".join(lines[last_future_idx:])
        return new_source
    except Exception:
        return code_to_prepend + "\n" + source
