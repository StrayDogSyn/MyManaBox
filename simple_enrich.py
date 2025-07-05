import pandas as pd
import json

# Load the original CSV
print("Loading moxfield_export.csv...")
df = pd.read_csv("data/moxfield_export.csv")
print(f"Loaded {len(df)} cards")

# Load the cache
print("Loading cache...")
with open("data/card_cache.json", "r") as f:
    cache = json.load(f)
print(f"Loaded {len(cache)} cached entries")

# Create enriched data
enriched_data = []
for idx, row in df.iterrows():
    card_name = row['Name']
    edition = row['Edition']
    
    # Try to find cache entry
    cache_key = f"{card_name}_{edition}"
    if cache_key not in cache:
        cache_key = f"{card_name}_any"
    
    # Start with original data
    enriched_row = row.to_dict()
    
    # Add Scryfall data if available
    if cache_key in cache:
        scryfall_data = cache[cache_key]
        enriched_row.update({
            'Mana_Cost': scryfall_data.get('mana_cost', ''),
            'CMC': scryfall_data.get('cmc', ''),
            'Colors': '|'.join(scryfall_data.get('colors', [])),
            'Type_Line': scryfall_data.get('type_line', ''),
            'Rarity': scryfall_data.get('rarity', ''),
            'Set_Name': scryfall_data.get('set_name', ''),
            'USD_Price': scryfall_data.get('prices', {}).get('usd', ''),
            'EUR_Price': scryfall_data.get('prices', {}).get('eur', ''),
            'Oracle_Text': scryfall_data.get('oracle_text', ''),
            'Artist': scryfall_data.get('artist', ''),
        })
    
    enriched_data.append(enriched_row)

# Save enriched CSV
enriched_df = pd.DataFrame(enriched_data)
output_file = "data/enriched_collection.csv"
enriched_df.to_csv(output_file, index=False)

print(f"Created enriched CSV with {len(enriched_df.columns)} columns")
print(f"Saved to: {output_file}")
