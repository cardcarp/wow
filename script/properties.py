"""
Collect every distinct value of the properties worth filtering on.

Feeds select-option lists in downstream apps, so the output is nothing but
{property: [values]}, alphabetical, split into cards and decks — no hierarchy,
no counts. The lists are a reference to hand-order from, not a finished
ordering.

Requires compile.py to be run first.
"""

import json
import os

DATABASE = 'dist/database.json'
DECKS = 'dist/deck.json'
OUTPUT = 'dist/properties.json'

CARD_PROPERTIES = ('layout', 'category', 'theme', 'faction', 'class', 'type',
                   'combat', 'rarity', 'regulation')
DECK_PROPERTIES = ('format', 'group', 'theme', 'complexity', 'division')


def load(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def collect(records, properties):
    found = {prop: set() for prop in properties}

    for record in records.values():
        for prop in properties:
            value = record.get(prop)
            if value is None:
                continue
            if isinstance(value, list):
                found[prop].update(item for item in value if item)
            elif value:
                found[prop].add(value)

    return {prop: sorted(found[prop]) for prop in properties}


def create_properties():
    database = load(DATABASE)
    if database is None:
        print(f"Error: {DATABASE} not found. Run compile.py first.")
        return

    properties = {'cards': collect(database, CARD_PROPERTIES)}

    # A deck's 'group' is a folder grouping ('2011', 'raid') authored as display
    # text, not a reference, so unlike the other datasets there is no id to resolve.
    decks = load(DECKS)
    if decks is None:
        print(f"Warning: {DECKS} not found, deck properties omitted.")
    else:
        properties['decks'] = collect(decks, DECK_PROPERTIES)

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(properties, f, indent=2, ensure_ascii=False)

    summary = '; '.join(
        f"{group} ({', '.join(f'{k} {len(v)}' for k, v in values.items())})"
        for group, values in properties.items())
    print(f"Built {OUTPUT}: {summary}")


if __name__ == "__main__":
    create_properties()
