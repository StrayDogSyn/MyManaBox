"""
CardForge Sync Models
External platform synchronization tracking
"""

from typing import Optional
from datetime import datetime
from pydantic import Field

from .base import BaseModel, TimestampMixin
from .enums import SyncStatus, SyncPlatform


class SyncState(BaseModel):
    """
    Tracks synchronization state with external platforms.
    
    Maps to 'sync_state' table.
    """
    
    id: Optional[int] = None
    platform: str  # 'manabox', 'moxfield', 'archidekt', 'google_drive'
    entity_type: str  # 'collection', 'deck', 'backup'
    entity_id: Optional[int] = None
    external_id: Optional[str] = None
    last_sync: Optional[datetime] = None
    sync_hash: Optional[str] = None  # Hash for change detection
    status: str = "synced"  # 'synced', 'pending', 'conflict', 'error'
    error_message: Optional[str] = None
    
    @property
    def platform_enum(self) -> SyncPlatform:
        """Get platform as enum."""
        return SyncPlatform(self.platform)
    
    @property
    def status_enum(self) -> SyncStatus:
        """Get status as enum."""
        return SyncStatus(self.status)
    
    @property
    def needs_sync(self) -> bool:
        """Check if sync is needed."""
        return self.status in ('pending', 'conflict', 'error')


class SetInfo(BaseModel):
    """
    MTG Set information.
    
    Maps to 'sets' table.
    """
    
    code: str  # Primary key
    name: str
    release_date: Optional[str] = None
    set_type: Optional[str] = None
    card_count: Optional[int] = None
    icon_svg_uri: Optional[str] = None
    scryfall_uri: Optional[str] = None
    is_digital: bool = False
    is_foil_only: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @classmethod
    def from_scryfall(cls, data: dict) -> 'SetInfo':
        """Create SetInfo from Scryfall API response."""
        return cls(
            code=data['code'],
            name=data['name'],
            release_date=data.get('released_at'),
            set_type=data.get('set_type'),
            card_count=data.get('card_count'),
            icon_svg_uri=data.get('icon_svg_uri'),
            scryfall_uri=data.get('scryfall_uri'),
            is_digital=data.get('digital', False),
            is_foil_only=data.get('foil_only', False),
        )
