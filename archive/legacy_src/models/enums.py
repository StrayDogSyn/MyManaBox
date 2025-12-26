"""Enumerations for MTG card attributes."""

from enum import Enum
from typing import Set, List


class CardColor(Enum):
    """Magic card colors."""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"
    
    @classmethod
    def from_colors(cls, colors: List[str]) -> Set['CardColor']:
        """Convert list of color strings to CardColor set."""
        color_map = {
            'W': cls.WHITE,
            'U': cls.BLUE,
            'B': cls.BLACK,
            'R': cls.RED,
            'G': cls.GREEN,
            'C': cls.COLORLESS
        }
        return {color_map.get(color.upper(), cls.COLORLESS) for color in colors if color}


class CardRarity(Enum):
    """Magic card rarities."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    SPECIAL = "special"


class CardType(Enum):
    """Main Magic card types."""
    CREATURE = "Creature"
    INSTANT = "Instant"
    SORCERY = "Sorcery"
    ARTIFACT = "Artifact"
    ENCHANTMENT = "Enchantment"
    PLANESWALKER = "Planeswalker"
    LAND = "Land"
    TRIBAL = "Tribal"
    BATTLE = "Battle"
    
    @classmethod
    def from_type_line(cls, type_line: str) -> Set['CardType']:
        """Extract card types from type line."""
        if not type_line:
            return set()
        
        type_line = type_line.lower()
        found_types = set()
        
        for card_type in cls:
            if card_type.value.lower() in type_line:
                found_types.add(card_type)
        
        return found_types


class Condition(Enum):
    """Card condition."""
    MINT = "Mint"
    NEAR_MINT = "Near Mint"
    LIGHTLY_PLAYED = "Lightly Played"
    MODERATELY_PLAYED = "Moderately Played"
    HEAVILY_PLAYED = "Heavily Played"
    DAMAGED = "Damaged"
