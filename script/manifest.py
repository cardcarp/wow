import json
import os

from part.util import to_kebab_case


def with_id(data):
    # The dict key becomes a property on the record too, so a record still
    # identifies itself once it is flattened out of the dict downstream.
    return {record_id: {"id": record_id, **record}
            for record_id, record in data.items()}


def combine_data():
    
    mappings = {
        'card_dict': 'dist/database.json',
        'deck_dict': 'dist/deck.json',
    }
    
    combined = {}
    
    for key, path in mappings.items():
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if key == 'card_dict':
                print(f"Processing image paths for {len(data)} cards...")
                for record_id, record in data.items():

                    collection_type = record.get('collection_type')
                    collection_index = record.get('collection_index')
                    collection_id = record.get('collection_id')

                    set_index = record.get('set_index')
                    set_id = record.get('set_id')

                    oracle_id = record.get('oracle_id')
                    
                    card_index = record.get('card_index')
                    card_name = record.get('name')
                    card_layout = record.get('layout')

                    collection_folder = f"{collection_index}-{collection_id}" if collection_index else collection_id
                    set_folder = f"{set_index}-{set_id}" if set_index else set_id
                    filename = f"{card_index}-{card_name}" if card_index else card_name

                    segments = [
                        to_kebab_case(collection_type),
                        to_kebab_case(collection_folder),
                        to_kebab_case(set_folder),
                        to_kebab_case(filename)
                    ]

                    dir_path = f"/".join(filter(None, segments))
                    
                    record['dir'] = dir_path

            data = with_id(data)

            combined[key] = data
            print(f"Loaded {path} into key '{key}'")

        else:
            print(f"Warning: {path} not found, skipping key '{key}'")
            combined[key] = {}

    output_path = 'dist/manifest.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        # Written compact rather than pretty-printed.
        json.dump(combined, f, separators=(',', ':'))
    
    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    combine_data()
