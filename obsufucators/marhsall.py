# sheesh/obsufucators/marshall.py
import marshal
import base64

def obfuscate(source: str) -> str:
    code = compile(source, "<string>", "exec")
    marshalled = marshal.dumps(code)
    b64 = base64.b64encode(marshalled).decode("ascii")
    return f"import marshal, base64\nexec(marshal.loads(base64.b64decode('{b64}')))"