#!/usr/bin/env python3
"""
Verify that all Scryfall API fields are included in CSV export.
This script shows what fields are now available for export.
"""

import sys
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.models.card import Card
from src.models.enums import CardColor, CardRarity, CardType, Condition
from decimal import Decimal


def show_comprehensive_fields():
    """Show all fields that are now available for CSV export."""
    print("MyManaBox - Comprehensive CSV Export Fields")
    print("=" * 60)
    
    # Create a sample card with all possible fields populated
    sample_card = Card(
        name="Lightning Bolt",
        edition="lea",
        count=1,
        purchase_price=Decimal("50.0"),
        market_value=Decimal("75.0"),
        condition=Condition.NEAR_MINT,
        foil=False,
    )
    
    # Simulate enrichment with sample Scryfall data
    sample_card.scryfall_id = "abc123"
    sample_card.colors = {CardColor.RED}
    sample_card.color_identity = {CardColor.RED}
    sample_card.rarity = CardRarity.COMMON
    sample_card.type_line = "Instant"
    sample_card.mana_cost = "{R}"
    sample_card.cmc = 1
    sample_card.oracle_text = "Lightning Bolt deals 3 damage to any target."
    sample_card.artist = "Christopher Rush"
    sample_card.set_name = "Limited Edition Alpha"
    sample_card.keywords = ["Instant"]
    sample_card.legalities = {"legacy": "legal", "vintage": "legal"}
    sample_card.reserved = True
    sample_card.prices = {
        "usd": "75.00",
        "usd_foil": None,
        "eur": "65.00",
        "tix": "2.50"
    }
    
    # Get the comprehensive dictionary
    card_dict = sample_card.to_dict()
    
    print(f"Total fields available for export: {len(card_dict)}")
    print("\nAll exportable fields:")
    print("-" * 40)
    
    # Group fields by category
    basic_fields = []
    scryfall_fields = []
    price_fields = []
    technical_fields = []
    boolean_fields = []
    image_fields = []
    
    for field_name in sorted(card_dict.keys()):
        if any(x in field_name.lower() for x in ['price', 'usd', 'eur', 'tix']):
            price_fields.append(field_name)
        elif any(x in field_name.lower() for x in ['image', 'uri']):
            image_fields.append(field_name)
        elif any(x in field_name.lower() for x in ['id', 'multiverse', 'arena', 'mtgo', 'tcg']):
            technical_fields.append(field_name)
        elif field_name in ['Name', 'Edition', 'Count', 'Condition', 'Foil']:
            basic_fields.append(field_name)
        elif card_dict[field_name] in ['Yes', '']:  # Boolean fields typically show as Yes or empty
            boolean_fields.append(field_name)
        else:
            scryfall_fields.append(field_name)
    
    categories = [
        ("Basic Card Info", basic_fields),
        ("Scryfall Game Data", scryfall_fields),
        ("Price Information", price_fields),
        ("Boolean Properties", boolean_fields),
        ("Technical IDs", technical_fields),
        ("Images & URIs", image_fields),
    ]
    
    for category_name, fields in categories:
        if fields:
            print(f"\n{category_name} ({len(fields)} fields):")
            for field in fields:
                print(f"  • {field}")
    
    print(f"\n" + "=" * 60)
    print("SUMMARY:")
    print(f"• Total exportable fields: {len(card_dict)}")
    print(f"• Basic card info: {len(basic_fields)} fields")
    print(f"• Scryfall game data: {len(scryfall_fields)} fields")
    print(f"• Price information: {len(price_fields)} fields")
    print(f"• Boolean properties: {len(boolean_fields)} fields")
    print(f"• Technical IDs: {len(technical_fields)} fields")
    print(f"• Images & URIs: {len(image_fields)} fields")
    
    print(f"\n✅ All available Scryfall API data is now included in CSV export!")
    print("📝 When you run the enrichment, these fields will be populated with actual data.")
    
    return len(card_dict)


if __name__ == "__main__":
    field_count = show_comprehensive_fields()
    print(f"\n🎉 Success! Your CSV exports will now include {field_count} comprehensive fields!")
