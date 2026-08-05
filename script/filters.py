import json
import os

def create_properties():
    database_path = 'dist/database.json'
    if not os.path.exists(database_path):
        print(f"Error: {database_path} not found.")
        return

    with open(database_path, 'r', encoding='utf-8') as f:
        database = json.load(f)

    # Temporary properties to hold dates for sorting
    # { collection_type: { collection_name: { set_name: date_release } } }
    temp_set_data = {}
    
    # propertiess to hold unique values for other properties
    additional_props = {
        'category': set(),
        'faction': set(),
        'class': set(),
        'combat': set(),
        'set_type': set(),
        'regulation': set(),
        'rarity': set()
    }

    for card_id, card in database.items():
        # Handle set hierarchy
        ctype = card.get('collection_type')
        cname = card.get('collection_name')
        sname = card.get('set_name')
        sdate = card.get('date_release') or "9999-99"

        if ctype and cname and sname:
            if ctype not in temp_set_data:
                temp_set_data[ctype] = {}
            
            if cname not in temp_set_data[ctype]:
                temp_set_data[ctype][cname] = {}
            
            if sname not in temp_set_data[ctype][cname]:
                temp_set_data[ctype][cname][sname] = sdate
            else:
                if sdate < temp_set_data[ctype][cname][sname]:
                    temp_set_data[ctype][cname][sname] = sdate
        
        # Handle additional properties
        for prop in additional_props:
            val = card.get(prop)
            if val is None:
                continue
            
            if isinstance(val, list):
                for item in val:
                    if item:
                        additional_props[prop].add(item)
            elif val:
                additional_props[prop].add(val)

    # Define the order of collection types
    type_order = ["set", "raid", "starter", "promo"]
    
    set_hierarchy = {}

    for ctype in type_order:
        if ctype not in temp_set_data:
            continue
        
        collections_in_type = temp_set_data[ctype]
        
        if ctype in ["set", "raid", "starter"]:
            def get_sorting_key(coll_name):
                dates = collections_in_type[coll_name].values()
                earliest_date = min(dates) if dates else "9999-99"
                return (earliest_date, coll_name)
            
            sorted_collection_names = sorted(collections_in_type.keys(), key=get_sorting_key)
            
            type_map = {}
            for cname in sorted_collection_names:
                sets_dict = collections_in_type[cname]
                sorted_sets = sorted(sets_dict.keys(), key=lambda x: (sets_dict[x], x))
                type_map[cname] = sorted_sets
            
            set_hierarchy[ctype] = type_map
        else:
            sorted_collection_names = sorted(collections_in_type.keys())
            type_map = {}
            for cname in sorted_collection_names:
                sets_dict = collections_in_type[cname]
                sorted_sets = sorted(sets_dict.keys(), key=lambda x: (sets_dict[x], x))
                type_map[cname] = sorted_sets
            set_hierarchy[ctype] = type_map

    # Construct final properties
    final_properties = {
        "set": set_hierarchy
    }
    
    # Add sorted lists for additional properties
    for prop, values in additional_props.items():
        final_properties[prop] = sorted(list(values))

    with open('dist/properties.json', 'w', encoding='utf-8') as f:
        json.dump(final_properties, f, indent=2)
    print("Built dist/properties.json")

if __name__ == "__main__":
    create_properties()
