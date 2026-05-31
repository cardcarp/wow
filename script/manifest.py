import json
import os
import re

from part.util import to_kebab_case, get_env

cdn = get_env("CDN_URL", "")

# Whitelist properties to keep lists lightweight and queryable-friendly
CARD_LIST_PROPERTIES = [
    "id",
    "card_name",
    "card_lex",
    "set_id",
    "oracle_id",
    "suit",
    "value",
    "legal",
    "rarity",
    "artist",
    "img"
]

DECK_LIST_PROPERTIES = [
    "id",
    "name",
    "category",
    "facet",
    "collection",
    "highlight",
    "total",
    "list"
]



def combine_data():
    
    mappings = {
        'card_dict': 'dist/database.json',
        'deck_dict': 'dist/deck.json',
        'data': 'dist/data.json',
    }
    
    combined = {}
    
    for key, path in mappings.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # If processing cards, add web/print image paths to each record
            if key == 'card_dict':
                print(f"Processing image paths for {len(data)} cards...")
                for record_id, record in data.items():

                    collection_type = record.get('collection_type')
                    collection_lex = record.get('collection_lex')
                    collection_id = record.get('collection_id')

                    set_lex = record.get('set_lex')
                    set_id = record.get('set_id')

                    oracle_id = record.get('oracle_id')
                    
                    card_lex = record.get('card_lex')
                    card_name = record.get('card_name')
                    card_layout = record.get('layout')

                    collection_folder = f"{collection_lex}-{collection_id}" if collection_lex else collection_id
                    set_folder = f"{set_lex}-{set_id}" if set_lex else set_id
                    filename = f"{card_lex}-{card_name}" if card_lex else card_name

                    segments = [
                        "card",
                        to_kebab_case(collection_type),
                        to_kebab_case(collection_folder),
                        to_kebab_case(set_folder),
                        to_kebab_case(filename)
                    ]

                    img_path = f"{cdn}/" + "/".join(filter(None, segments))
                    
                    record['img'] = img_path

            combined[key] = data
            print(f"Loaded {path} into key '{key}'")

        else:
            if key != 'data':
                print(f"Warning: {path} not found, skipping key '{key}'")
                combined[key] = {}

    # Map card_list and deck_list as flat arrays of the card_dict and deck_dict dictionaries.
    # Move their key into each item as a property "id".
    card_dict = combined.get('card_dict', {})
    card_list = []
    for record_id, record in card_dict.items():
        # Keep only whitelisted properties
        new_record = {"id": record_id}
        for prop in CARD_LIST_PROPERTIES:
            if prop == "id":
                continue
            if prop in record:
                new_record[prop] = record[prop]
        card_list.append(new_record)
    combined['card_list'] = card_list

    deck_dict = combined.get('deck_dict', {})
    deck_list = []
    for record_id, record in deck_dict.items():
        new_record = {"id": record_id}
        for prop in DECK_LIST_PROPERTIES:
            if prop == "id":
                continue
            if prop == "list":
                # Convert the deck list structure into a flat list of just card keys
                card_keys = []
                original_list = record.get("list", {})
                if isinstance(original_list, dict):
                    for group_cards in original_list.values():
                        if isinstance(group_cards, dict):
                            for card_key in group_cards.keys():
                                if card_key not in card_keys:
                                    card_keys.append(card_key)
                new_record["list"] = card_keys
            elif prop in record:
                new_record[prop] = record[prop]
        deck_list.append(new_record)
    combined['deck_list'] = deck_list

    output_path = 'dist/manifest.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(combined, f, indent=2)
    
    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    combine_data()
