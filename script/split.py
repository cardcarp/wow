import json
import os
import re
import sys
import shutil
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from part.util import to_kebab_case

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

def split_json_to_yml():
    # Split /dist JSONs into individual YAMLs
    # Review wiki for how data and folder structure cascade
    
    print("Cleaning up old data...")
    if os.path.exists('data'):
        # Clear all previous YAMLs and folders to avoid orphaned content
        shutil.rmtree('data')
    os.makedirs('data', exist_ok=True)

    print("Starting decomposition...")

    # Load database once for card name lookups
    cards_map = {}
    joined_file = 'dist/database.json'
    if os.path.exists(joined_file):
        with open(joined_file, 'r') as f:
            cards_map = json.load(f)
    else:
        print(f"Warning: {joined_file} not found.")

    # --- 1. Split metadata maps
    # Target folder, plus the schema whose field order the output should follow
    # (None leaves the JSON's own key order untouched)
    simple_maps = {
        'dist/oracle.json': ('data/oracle', 'oracle'),
        'dist/collection.json': ('data/collection', None),
        'dist/set.json': ('data/set', None),
        'dist/format.json': ('data/format', None)
    }

    for json_file, (target_dir, schema_name) in simple_maps.items():
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data_map = json.load(f)

            field_order = load_schema_order(schema_name) if schema_name else None

            print(f"Splitting {json_file} into {target_dir}...")
            for key, entry in data_map.items():
                yml_path = os.path.join(target_dir, f"{key}.yml")
                save_yml(yml_path, order_by_schema(entry, field_order))
        else:
            print(f"Warning: {json_file} not found, skipping.")

    # --- 2. Split deck
    deck_file = 'dist/deck.json'
    if os.path.exists(deck_file):
        with open(deck_file, 'r') as f:
            deck_map = json.load(f)
        print(f"Splitting {deck_file} into nested deck folders...")
        count = 0
        for deck_id, deck_data in deck_map.items():
            collection = to_kebab_case(deck_data.get('collection', 'error'))
            deck_name = to_kebab_case(deck_data.get('name'))

            path = os.path.join('data', 'deck', collection, f"{deck_name}.yml")

            # Convert deck_data to CommentedMap to support comments
            deck_cmap = CommentedMap(deck_data)
            deck_list = deck_cmap.get('list')
            if isinstance(deck_list, dict):
                deck_list_cmap = CommentedMap(deck_list)
                for section in ['hero', 'main', 'reserve', 'token']:
                    if section in deck_list_cmap:
                        section_data = deck_list_cmap[section]
                        if isinstance(section_data, dict):
                            section_cmap = CommentedMap(section_data)
                            for card_id in section_cmap:
                                card_info = cards_map.get(card_id)
                                if card_info:
                                    card_name = card_info.get('card_name')
                                    if card_name:
                                        section_cmap.yaml_add_eol_comment(card_name, card_id)
                            deck_list_cmap[section] = section_cmap
                deck_cmap['list'] = deck_list_cmap

            save_yml(path, deck_cmap)
            count += 1
        
        print(f"Finished decks. Total: {count}")


    # --- 3. Split cards
    if cards_map:
        print(f"Splitting cards from database into nested card folders...")
        count = 0
        for card_id, card_data in cards_map.items():

            collection_type = card_data.get('collection_type')
            collection_lex = card_data.get('collection_lex')
            collection_id = card_data.get('collection_id')
            set_lex = card_data.get('set_lex')
            set_id = card_data.get('set_id')
            oracle_id = card_data.get('oracle_id')
            card_lex = card_data.get('card_lex')
            card_name = card_data.get('card_name')

            collection_folder = f"{collection_lex}-{collection_id}" if collection_lex else collection_id
            set_folder = f"{set_lex}-{set_id}" if set_lex else set_id
            filename = f"{card_lex}-{card_name}" if card_lex else card_name

            segments = [
                "data",
                "card",
                to_kebab_case(collection_type),
                to_kebab_case(collection_folder),
                to_kebab_case(set_folder),
                to_kebab_case(filename),
            ]

            path = "/".join(filter(None, segments)) + ".yml"

            ordered_card_data = {
                "oracle": oracle_id,
                "lex": card_lex,
                "set": set_id,
                "rarity": card_data.get('rarity', ''),
                "artist": card_data.get('artist', ''),
                "flavor": card_data.get('flavor', ''),
                "variation": card_data.get('variation', [])
            }

            save_yml(path, ordered_card_data)
            count += 1
        
        print(f"Finished cards. Total: {count}")
    else:
        print(f"Error: Database map is empty or not found.")

if __name__ == "__main__":
    split_json_to_yml()
