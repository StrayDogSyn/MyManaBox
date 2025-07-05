import csv
import json
import os

def main():
    os.chdir(r"c:\Users\Petro\repos\MyManaBox")
    
    print("Loading cache...")
    with open('data/card_cache.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    print(f"Cache loaded: {len(cache)} entries")
    
    # Read original CSV
    print("Processing original CSV...")
    with open('data/moxfield_export.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        original_data = list(reader)
    
    print(f"Original CSV: {len(original_data)} rows")
    
    # Create enriched data
    enriched_rows = []
    for row in original_data:
        name = row['Name']
        edition = row['Edition']
        
        # Find cache entry
        cache_key = f"{name}_{edition}"
        if cache_key not in cache:
            cache_key = f"{name}_any"
        
        # Start with original data
        enriched = row.copy()
        
        # Add Scryfall data if available
        if cache_key in cache:
            data = cache[cache_key]
            enriched.update({
                'Mana Cost': data.get('mana_cost', ''),
                'CMC': data.get('cmc', ''),
                'Colors': '|'.join(data.get('colors', [])),
                'Color Identity': '|'.join(data.get('color_identity', [])),
                'Type Line': data.get('type_line', ''),
                'Rarity': data.get('rarity', ''),
                'Set Name': data.get('set_name', ''),
                'USD Price': data.get('prices', {}).get('usd', ''),
                'EUR Price': data.get('prices', {}).get('eur', ''),
                'Oracle Text': data.get('oracle_text', ''),
                'Scryfall URI': data.get('scryfall_uri', ''),
            })
        
        enriched_rows.append(enriched)
    
    # Get all possible columns
    all_columns = set()
    for row in enriched_rows:
        all_columns.update(row.keys())
    
    # Write enriched CSV
    print("Writing enriched CSV...")
    with open('data/enriched_collection_full.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_columns))
        writer.writeheader()
        writer.writerows(enriched_rows)
    
    print("Done! Created data/enriched_collection_full.csv")

if __name__ == "__main__":
    main()
