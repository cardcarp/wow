import json
import os
import sys
import re
from cerberus import Validator
from ruamel.yaml import YAML

# Extend Cerberus to understand YAML coercion in Python
COERCE_MAP = {
    'int': lambda v: None if v is None else int(v),
    'float': lambda v: None if v is None else float(v),
    'str': lambda v: None if v is None else str(v),
    'bool': lambda v: None if v is None else bool(v)
}

from part.util import to_kebab_case

def hydrate_schema(data):
    if isinstance(data, dict):
        for key, value in data.items():
            # If we find a 'coerce' key and its value is in our map, swap it
            if key == 'coerce' and value in COERCE_MAP:
                data[key] = COERCE_MAP[value]
            # Otherwise, keep digging down the tree
            else:
                hydrate_schema(value)
                
    elif isinstance(data, list):
        # This catches complex rules like 'anyof' or 'allof' which contain lists of dicts
        for item in data:
            hydrate_schema(item)
            
    return data

def load_yml(path):
    yaml = YAML()
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.load(f)

def get_validator(schema_name):
    schema_path = f'schema/{schema_name}.yml'
    if os.path.exists(schema_path):
        raw_schema = load_yml(schema_path)
        live_schema = hydrate_schema(raw_schema)
        return Validator(live_schema)
    return None


def validate_data(data, validator, context_name):
    is_valid = validator.validate(data)

    if not is_valid:
        print(f"Error in {context_name}:")
        for field, errors in validator.errors.items():
            print(f"  - {field}: {errors}")
        sys.exit(1)

    return validator.document

def compile_base_jsons():
    # 1. Convert modular YAML into base JSON files with validation
    print("Step 1: Validating and building base JSON files...")
    os.makedirs('dist', exist_ok=True)
    
    # Metadata maps
    mappings = [
        ('data/oracle', 'dist/oracle.json', 'oracle'),
        ('data/set', 'dist/set.json', 'set'),
        ('data/collection', 'dist/collection.json', 'collection'),
        ('data/format', 'dist/format.json', 'format')
    ]
    
    for yml_dir, json_out, schema_name in mappings:
        validator = get_validator(schema_name) if schema_name else None
        data_map = {}
        
        if not os.path.exists(yml_dir): continue
        
        for filename in sorted(os.listdir(yml_dir)):
            if filename.endswith('.yml'):
                key = filename.replace('.yml', '')
                item_data = load_yml(os.path.join(yml_dir, filename))
                clean_data = validate_data(item_data, validator, f"{yml_dir}/{filename}")
                data_map[key] = clean_data
                
        with open(json_out, 'w', encoding='utf-8') as f:
            json.dump(data_map, f, indent=2)
        print(f"  Built {json_out}")

    # Cards (nested)
    card_validator = get_validator('card')
    cards = {}
    for root, dirs, files in os.walk('data/card'):
        for file in files:
            if file.endswith('.yml'):
                card_raw = load_yml(os.path.join(root, file))
                card_clean = validate_data(card_raw, card_validator, f"{root}/{file}")

                card_data = {
                    **card_clean,
                    "oracle_id": card_raw["oracle"],
                    "card_lex": card_raw["lex"],
                    "set_id": card_raw["set"]
                }
                card_data.pop("oracle")
                card_data.pop("lex")
                card_data.pop("set")

                sid = card_data.get('set_id')
                lex = card_data.get('card_lex')
                card_id = f"{sid}-{lex}"
                
                cards[card_id] = card_data
    
    with open('dist/card.json', 'w', encoding='utf-8') as f:
        json.dump(cards, f, indent=2)
    print(f"  Built dist/card.json ({len(cards)} cards)")

    # Decks (nested)
    deck_validator = get_validator('deck')
    decks = {}
    for root, dirs, files in os.walk('data/deck'):
        for file in files:
            if file.endswith('.yml'):
                deck_data = load_yml(os.path.join(root, file))
                clean_data = validate_data(deck_data, deck_validator, f"{root}/{file}")
                
                dname = clean_data.get('name')
                dcol = clean_data.get('collection')
                deck_id = to_kebab_case(f"{dcol}-{dname}")
                
                decks[deck_id] = clean_data
    
    with open('dist/deck.json', 'w', encoding='utf-8') as f:
        json.dump(decks, f, indent=2)
    print(f"  Built dist/deck.json ({len(decks)} decks)")

def compile_joined_database():
    # 2. Join JSON files and output final artifacts
    print("Step 2: Joining data and outputing database...")
    
    with open('dist/card.json', 'r') as f: cards = json.load(f)
    with open('dist/oracle.json', 'r') as f: oracles = json.load(f)
    with open('dist/set.json', 'r') as f: sets = json.load(f)
    with open('dist/collection.json', 'r') as f: collections = json.load(f)
    with open('dist/format.json', 'r') as f: formats = json.load(f)
    with open('dist/deck.json', 'r') as f: decks = json.load(f)

    card_complete_dict = {}

    for card_id, record in cards.items():
        # Join Oracle
        oid = record.get("oracle_id")
        if oid in oracles:
            for k, v in oracles[oid].items():
                if k not in record: record[k] = v
        
        # Join Set
        sid = record.get("set_id")
        coll_id_from_set = None
        if sid in sets:
            set_info = sets[sid]
            coll_id_from_set = set_info.get("collection_id")
            for k, v in set_info.items():
                match k:
                    case 'name':
                        key = "set_name"
                    case 'type':
                        key = "set_type"
                    case 'lex':
                        key = "set_lex"
                    case 'collection':
                        key = "collection_id"
                    case _:
                        key = k
                if key not in record: record[key] = v

        # Join Collection
        cid = record.get("collection_id") or coll_id_from_set
        if cid in collections:
            for k, v in collections[cid].items():
                match k:
                    case 'name':
                        key = "collection_name"
                    case 'type':
                        key = "collection_type"
                    case 'lex':
                        key = "collection_lex"
                    case _:
                        key = k
                if key not in record: record[key] = v

        # Calculate Legality
        record["format"] = {}
        record["legal"] = []
        record["ban"] = []
        record["restrict"] = []
        c_set_id = record.get("set_id")
        c_reg = record.get("regulation")
        c_oid = record.get("oracle_id")
        c_cat = record.get("category")

        for f_name, f_rules in formats.items():
            legal, limit = False, 0
            s_allow = f_rules.get("set_allow", [])
            bans = f_rules.get("oracle_ban") or []

            if c_oid in bans:
                record["ban"].append(f_name)

            if "*" in s_allow or c_set_id in s_allow:
                r_allow = f_rules.get("regulation_allow", [])
                if "*" in r_allow or str(c_reg) in r_allow:
                    bans = f_rules.get("oracle_ban") or []
                    if not bans or c_oid not in bans:
                        restricts = f_rules.get("oracle_restrict")
                        cat_limits = f_rules.get("category_limit")
                        if restricts and c_oid in restricts:
                            legal, limit = True, restricts[c_oid]
                            record["restrict"].append(f_name)
                        elif cat_limits and c_cat in cat_limits:
                            legal, limit = True, cat_limits[c_cat]
                        else:
                            legal, limit = True, f_rules.get("oracle_limit", 4)
                        if legal:
                            record["legal"].append(f_name)
            record["format"][f_name] = {"legal": legal, "limit": limit}

        # Add it al together
        card_complete_dict[card_id] = record

    # Output complete card database
    with open('dist/database.json', 'w', encoding='utf-8') as f:
        json.dump(card_complete_dict, f, indent=2)
    print(f"  Built dist/database.json")

if __name__ == "__main__":
    compile_base_jsons()
    print("-" * 30)
    compile_joined_database()