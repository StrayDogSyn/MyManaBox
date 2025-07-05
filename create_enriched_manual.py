#!/usr/bin/env python3
"""
Create enriched CSV by merging moxfield_export.csv with cached Scryfall data.
"""

import pandas as pd
import json
from pathlib import Path

def main():
    print("🔄 Creating enriched CSV from cached Scryfall data...")
    
    # Load original CSV
    print("📂 Loading moxfield_export.csv...")
    original_csv = "data/moxfield_export.csv"
    df = pd.read_csv(original_csv)
    print(f"✅ Loaded {len(df)} cards from original CSV")
    
    # Load cached Scryfall data
    print("📂 Loading cached Scryfall data...")
    cache_file = "data/card_cache.json"
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    print(f"✅ Loaded {len(cache)} cached card entries")
    
    # Create enriched columns
    enriched_data = []
    
    for _, row in df.iterrows():
        card_name = row['Name']
        edition = row['Edition']
        
        # Try to find exact match first, then fallback to name only
        cache_key = f"{card_name}_{edition}"
        if cache_key not in cache:
            cache_key = f"{card_name}_any"
        
        # Start with original row data
        enriched_row = row.to_dict()
        
        # Add Scryfall data if available
        if cache_key in cache:
            scryfall_data = cache[cache_key]
            
            # Add new enriched columns
            enriched_row.update({
                'Mana Cost': scryfall_data.get('mana_cost', ''),
                'CMC': scryfall_data.get('cmc', ''),
                'Colors': '|'.join(scryfall_data.get('colors', [])),
                'Color Identity': '|'.join(scryfall_data.get('color_identity', [])),
                'Type Line': scryfall_data.get('type_line', ''),
                'Rarity': scryfall_data.get('rarity', ''),
                'Set Name': scryfall_data.get('set_name', ''),
                'USD Price': scryfall_data.get('prices', {}).get('usd', ''),
                'USD Foil Price': scryfall_data.get('prices', {}).get('usd_foil', ''),
                'EUR Price': scryfall_data.get('prices', {}).get('eur', ''),
                'EUR Foil Price': scryfall_data.get('prices', {}).get('eur_foil', ''),
                'TIX Price': scryfall_data.get('prices', {}).get('tix', ''),
                'Scryfall URI': scryfall_data.get('scryfall_uri', ''),
                'Oracle Text': scryfall_data.get('oracle_text', ''),
                'Power': scryfall_data.get('power', ''),
                'Toughness': scryfall_data.get('toughness', ''),
                'Loyalty': scryfall_data.get('loyalty', ''),
                'Artist': scryfall_data.get('artist', ''),
                'Flavor Text': scryfall_data.get('flavor_text', ''),
                'Released At': scryfall_data.get('released_at', ''),
                'Border Color': scryfall_data.get('border_color', ''),
                'Frame': scryfall_data.get('frame', ''),
                'Layout': scryfall_data.get('layout', ''),
                'Reserved': 'Yes' if scryfall_data.get('reserved', False) else '',
                'Digital': 'Yes' if scryfall_data.get('digital', False) else '',
                'Reprint': 'Yes' if scryfall_data.get('reprint', False) else '',
                'Promo': 'Yes' if scryfall_data.get('promo', False) else '',
                'Full Art': 'Yes' if scryfall_data.get('full_art', False) else '',
                'Textless': 'Yes' if scryfall_data.get('textless', False) else '',
                'Oversized': 'Yes' if scryfall_data.get('oversized', False) else '',
                'Scryfall ID': scryfall_data.get('id', ''),
                'Oracle ID': scryfall_data.get('oracle_id', ''),
                'Arena ID': scryfall_data.get('arena_id', ''),
                'MTGO ID': scryfall_data.get('mtgo_id', ''),
                'TCGPlayer ID': scryfall_data.get('tcgplayer_id', ''),
                'Cardmarket ID': scryfall_data.get('cardmarket_id', ''),
            })
            
            # Add image URLs if available
            if 'image_uris' in scryfall_data:
                image_uris = scryfall_data['image_uris']
                enriched_row.update({
                    'Image Small': image_uris.get('small', ''),
                    'Image Normal': image_uris.get('normal', ''),
                    'Image Large': image_uris.get('large', ''),
                    'Image PNG': image_uris.get('png', ''),
                    'Image Art Crop': image_uris.get('art_crop', ''),
                    'Image Border Crop': image_uris.get('border_crop', ''),
                })
            
            # Add legalities if available
            if 'legalities' in scryfall_data:
                legalities = scryfall_data['legalities']
                for format_name, legality in legalities.items():
                    enriched_row[f'Legal_{format_name.title()}'] = legality
        
        enriched_data.append(enriched_row)
    
    # Create enriched DataFrame
    enriched_df = pd.DataFrame(enriched_data)
    
    # Save enriched CSV
    output_file = "data/enriched_collection.csv"
    print(f"💾 Saving enriched collection to {output_file}...")
    enriched_df.to_csv(output_file, index=False)
    
    # Show results
    file_path = Path(output_file)
    if file_path.exists():
        size_mb = file_path.stat().st_size / (1024 * 1024)
        print(f"✅ Successfully created enriched CSV!")
        print(f"📊 File: {output_file}")
        print(f"📊 Size: {size_mb:.1f} MB")
        print(f"📊 Columns: {len(enriched_df.columns)} (vs {len(df.columns)} original)")
        print(f"📊 Rows: {len(enriched_df)}")
        
        # Show added columns
        new_columns = set(enriched_df.columns) - set(df.columns)
        print(f"📋 Added {len(new_columns)} new columns with Scryfall data:")
        for col in sorted(new_columns):
            print(f"   - {col}")
        
        return True
    else:
        print("❌ Failed to create enriched CSV")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
