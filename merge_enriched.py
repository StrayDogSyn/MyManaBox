#!/usr/bin/env python3
"""
Create enriched CSV by merging the original Moxfield export with cached Scryfall data
"""

import csv
import json
from pathlib import Path

def load_cache():
    """Load the Scryfall cache"""
    with open('data/card_cache.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_scryfall_data(cache, card_name, edition):
    """Get Scryfall data for a card"""
    # Try exact match first
    key = f"{card_name}_{edition}"
    if key in cache:
        return cache[key]
    
    # Try any edition
    key = f"{card_name}_any"
    if key in cache:
        return cache[key]
    
    return None

def main():
    print("🔄 Creating enriched CSV from cache data...")
    
    # Load cache
    cache = load_cache()
    print(f"✅ Loaded {len(cache)} cached entries")
    
    # Define enriched columns
    base_columns = [
        'Count', 'Tradelist Count', 'Name', 'Edition', 'Condition', 'Language',
        'Foil', 'Tags', 'Last Modified', 'Collector Number', 'Alter', 'Proxy', 'Purchase Price'
    ]
    
    enriched_columns = base_columns + [
        'Mana Cost', 'CMC', 'Colors', 'Color Identity', 'Type Line', 'Rarity', 'Set Name',
        'USD Price', 'USD Foil Price', 'EUR Price', 'EUR Foil Price', 'TIX Price',
        'Oracle Text', 'Power', 'Toughness', 'Loyalty', 'Artist', 'Flavor Text',
        'Released At', 'Border Color', 'Frame', 'Layout', 'Reserved', 'Digital',
        'Reprint', 'Promo', 'Full Art', 'Textless', 'Oversized', 'Scryfall ID',
        'Oracle ID', 'Arena ID', 'MTGO ID', 'TCGPlayer ID', 'Cardmarket ID',
        'Image Small', 'Image Normal', 'Image Large', 'Image PNG', 'Image Art Crop',
        'Image Border Crop', 'Scryfall URI'
    ]
    
    # Read original CSV and create enriched version
    with open('data/moxfield_export.csv', 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        with open('data/enriched_collection.csv', 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=enriched_columns)
            writer.writeheader()
            
            rows_processed = 0
            for row in reader:
                # Start with original data
                enriched_row = {}
                for col in base_columns:
                    enriched_row[col] = row.get(col, '')
                
                # Get Scryfall data
                card_name = row['Name']
                edition = row['Edition']
                scryfall_data = get_scryfall_data(cache, card_name, edition)
                
                if scryfall_data:
                    # Add enriched data
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
                        'Scryfall URI': scryfall_data.get('scryfall_uri', ''),
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
                else:
                    # Fill empty values for missing enrichment columns
                    for col in enriched_columns:
                        if col not in enriched_row:
                            enriched_row[col] = ''
                
                writer.writerow(enriched_row)
                rows_processed += 1
                
                if rows_processed % 100 == 0:
                    print(f"📊 Processed {rows_processed} rows...")
    
    # Show results
    output_path = Path('data/enriched_collection.csv')
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"\n✅ Successfully created enriched CSV!")
        print(f"📊 File: data/enriched_collection.csv")
        print(f"📊 Size: {size_mb:.1f} MB")
        print(f"📊 Rows processed: {rows_processed}")
        print(f"📊 Columns: {len(enriched_columns)} (vs 13 original)")
        print(f"📊 Added columns: {len(enriched_columns) - 13}")
        print("\n🎯 The enriched CSV now includes:")
        print("   • Current market prices (USD, EUR, TIX)")
        print("   • Card details (mana cost, colors, type, rarity)")
        print("   • Oracle text and flavor text")
        print("   • Artist and set information") 
        print("   • Card properties (reserved, promo, etc.)")
        print("   • Image URLs for all sizes")
        print("   • External IDs (Scryfall, Arena, MTGO, etc.)")
        return True
    else:
        print("❌ Failed to create enriched CSV")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\nDone! {'✅' if success else '❌'}")
