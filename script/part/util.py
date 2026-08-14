import re
import os
import sys
import unicodedata

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

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

    # Remove apostrophes entirely (Lodash behavior), curly included so that
    # "Kur'talos" and "Kur’talos" cannot kebab to different ids
    text = re.sub(r"['‘’]", "", text)

    # Transliterate accents to their base letter, so an accented character is
    # folded rather than treated as a separator
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))

    # No camelCase splitting: these are proper names, not code identifiers.
    # "BlizzCon" is one word.

    # Replace non-alphanumeric with hyphens
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text)

    # Normalize case and trim
    return text.lower().strip("-")

def load_schema_order(schema_name):
    # Field order is taken from the schema file so the two never drift apart
    schema_path = f'schema/{schema_name}.yml'
    if not os.path.exists(schema_path):
        print(f"Warning: schema/{schema_name}.yml not found, leaving field order as-is.")
        return None

    yaml = YAML()
    with open(schema_path, 'r', encoding='utf-8') as f:
        return list(yaml.load(f).keys())

def order_by_schema(entry, order):
    # Keys the schema knows about come first, in schema order.
    # Anything unrecognized is kept at the end rather than dropped.
    if not order:
        return entry

    ordered = {key: entry[key] for key in order if key in entry}
    ordered.update({k: v for k, v in entry.items() if k not in order})
    return ordered

def save_yml(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    # 1. Initialize and configure ruamel
    yaml = YAML()
    yaml.width = sys.maxsize
    yaml.explicit_start = False # Prevents the "---" document start marker
    
    # mapping (spaces for dicts), sequence (spaces for list items), offset (spaces before the dash)
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    # 2. Check if data is already a CommentedMap to preserve comments
    if isinstance(data, CommentedMap):
        cmap = data
    else:
        cmap = CommentedMap(data)
    
    # 3. Natively inject a blank line before every top-level key (except the very first one)
    for i, key in enumerate(cmap.keys()):
        if i > 0:
            cmap.yaml_set_comment_before_after_key(key, before='\n')
            
    # 4. Write directly to the file
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(cmap, f)
