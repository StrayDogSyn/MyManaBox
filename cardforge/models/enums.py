"""
CardForge Enumerations
Type-safe enums for MTG card attributes
"""

from enum import Enum, auto
from typing import Set, List, Optional


class CardColor(str, Enum):
    """Magic card colors using standard notation."""
    WHITE = "W"
    BLUE = "U"
    BLACK = "B"
    RED = "R"
    GREEN = "G"
    COLORLESS = "C"
    
    @classmethod
    def from_string(cls, color: str) -> Optional['CardColor']:
        """Convert color string to enum."""
        color_map = {
            'W': cls.WHITE, 'WHITE': cls.WHITE,
            'U': cls.BLUE, 'BLUE': cls.BLUE,
            'B': cls.BLACK, 'BLACK': cls.BLACK,
            'R': cls.RED, 'RED': cls.RED,
            'G': cls.GREEN, 'GREEN': cls.GREEN,
            'C': cls.COLORLESS, 'COLORLESS': cls.COLORLESS,
        }
        return color_map.get(color.upper())
    
    @classmethod
    def from_list(cls, colors: List[str]) -> Set['CardColor']:
        """Convert list of color strings to set of CardColor."""
        result = set()
        for color in colors or []:
            parsed = cls.from_string(color)
            if parsed:
                result.add(parsed)
        return result
    
    @classmethod
    def to_identity_string(cls, colors: Set['CardColor']) -> str:
        """Convert color set to WUBRG-ordered string."""
        order = [cls.WHITE, cls.BLUE, cls.BLACK, cls.RED, cls.GREEN]
        return ''.join(c.value for c in order if c in colors)


class Rarity(str, Enum):
    """Card rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    MYTHIC = "mythic"
    SPECIAL = "special"
    BONUS = "bonus"
    
    @classmethod
    def from_string(cls, rarity: str) -> Optional['Rarity']:
        """Convert rarity string to enum."""
        if not rarity:
            return None
        try:
            return cls(rarity.lower())
        except ValueError:
            return None
    
    @property
    def sort_order(self) -> int:
        """Get sort order (higher = rarer)."""
        order = {
            self.COMMON: 1,
            self.UNCOMMON: 2,
            self.RARE: 3,
            self.MYTHIC: 4,
            self.SPECIAL: 5,
            self.BONUS: 0,
        }
        return order.get(self, 0)


class Condition(str, Enum):
    """Card physical condition grades."""
    MINT = "M"
    NEAR_MINT = "NM"
    LIGHTLY_PLAYED = "LP"
    MODERATELY_PLAYED = "MP"
    HEAVILY_PLAYED = "HP"
    DAMAGED = "DMG"
    
    @classmethod
    def from_string(cls, condition: str) -> 'Condition':
        """Convert condition string to enum."""
        if not condition:
            return cls.NEAR_MINT
        
        condition_map = {
            'M': cls.MINT, 'MINT': cls.MINT,
            'NM': cls.NEAR_MINT, 'NEAR MINT': cls.NEAR_MINT, 'NEAR_MINT': cls.NEAR_MINT,
            'LP': cls.LIGHTLY_PLAYED, 'LIGHTLY PLAYED': cls.LIGHTLY_PLAYED,
            'SP': cls.LIGHTLY_PLAYED,  # Some use SP for slightly played
            'MP': cls.MODERATELY_PLAYED, 'MODERATELY PLAYED': cls.MODERATELY_PLAYED,
            'HP': cls.HEAVILY_PLAYED, 'HEAVILY PLAYED': cls.HEAVILY_PLAYED,
            'DMG': cls.DAMAGED, 'DAMAGED': cls.DAMAGED, 'D': cls.DAMAGED,
        }
        return condition_map.get(condition.upper().replace('-', '_'), cls.NEAR_MINT)
    
    @property
    def price_modifier(self) -> float:
        """Get price modifier for condition."""
        modifiers = {
            self.MINT: 1.1,
            self.NEAR_MINT: 1.0,
            self.LIGHTLY_PLAYED: 0.9,
            self.MODERATELY_PLAYED: 0.75,
            self.HEAVILY_PLAYED: 0.6,
            self.DAMAGED: 0.4,
        }
        return modifiers.get(self, 1.0)
    
    @property
    def display_name(self) -> str:
        """Get human-readable condition name."""
        names = {
            self.MINT: "Mint",
            self.NEAR_MINT: "Near Mint",
            self.LIGHTLY_PLAYED: "Lightly Played",
            self.MODERATELY_PLAYED: "Moderately Played",
            self.HEAVILY_PLAYED: "Heavily Played",
            self.DAMAGED: "Damaged",
        }
        return names.get(self, "Unknown")


class FoilType(str, Enum):
    """Card foil treatment types."""
    NORMAL = "normal"
    FOIL = "foil"
    ETCHED = "etched"
    
    @classmethod
    def from_string(cls, foil: str) -> 'FoilType':
        """Convert foil string to enum."""
        if not foil:
            return cls.NORMAL
        foil_lower = foil.lower().strip()
        if foil_lower in ('foil', 'true', 'yes', '1'):
            return cls.FOIL
        if foil_lower == 'etched':
            return cls.ETCHED
        return cls.NORMAL
    
    @property
    def price_multiplier(self) -> float:
        """Get base price multiplier for foil type."""
        multipliers = {
            self.NORMAL: 1.0,
            self.FOIL: 5.4,  # TCGPlayer-style aggressive multiplier
            self.ETCHED: 2.0,
        }
        return multipliers.get(self, 1.0)


class Format(str, Enum):
    """MTG game formats."""
    COMMANDER = "commander"
    STANDARD = "standard"
    MODERN = "modern"
    LEGACY = "legacy"
    VINTAGE = "vintage"
    PIONEER = "pioneer"
    PAUPER = "pauper"
    HISTORIC = "historic"
    ALCHEMY = "alchemy"
    BRAWL = "brawl"
    OATHBREAKER = "oathbreaker"
    DUEL = "duel"  # Duel Commander
    PREMODERN = "premodern"
    OLDSCHOOL = "oldschool"
    CASUAL = "casual"
    
    @property
    def deck_size(self) -> int:
        """Get minimum deck size for format."""
        sizes = {
            self.COMMANDER: 100,
            self.BRAWL: 60,
            self.OATHBREAKER: 60,
        }
        return sizes.get(self, 60)
    
    @property
    def max_copies(self) -> int:
        """Get maximum copies of a card (excluding basics)."""
        if self in (self.COMMANDER, self.BRAWL, self.OATHBREAKER, self.DUEL):
            return 1
        return 4


class Legality(str, Enum):
    """Card legality status in a format."""
    LEGAL = "legal"
    NOT_LEGAL = "not_legal"
    BANNED = "banned"
    RESTRICTED = "restricted"
    
    @property
    def is_playable(self) -> bool:
        """Check if card can be played."""
        return self in (self.LEGAL, self.RESTRICTED)


class CardLayout(str, Enum):
    """Card layout types from Scryfall."""
    NORMAL = "normal"
    SPLIT = "split"
    FLIP = "flip"
    TRANSFORM = "transform"
    MODAL_DFC = "modal_dfc"
    MELD = "meld"
    LEVELER = "leveler"
    CLASS = "class"
    SAGA = "saga"
    ADVENTURE = "adventure"
    MUTATE = "mutate"
    PROTOTYPE = "prototype"
    BATTLE = "battle"
    PLANAR = "planar"
    SCHEME = "scheme"
    VANGUARD = "vanguard"
    TOKEN = "token"
    DOUBLE_FACED_TOKEN = "double_faced_token"
    EMBLEM = "emblem"
    AUGMENT = "augment"
    HOST = "host"
    ART_SERIES = "art_series"
    REVERSIBLE_CARD = "reversible_card"
    
    @property
    def has_multiple_faces(self) -> bool:
        """Check if layout has multiple card faces."""
        return self in (
            self.SPLIT, self.FLIP, self.TRANSFORM, self.MODAL_DFC,
            self.MELD, self.ADVENTURE, self.REVERSIBLE_CARD
        )


class CardType(str, Enum):
    """Main MTG card types."""
    CREATURE = "Creature"
    INSTANT = "Instant"
    SORCERY = "Sorcery"
    ARTIFACT = "Artifact"
    ENCHANTMENT = "Enchantment"
    PLANESWALKER = "Planeswalker"
    LAND = "Land"
    TRIBAL = "Tribal"
    BATTLE = "Battle"
    KINDRED = "Kindred"  # New type replacing Tribal
    
    @classmethod
    def from_type_line(cls, type_line: str) -> Set['CardType']:
        """Extract card types from type line."""
        if not type_line:
            return set()
        
        type_line_lower = type_line.lower()
        found_types = set()
        
        for card_type in cls:
            if card_type.value.lower() in type_line_lower:
                found_types.add(card_type)
        
        return found_types
    
    @property
    def is_permanent(self) -> bool:
        """Check if type represents a permanent."""
        return self not in (self.INSTANT, self.SORCERY)


class DeckCategory(str, Enum):
    """Deck card categories for analysis."""
    COMMANDER = "commander"
    RAMP = "ramp"
    CARD_DRAW = "card_draw"
    REMOVAL = "removal"
    PROTECTION = "protection"
    BOARD_WIPE = "board_wipe"
    FINISHER = "finisher"
    COMBO = "combo"
    TUTOR = "tutor"
    RECURSION = "recursion"
    LAND = "land"
    UTILITY = "utility"
    CREATURE = "creature"
    
    @property
    def priority(self) -> int:
        """Get category priority for buy list generation."""
        priorities = {
            self.COMMANDER: 1,
            self.COMBO: 1,
            self.PROTECTION: 2,
            self.RAMP: 2,
            self.REMOVAL: 3,
            self.CARD_DRAW: 3,
            self.TUTOR: 3,
            self.FINISHER: 3,
            self.BOARD_WIPE: 3,
            self.RECURSION: 4,
            self.LAND: 4,
            self.UTILITY: 4,
            self.CREATURE: 5,
        }
        return priorities.get(self, 5)


class BuyListStatus(str, Enum):
    """Buy list item status."""
    WANTED = "wanted"
    ORDERED = "ordered"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class SellListStatus(str, Enum):
    """Sell list item status."""
    CONSIDERING = "considering"
    LISTED = "listed"
    SOLD = "sold"
    REMOVED = "removed"


class SellReason(str, Enum):
    """Reasons for selling cards."""
    DUPLICATE = "duplicate"
    NOT_NEEDED = "not_needed"
    UPGRADE = "upgrade"
    CASH_OUT = "cash_out"
    ROTATION = "rotation"


class SyncStatus(str, Enum):
    """External platform sync status."""
    SYNCED = "synced"
    PENDING = "pending"
    CONFLICT = "conflict"
    ERROR = "error"


class SyncPlatform(str, Enum):
    """External platforms for sync."""
    MANABOX = "manabox"
    MOXFIELD = "moxfield"
    ARCHIDEKT = "archidekt"
    GOOGLE_DRIVE = "google_drive"


class GameResult(str, Enum):
    """Game result outcomes."""
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"
    SCOOP = "scoop"


class PriceSource(str, Enum):
    """Price data sources."""
    SCRYFALL = "scryfall"
    TCGPLAYER = "tcgplayer"
    CARDKINGDOM = "cardkingdom"
    CARDMARKET = "cardmarket"
