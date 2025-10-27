# obsufucators/zlib_compressor.py
import zlib
import base64

def obfuscate(source: str) -> str:
    compressed = zlib.compress(source.encode("utf-8"))
    b64 = base64.b64encode(compressed).decode("utf-8")
    wrapper = f"import zlib, base64\nexec(zlib.decompress(base64.b64decode('{b64}')))"
    return wrapper