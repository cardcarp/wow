"""
Build the set hierarchy: type -> collection -> set.

Requires compile.py to be run first.
"""

import json
import os
import re
from collections import Counter

# Used only for the console:
PRIMARY_TYPE = 'Set'

# Presentation order:
TYPE_ORDER = ('Set', 'Raid', 'Dungeon', 'Starter', 'Promo', 'Craft', 'Badge', 'Token', 'Extra')

# Sorts last, so anything undated trails the dated records instead of leading them
UNDATED = '9999-99'

SET_PATH = 'dist/set.json'
COLLECTION_PATH = 'dist/collection.json'
CARD_PATH = 'dist/card.json'
OUTPUT_PATH = 'dist/sets.json'


def as_number(value):
    # Indices here are strings that carry more than a number: '02a' marks a
    # companion of set 2, 'reborn-01' a reprint line. Take the first run of
    # digits and let the raw string do the ordering.
    match = re.search(r'\d+', str(value or ''))
    return int(match.group()) if match else None


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ordered_types(present):
    known = [t for t in TYPE_ORDER if t in present]
    return known + sorted(set(present) - set(TYPE_ORDER))


def count_cards_per_set(card_path):
    # Actual printed count per set, tallied from the card records themselves
    if not os.path.exists(card_path):
        print(f"Warning: {card_path} not found, card totals will be 0.")
        return Counter()

    totals = Counter()
    for card in load_json(card_path).values():
        set_id = card.get('set_id')
        if set_id:
            totals[set_id] += 1

    return totals


def create_sets():
    # Mirrors how the dataset nests, and how data/ is foldered: collection type,
    # then collection, then set. A collection has exactly one type, so it appears
    # under exactly one of them, holding all of its sets.
    missing = [p for p in (SET_PATH, COLLECTION_PATH) if not os.path.exists(p)]
    if missing:
        print(f"Error: {', '.join(missing)} not found. Run compile.py first.")
        return

    sets = load_json(SET_PATH)
    collections = load_json(COLLECTION_PATH)
    card_totals = count_cards_per_set(CARD_PATH)

    grouped = {}
    orphans = []

    for set_id, record in sets.items():
        collection_id = record.get('collection_id')
        if collection_id not in collections:
            orphans.append((set_id, collection_id))
            continue

        grouped.setdefault(collections[collection_id].get('type'), {}) \
               .setdefault(collection_id, []).append({
                   'id': set_id,
                   'name': record.get('name'),
                   'index': as_number(record.get('index')),
                   'type': record.get('type'),
                   'publisher': record.get('publisher'),
                   'date': record.get('date'),
                   'card_total': card_totals.get(set_id, 0),
               })

    if orphans:
        # compile.py rejects these, so reaching here means dist/ is stale
        print(f"Warning: {len(orphans)} set(s) reference an unknown collection:")
        for set_id, collection_id in orphans[:5]:
            print(f"  - {set_id} -> {collection_id}")

    def set_key(entry):
        # The raw index, not the parsed one: it is zero-padded, so it sorts
        # '01' < '01a' < '02' on its own and keeps a companion beside its parent
        # set. Sets without one are undated companions, so they trail, by date.
        raw = sets[entry['id']].get('index')
        return (raw is None, raw or '', entry['date'] or UNDATED, entry['name'] or '')

    def collection_key(members):
        # Collection indices are too sparse to order by...
        # so the first release date leads, with the id settling any tie.
        return min((s['date'] for s in members if s['date']), default=UNDATED)

    hierarchy = []

    for collection_type in ordered_types(grouped):
        by_collection = grouped[collection_type]
        for members in by_collection.values():
            members.sort(key=set_key)

        entries = []
        for collection_id in sorted(by_collection,
                                    key=lambda c: (collection_key(by_collection[c]), c)):
            members = by_collection[collection_id]
            collection = collections[collection_id]

            entries.append({
                'id': collection_id,
                'name': collection.get('name'),
                'index': as_number(collection.get('index')),
                'date': min((s['date'] for s in members if s['date']), default=None),
                'card_total': sum(s['card_total'] for s in members),
                'list': members,
            })

        hierarchy.append({
            'type': collection_type,
            'card_total': sum(c['card_total'] for c in entries),
            'list': entries,
        })

    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(hierarchy, f, indent=2, ensure_ascii=False)

    total = sum(len(c['list']) for t in hierarchy for c in t['list'])
    primary = sum(len(c['list']) for t in hierarchy for c in t['list']
                  if t['type'] == PRIMARY_TYPE)
    print(f"Built {OUTPUT_PATH} ({len(hierarchy)} collection types, {total} sets, "
          f"{primary} of them {PRIMARY_TYPE})")


if __name__ == "__main__":
    create_sets()
