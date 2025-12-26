"""Helper utilities for MyManaBox."""

from typing import List, Optional, Dict, Any
from decimal import Decimal
from ..models import Card, CardColor
from .constants import Constants


class ColorHelper:
    """Helper for color-related operations."""
    
    @staticmethod
    def get_color_name(color_code: str) -> str:
        """Get full color name from code."""
        return Constants.COLOR_NAMES.get(color_code.upper(), 'Unknown')
    
    @staticmethod
    def classify_by_color_keywords(card_name: str) -> str:
        """Classify card by color using keywords in name."""
        name_lower = card_name.lower()
        
        for color, keywords in Constants.COLOR_KEYWORDS.items():
            if any(keyword in name_lower for keyword in keywords):
                return color
        
        return 'Multicolor'  # Default fallback
    
    @staticmethod
    def get_color_identity_string(colors: set) -> str:
        """Convert color identity set to readable string."""
        if not colors:
            return 'Colorless'
        elif len(colors) == 1:
            color = next(iter(colors))
            return Constants.COLOR_NAMES.get(color.value, 'Unknown')
        else:
            return 'Multicolor'


class PriceHelper:
    """Helper for price-related operations."""
    
    @staticmethod
    def parse_price_string(price_str: str) -> Optional[Decimal]:
        """Parse price string to Decimal."""
        if not price_str or price_str.lower() in ['', 'nan', 'none']:
            return None
        
        try:
            # Remove currency symbols and whitespace
            cleaned = price_str.replace('$', '').replace(',', '').strip()
            return Decimal(cleaned)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def format_price(price: Optional[Decimal]) -> str:
        """Format price for display."""
        if price is None:
            return ""
        return f"${price:.2f}"
    
    @staticmethod
    def classify_by_price_range(price: Optional[Decimal]) -> str:
        """Classify card into price range."""
        if price is None:
            return "No Price"
        
        price_float = float(price)
        
        for range_info in Constants.PRICE_RANGES:
            if range_info['min'] <= price_float <= range_info['max']:
                return range_info['name']
        
        return "Unknown Range"
    
    @staticmethod
    def estimate_rarity_from_price(price: Optional[Decimal]) -> str:
        """Estimate rarity based on price (heuristic)."""
        if price is None or price == 0:
            return 'common'
        
        price_float = float(price)
        
        if price_float < 0.50:
            return 'common'
        elif price_float < 2.00:
            return 'uncommon'
        elif price_float < 10.00:
            return 'rare'
        else:
            return 'mythic'


class ValidationHelper:
    """Helper for validation operations."""
    
    @staticmethod
    def validate_csv_headers(headers: List[str]) -> tuple[bool, str]:
        """Validate CSV headers for required fields."""
        required_headers = ['Name', 'Edition', 'Count']
        optional_headers = ['Purchase Price', 'Condition', 'Foil']
        
        headers_lower = [h.lower() for h in headers]
        missing_required = []
        
        for required in required_headers:
            if required.lower() not in headers_lower:
                missing_required.append(required)
        
        if missing_required:
            return False, f"Missing required headers: {', '.join(missing_required)}"
        
        return True, "Valid CSV headers"
    
    @staticmethod
    def validate_card_data(card_data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate individual card data."""
        # Check required fields
        if not card_data.get('Name'):
            return False, "Card name is required"
        
        if not card_data.get('Edition'):
            return False, "Edition is required"
        
        # Validate count
        try:
            count = int(card_data.get('Count', 1))
            if count < 1:
                return False, "Count must be positive"
        except (ValueError, TypeError):
            return False, "Invalid count value"
        
        # Validate price if present
        price_str = card_data.get('Purchase Price', '')
        if price_str:
            price = PriceHelper.parse_price_string(str(price_str))
            if price is None and price_str.strip():
                return False, "Invalid price format"
        
        return True, "Valid card data"
    
    @staticmethod
    def validate_file_format(file_path: str) -> tuple[bool, str]:
        """Validate file format and accessibility."""
        try:
            from pathlib import Path
            path = Path(file_path)
            
            if not path.exists():
                return False, "File does not exist"
            
            if not path.is_file():
                return False, "Path is not a file"
            
            if path.suffix.lower() not in ['.csv', '.txt']:
                return False, "File must be CSV or TXT format"
            
            # Check if file is readable
            try:
                with open(path, 'r') as f:
                    f.read(1)  # Try to read first character
            except Exception:
                return False, "File is not readable"
            
            return True, "Valid file format"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        import re
        
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'[^\w\s\-_.]', '', sanitized)
        sanitized = re.sub(r'\s+', '_', sanitized)
        
        # Limit length
        if len(sanitized) > 100:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:95] + ('.' + ext if ext else '')
        
        return sanitized
    
    @staticmethod
    def validate_url(url: str) -> tuple[bool, str]:
        """Validate URL format."""
        import re
        
        if not url:
            return False, "URL is required"
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        
        # Check for Moxfield specifically
        if 'moxfield.com' in url.lower():
            if '/collection/' not in url.lower():
                return False, "URL must be a Moxfield collection URL"
        
        return True, "Valid URL"
