import json
import os
import shutil

from ruamel.yaml.comments import CommentedMap

from part.util import to_kebab_case, save_yml, load_schema_order, order_by_schema

# The only trees this script owns. data/format is deliberately excluded: it is
# hand-authored and carries comments that a JSON round-trip would flatten.
OWNED_DIRS = ('data/oracle', 'data/collection', 'data/set', 'data/card', 'data/deck')

REQUIRED_INPUTS = ('dist/collection.json', 'dist/set.json', 'dist/oracle.json',
                   'dist/card.json', 'dist/deck.json')

DECK_SECTIONS = ('hero', 'main', 'reserve', 'token')


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def split_json_to_yml():
    # Split /dist JSONs back into individual YAMLs. This is the inverse of
    # compile.py: ids are dropped and every cross-reference is written back as
    # the human-readable name it was derived from.

    missing = [path for path in REQUIRED_INPUTS if not os.path.exists(path)]
    if missing:
        print("Error: cannot split without a complete build. Missing:")
        for path in missing:
            print(f"  - {path}")
        return

    collections = load_json('dist/collection.json')
    sets = load_json('dist/set.json')
    oracles = load_json('dist/oracle.json')
    cards = load_json('dist/card.json')
    decks = load_json('dist/deck.json')

    print("Cleaning up old data...")
    for folder in OWNED_DIRS:
        # Clear previous YAMLs and folders to avoid orphaned content
        shutil.rmtree(folder, ignore_errors=True)
    os.makedirs('data', exist_ok=True)

    print("Starting decomposition...")

    collection_order = load_schema_order('collection')
    set_order = load_schema_order('set')
    oracle_order = load_schema_order('oracle')
    card_order = load_schema_order('card')

    # --- 1. Collections and oracles carry no references -----------------------
    for collection_id, record in collections.items():
        save_yml(f'data/collection/{collection_id}.yml',
                 order_by_schema(dict(record), collection_order))
    print(f"Finished collections. Total: {len(collections)}")

    for oracle_id, record in oracles.items():
        save_yml(f'data/oracle/{oracle_id}.yml',
                 order_by_schema(dict(record), oracle_order))
    print(f"Finished oracles. Total: {len(oracles)}")

    # --- 2. Sets: collection_id becomes the collection's name -----------------
    for set_id, record in sets.items():
        entry = dict(record)
        entry['collection'] = collections[entry.pop('collection_id')]['name']
        save_yml(f'data/set/{set_id}.yml', order_by_schema(entry, set_order))
    print(f"Finished sets. Total: {len(sets)}")

    # --- 3. Decks, annotated with each card's name ----------------------------
    for deck_id, record in decks.items():
        collection = to_kebab_case(record.get('collection', 'error'))
        path = os.path.join('data', 'deck', collection,
                            f"{to_kebab_case(record.get('name'))}.yml")

        deck_map = CommentedMap(record)
        entries = deck_map.get('list')
        if isinstance(entries, dict):
            list_map = CommentedMap(entries)
            for section in DECK_SECTIONS:
                if not isinstance(list_map.get(section), dict):
                    continue
                section_map = CommentedMap(list_map[section])
                for card_ref in section_map:
                    card = cards.get(card_ref)
                    oracle = oracles.get(card['oracle_id']) if card else None
                    if oracle and oracle.get('name'):
                        section_map.yaml_add_eol_comment(oracle['name'], card_ref)
                list_map[section] = section_map
            deck_map['list'] = list_map

        save_yml(path, deck_map)
    print(f"Finished decks. Total: {len(decks)}")

    # --- 4. Cards: nested by collection type, collection and set --------------
    for card_id, record in cards.items():
        set_record = sets[record['set_id']]
        collection_id = set_record['collection_id']
        collection = collections[collection_id]
        oracle = oracles[record['oracle_id']]

        collection_folder = (f"{collection['index']}-{collection_id}"
                             if collection.get('index') else collection_id)
        set_folder = (f"{set_record['index']}-{record['set_id']}"
                      if set_record.get('index') else record['set_id'])
        filename = (f"{record['card_index']}-{oracle['name']}"
                    if record.get('card_index') else oracle['name'])

        path = '/'.join([
            'data', 'card',
            to_kebab_case(collection['type']),
            to_kebab_case(collection_folder),
            to_kebab_case(set_folder),
            to_kebab_case(filename),
        ]) + '.yml'

        entry = {
            'oracle': record['oracle_id'],
            'index': record.get('card_index'),
            'set': set_record['name'],
            'rarity': record.get('rarity', ''),
            'artist': record.get('artist', ''),
            'flavor': record.get('flavor', ''),
            'variation': record.get('variation', []),
        }

        save_yml(path, order_by_schema(entry, card_order))
    print(f"Finished cards. Total: {len(cards)}")


if __name__ == "__main__":
    split_json_to_yml()
