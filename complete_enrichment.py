#!/usr/bin/env python3
"""
Complete Collection Enrichment - Process all 1,836 cards with cached Scryfall data
"""

import csv
import json
import os
from pathlib import Path

def load_scryfall_cache():
    """Load the cached Scryfall data"""
    try:
        with open('data/card_cache.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
        return {}

def find_cached_data(cache, card_name, edition):
    """Find cached Scryfall data for a card"""
    # Try exact match first (name_edition)
    exact_key = f"{card_name}_{edition}"
    if exact_key in cache:
        return cache[exact_key]
    
    # Try generic match (name_any)
    generic_key = f"{card_name}_any"
    if generic_key in cache:
        return cache[generic_key]
    
    # Try to find any match for this card name
    for key in cache:
        if key.startswith(f"{card_name}_"):
            return cache[key]
    
    return None

def enrich_card_data(original_row, scryfall_data):
    """Enrich original card data with Scryfall information"""
    enriched = original_row.copy()
    
    if not scryfall_data:
        return enriched
    
    # Core game data
    enriched.update({
        'Mana Cost': scryfall_data.get('mana_cost', ''),
        'CMC': str(scryfall_data.get('cmc', '')),
        'Colors': '|'.join(scryfall_data.get('colors', [])),
        'Color Identity': '|'.join(scryfall_data.get('color_identity', [])),
        'Type Line': scryfall_data.get('type_line', ''),
        'Rarity': scryfall_data.get('rarity', ''),
        'Set Name': scryfall_data.get('set_name', ''),
        'Oracle Text': scryfall_data.get('oracle_text', ''),
        'Power': scryfall_data.get('power', ''),
        'Toughness': scryfall_data.get('toughness', ''),
        'Loyalty': scryfall_data.get('loyalty', ''),
        'Artist': scryfall_data.get('artist', ''),
        'Flavor Text': scryfall_data.get('flavor_text', ''),
        'Released At': scryfall_data.get('released_at', ''),
    })
    
    # Pricing data
    prices = scryfall_data.get('prices', {})
    enriched.update({
        'USD Price': prices.get('usd', ''),
        'USD Foil Price': prices.get('usd_foil', ''),
        'USD Etched Price': prices.get('usd_etched', ''),
        'EUR Price': prices.get('eur', ''),
        'EUR Foil Price': prices.get('eur_foil', ''),
        'EUR Etched Price': prices.get('eur_etched', ''),
        'TIX Price': prices.get('tix', ''),
    })
    
    # Card properties
    enriched.update({
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
        'Story Spotlight': 'Yes' if scryfall_data.get('story_spotlight', False) else '',
    })
    
    # IDs and references
    enriched.update({
        'Scryfall ID': scryfall_data.get('id', ''),
        'Oracle ID': scryfall_data.get('oracle_id', ''),
        'Arena ID': str(scryfall_data.get('arena_id', '')),
        'MTGO ID': str(scryfall_data.get('mtgo_id', '')),
        'MTGO Foil ID': str(scryfall_data.get('mtgo_foil_id', '')),
        'TCGPlayer ID': str(scryfall_data.get('tcgplayer_id', '')),
        'TCGPlayer Etched ID': str(scryfall_data.get('tcgplayer_etched_id', '')),
        'Cardmarket ID': str(scryfall_data.get('cardmarket_id', '')),
        'Scryfall URI': scryfall_data.get('scryfall_uri', ''),
    })
    
    # Image URLs
    image_uris = scryfall_data.get('image_uris', {})
    enriched.update({
        'Image Small': image_uris.get('small', ''),
        'Image Normal': image_uris.get('normal', ''),
        'Image Large': image_uris.get('large', ''),
        'Image PNG': image_uris.get('png', ''),
        'Image Art Crop': image_uris.get('art_crop', ''),
        'Image Border Crop': image_uris.get('border_crop', ''),
    })
    
    # Legalities
    legalities = scryfall_data.get('legalities', {})
    for format_name, legality in legalities.items():
        enriched[f'Legal_{format_name.replace("_", " ").title()}'] = legality
    
    # Additional fields
    enriched.update({
        'Keywords': '|'.join(scryfall_data.get('keywords', [])),
        'Produced Mana': '|'.join(scryfall_data.get('produced_mana', [])),
        'Color Indicator': '|'.join(scryfall_data.get('color_indicator', [])),
        'Hand Modifier': scryfall_data.get('hand_modifier', ''),
        'Life Modifier': scryfall_data.get('life_modifier', ''),
        'EDHREC Rank': str(scryfall_data.get('edhrec_rank', '')),
        'Penny Rank': str(scryfall_data.get('penny_rank', '')),
    })
    
    return enriched

def main():
    print("🚀 Starting complete collection enrichment...")
    print("=" * 60)
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Load Scryfall cache
    print("📂 Loading Scryfall cache...")
    cache = load_scryfall_cache()
    if not cache:
        print("❌ No cache found! Please run enrichment first.")
        return False
    
    print(f"✅ Loaded {len(cache)} cached Scryfall entries")
    
    # Load original collection
    print("📂 Loading original collection...")
    try:
        with open('data/moxfield_export.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            original_cards = list(reader)
    except Exception as e:
        print(f"❌ Error loading original CSV: {e}")
        return False
    
    print(f"✅ Loaded {len(original_cards)} cards from collection")
    
    # Process all cards
    print("🔄 Enriching all cards with Scryfall data...")
    enriched_cards = []
    cards_with_data = 0
    
    for i, card in enumerate(original_cards):
        card_name = card['Name']
        edition = card['Edition']
        
        # Find cached Scryfall data
        scryfall_data = find_cached_data(cache, card_name, edition)
        
        # Enrich the card
        enriched_card = enrich_card_data(card, scryfall_data)
        enriched_cards.append(enriched_card)
        
        if scryfall_data:
            cards_with_data += 1
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"   📊 Processed {i + 1}/{len(original_cards)} cards ({cards_with_data} enriched)")
    
    print(f"✅ Enrichment complete: {cards_with_data}/{len(original_cards)} cards have Scryfall data")
    
    # Determine all columns
    all_columns = set()
    for card in enriched_cards:
        all_columns.update(card.keys())
    
    # Sort columns logically
    base_columns = [
        'Count', 'Tradelist Count', 'Name', 'Edition', 'Condition', 'Language',
        'Foil', 'Tags', 'Last Modified', 'Collector Number', 'Alter', 'Proxy', 'Purchase Price'
    ]
    
    enriched_columns = sorted([col for col in all_columns if col not in base_columns])
    final_columns = base_columns + enriched_columns
    
    # Write enriched CSV
    output_file = 'data/enriched_collection_complete.csv'
    print(f"💾 Writing complete enriched collection to {output_file}...")
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=final_columns)
            writer.writeheader()
            writer.writerows(enriched_cards)
    except Exception as e:
        print(f"❌ Error writing CSV: {e}")
        return False
    
    # Show results
    output_path = Path(output_file)
    if output_path.exists():
        size_mb = output_path.stat().st_size / (1024 * 1024)
        
        print("\n🎉 SUCCESS! Complete enriched collection created!")
        print("=" * 60)
        print(f"📄 File: {output_file}")
        print(f"📊 Size: {size_mb:.1f} MB")
        print(f"📋 Total columns: {len(final_columns)} (vs 13 original)")
        print(f"📋 Cards processed: {len(enriched_cards)}")
        print(f"📋 Cards with Scryfall data: {cards_with_data}")
        print(f"📋 Coverage: {(cards_with_data/len(enriched_cards)*100):.1f}%")
        
        # Calculate values
        total_purchase = sum(float(card.get('Purchase Price', 0) or 0) for card in enriched_cards)
        total_usd = sum(float(card.get('USD Price', 0) or 0) * int(card.get('Count', 1)) for card in enriched_cards)
        
        if total_purchase > 0:
            print(f"\n💰 Collection Value:")
            print(f"   Purchase value: ${total_purchase:.2f}")
            print(f"   Current USD value: ${total_usd:.2f}")
            if total_usd > 0:
                appreciation = total_usd - total_purchase
                print(f"   Value change: ${appreciation:.2f} ({(appreciation/total_purchase)*100:.1f}%)")
        
        print(f"\n🎯 Your collection now includes:")
        print(f"   • Complete market pricing (USD, EUR, TIX)")
        print(f"   • Full card details (mana, colors, types, rarity)")
        print(f"   • Oracle and flavor text")
        print(f"   • Artist and set information")
        print(f"   • Legal format information")
        print(f"   • High-resolution image URLs")
        print(f"   • External platform IDs")
        print(f"   • Card properties and metadata")
        
        return True
    else:
        print("❌ Failed to create enriched collection file")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
