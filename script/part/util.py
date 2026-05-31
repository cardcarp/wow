import re
import os

_dotenv_loaded = False

def load_dotenv():
    global _dotenv_loaded
    if _dotenv_loaded:
        return
    possible_paths = [
        '.env',
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        os.environ[k.strip()] = v.strip().strip('"').strip("'")
            break
    _dotenv_loaded = True

def get_env(key, default=""):
    load_dotenv()
    return os.environ.get(key, default)

def to_kebab_case(text):
    if text is None:
        return ""

    text = str(text)

    # Remove apostrophes entirely (Lodash behavior)
    text = re.sub(r"[']", "", text)

    # Handle camelCase / PascalCase boundaries
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", text)
    text = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", text)

    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)

    # Normalize case and trim
    return text.lower().strip("-")
