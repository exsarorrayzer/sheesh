# obsufucators/base64.py
import base64

def obfuscate(source: str) -> str:
    encoded = base64.b64encode(source.encode("utf-8")).decode("utf-8")
    wrapper = f"import base64\nexec(base64.b64decode('{encoded}'))"
    return wrapper