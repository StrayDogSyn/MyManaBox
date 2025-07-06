#!/usr/bin/env python3
"""
Average Pricing Demo - Demonstrate the average pricing functionality.
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

def demo_average_pricing():
    """Demonstrate average pricing functionality."""
    print("🎯 AVERAGE PRICING IMPLEMENTATION DEMO")
    print("=" * 60)
    
    try:
        from scripts.average_pricing import AveragePricingService
        
        print("✅ Successfully imported AveragePricingService")
        
        # Initialize service
        pricing_service = AveragePricingService()
        
        # Run analysis
        print("\n🧮 Running comprehensive analysis...")
        results = pricing_service.calculate_comprehensive_averages()
        
        if results:
            print("✅ Analysis completed successfully!")
            
            # Show summary
            pricing_service.print_average_summary(results)
            
            # Highlight key insights
            print(f"\n🔍 KEY INSIGHTS:")
            
            overview = results.get('collection_overview', {})
            if overview:
                avg_price = overview.get('average_card_price', 0)
                median_price = overview.get('median_card_price', 0)
                print(f"   📊 Average vs Median: ${avg_price:.2f} vs ${median_price:.2f}")
                print(f"       (Difference indicates price distribution skew)")
            
            foil_stats = results.get('foil_analysis', {})
            if 'foil_premium' in foil_stats:
                premium = foil_stats['foil_premium']
                print(f"   ✨ Foil Premium: {premium:.2f}x regular price")
                if premium > 3:
                    print(f"       (High foil premium - foils are valuable in your collection)")
                elif premium < 2:
                    print(f"       (Low foil premium - foils close to regular pricing)")
            
            card_stats = results.get('card_level', {})
            if card_stats:
                print(f"   🔄 Duplicate Cards: {len(card_stats)} cards with multiple copies")
                print(f"       (Useful for trading or collection optimization)")
            
            tier_stats = results.get('price_tiers', {})
            if tier_stats:
                high_value_count = tier_stats.get('high', {}).get('card_count', 0) + \
                                 tier_stats.get('ultra_high', {}).get('card_count', 0)
                print(f"   💎 High-Value Cards: {high_value_count} cards worth $25+")
            
            print(f"\n📁 Results saved to JSON file for detailed analysis")
            
        else:
            print("❌ Analysis failed")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure average_pricing.py is in the scripts directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_average_pricing()
