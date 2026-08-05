import json
import os
from datetime import datetime
from collections import defaultdict

def create_sets():
    database_path = 'dist/database.json'
    if not os.path.exists(database_path):
        print(f"Error: {database_path} not found.")
        return

    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)

    temp_set_data = defaultdict(lambda: defaultdict(dict))

    set_level_fields = [
        'set_id', 'set_type', 'set_lex',
        'collection_id', 'collection_name', 'collection_type', 'collection_lex',
        'card_total', 'card_subtotal', 'date_release', 'source',
    ]

    for card_id, card in database.items():
        ctype = card.get('collection_type')
        cname = card.get('collection_name')
        sname = card.get('set_name')

        if not (ctype and cname and sname):
            continue

        if sname not in temp_set_data[ctype][cname]:
            temp_set_data[ctype][cname][sname] = {
                field: card.get(field) for field in set_level_fields
            }

    type_order = ["set", "raid", "starter", "extra"]
    set_hierarchy = {}

    for ctype in type_order:
        if ctype not in temp_set_data:
            continue

        collections_in_type = temp_set_data[ctype]

        def get_collection_sort_key(coll_name):
            sets = collections_in_type[coll_name]
            earliest = min(
                (s.get('date_release') or "9999-99" for s in sets.values()),
                default="9999-99"
            )
            return (earliest, coll_name)

        if ctype in ["set", "raid", "starter"]:
            sorted_collection_names = sorted(collections_in_type.keys(), key=get_collection_sort_key)
        else:
            sorted_collection_names = sorted(collections_in_type.keys())

        def get_set_sort_key(sname, s):
            lex = s.get('set_lex')
            date = s.get('date_release') or "9999-99"
            
            # Tuple priority: 1. Lex, 2. Date, 3. Alphabetical Name
            return (lex is None, lex or "", date, sname)

        type_map = {}
        for cname in sorted_collection_names:
            sets_dict = collections_in_type[cname]
            
            sorted_set_names = sorted(
                sets_dict.keys(),
                key=lambda x: get_set_sort_key(x, sets_dict[x])
            )
            
            def fmt_date(raw):
                return datetime.strptime(raw, "%Y-%m").strftime("%B %Y") if raw else None

            earliest_raw = min(
                (s.get('date_release') for s in sets_dict.values() if s.get('date_release')),
                default=None
            )
            
            sorted_sets = {
                sname: {**sets_dict[sname], 'date_release': fmt_date(sets_dict[sname].get('date_release'))}
                for sname in sorted_set_names
            }
            
            type_map[cname] = {
                "set_total": sum(1 for s in sorted_sets.values() if s.get('set_type') == ctype),
                "collection_total": len(sorted_sets),
                "card_total": sum(s.get('card_total') or 0 for s in sorted_sets.values()),
                "date": fmt_date(earliest_raw),
                "list": sorted_sets,
            }

        set_hierarchy[ctype] = type_map

    with open('dist/sets.json', 'w', encoding='utf-8') as f:
        json.dump(set_hierarchy, f, indent=2)
    print("Built dist/sets.json")

if __name__ == "__main__":
    create_sets()