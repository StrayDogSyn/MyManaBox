"""
CardForge Card Repository
Card data access with FTS5 full-text search
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal

from cardforge.models import Card, CardFace, SetInfo
from cardforge.database import get_connection
from .base_repository import BaseRepository


class CardRepository(BaseRepository[Card]):
    """
    Repository for card data operations.
    
    Features:
    - Full-text search using FTS5
    - Scryfall ID lookups
    - Bulk upsert for imports
    """
    
    table_name = "cards"
    model_class = Card
    
    async def get_by_scryfall_id(self, scryfall_id: str) -> Optional[Card]:
        """Get card by Scryfall UUID."""
        return await self.find_one_by(scryfall_id=scryfall_id)
    
    async def get_by_name(
        self, 
        name: str, 
        set_code: Optional[str] = None
    ) -> Optional[Card]:
        """Get card by exact name, optionally filtered by set."""
        if set_code:
            return await self.find_one_by(name=name, set_code=set_code)
        return await self.find_one_by(name=name)
    
    async def get_by_oracle_id(self, oracle_id: str) -> List[Card]:
        """Get all printings of a card by oracle ID."""
        return await self.find_by(oracle_id=oracle_id)
    
    async def search(
        self,
        query: Optional[str] = None,
        colors: Optional[List[str]] = None,
        color_identity: Optional[List[str]] = None,
        set_code: Optional[str] = None,
        rarity: Optional[str] = None,
        type_filter: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        min_cmc: Optional[float] = None,
        max_cmc: Optional[float] = None,
        is_commander: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Card]:
        """
        Search cards with multiple filters.
        
        Uses FTS5 for text search, SQL for other filters.
        """
        conditions = []
        params = []
        
        # Base query - either FTS or regular
        if query:
            # Use FTS5 for text search
            base_sql = """
                SELECT c.* FROM cards c
                JOIN cards_fts fts ON c.id = fts.rowid
                WHERE cards_fts MATCH ?
            """
            params.append(f'"{query}"*')  # Prefix match
            table_alias = "c."
        else:
            base_sql = "SELECT * FROM cards WHERE 1=1"
            table_alias = ""
        
        # Color filter (card contains these colors)
        if colors:
            for color in colors:
                conditions.append(f"{table_alias}colors LIKE ?")
                params.append(f'%"{color}"%')
        
        # Color identity filter (exact or subset)
        if color_identity:
            # Check each color is present
            for color in color_identity:
                conditions.append(f"{table_alias}color_identity LIKE ?")
                params.append(f'%"{color}"%')
        
        # Set filter
        if set_code:
            conditions.append(f"{table_alias}set_code = ?")
            params.append(set_code.lower())
        
        # Rarity filter
        if rarity:
            conditions.append(f"{table_alias}rarity = ?")
            params.append(rarity.lower())
        
        # Type filter
        if type_filter:
            conditions.append(f"{table_alias}type_line LIKE ?")
            params.append(f'%{type_filter}%')
        
        # Price filters
        if min_price is not None:
            conditions.append(f"CAST(json_extract({table_alias}prices_json, '$.usd') AS REAL) >= ?")
            params.append(float(min_price))
        
        if max_price is not None:
            conditions.append(f"CAST(json_extract({table_alias}prices_json, '$.usd') AS REAL) <= ?")
            params.append(float(max_price))
        
        # CMC filters
        if min_cmc is not None:
            conditions.append(f"{table_alias}cmc >= ?")
            params.append(min_cmc)
        
        if max_cmc is not None:
            conditions.append(f"{table_alias}cmc <= ?")
            params.append(max_cmc)
        
        # Commander filter (legendary creatures or cards that say "can be your commander")
        if is_commander:
            conditions.append(
                f"({table_alias}type_line LIKE '%Legendary%Creature%' OR "
                f"{table_alias}oracle_text LIKE '%can be your commander%')"
            )
        
        # Build final query
        sql = base_sql
        if conditions:
            sql += " AND " + " AND ".join(conditions)
        
        sql += f" ORDER BY {table_alias}name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, tuple(params))
            rows = await cursor.fetchall()
            return [Card.from_row(row) for row in rows]
    
    async def upsert(self, card: Card) -> Card:
        """Insert or update card by scryfall_id."""
        existing = await self.get_by_scryfall_id(card.scryfall_id)
        
        if existing:
            card.id = existing.id
            return await self.update(card)
        else:
            return await self.create(card)
    
    async def bulk_upsert(self, cards: List[Card]) -> int:
        """
        Bulk upsert cards efficiently.
        
        Returns number of cards processed.
        """
        if not cards:
            return 0
        
        count = 0
        async with get_connection() as conn:
            for card in cards:
                # Check if exists
                cursor = await conn.execute(
                    "SELECT id FROM cards WHERE scryfall_id = ?",
                    (card.scryfall_id,)
                )
                existing = await cursor.fetchone()
                
                data = card.to_db_dict()
                if 'id' in data:
                    del data['id']
                
                if existing:
                    # Update
                    card.id = existing[0]
                    set_clause = ', '.join(f"{k} = ?" for k in data.keys())
                    await conn.execute(
                        f"UPDATE cards SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (*data.values(), card.id)
                    )
                else:
                    # Insert
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join('?' * len(data))
                    cursor = await conn.execute(
                        f"INSERT INTO cards ({columns}) VALUES ({placeholders})",
                        tuple(data.values())
                    )
                    card.id = cursor.lastrowid
                
                count += 1
            
            await conn.commit()
        
        return count
    
    async def get_with_faces(self, card_id: int) -> Optional[Card]:
        """Get card with its faces loaded."""
        card = await self.get(card_id)
        if not card:
            return None
        
        async with get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM card_faces WHERE card_id = ? ORDER BY face_index",
                (card_id,)
            )
            rows = await cursor.fetchall()
            card.card_faces = [CardFace.from_row(row) for row in rows]
        
        return card
    
    async def get_random(self, count: int = 1) -> List[Card]:
        """Get random cards."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT * FROM cards ORDER BY RANDOM() LIMIT ?",
                (count,)
            )
            rows = await cursor.fetchall()
            return [Card.from_row(row) for row in rows]
    
    async def get_by_tcgplayer_id(self, tcgplayer_id: int) -> Optional[Card]:
        """Get card by TCGPlayer ID."""
        return await self.find_one_by(tcgplayer_id=tcgplayer_id)


class SetRepository(BaseRepository[SetInfo]):
    """Repository for set information."""
    
    table_name = "sets"
    model_class = SetInfo
    
    async def get_by_code(self, code: str) -> Optional[SetInfo]:
        """Get set by code."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM sets WHERE code = ?",
                (code.lower(),)
            )
            row = await cursor.fetchone()
            return SetInfo.from_row(row) if row else None
    
    async def upsert(self, set_info: SetInfo) -> SetInfo:
        """Insert or update set."""
        existing = await self.get_by_code(set_info.code)
        
        data = set_info.to_db_dict()
        
        async with get_connection() as conn:
            if existing:
                # Update
                del data['code']  # Don't update primary key
                set_clause = ', '.join(f"{k} = ?" for k in data.keys())
                await conn.execute(
                    f"UPDATE sets SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE code = ?",
                    (*data.values(), set_info.code)
                )
            else:
                # Insert
                columns = ', '.join(data.keys())
                placeholders = ', '.join('?' * len(data))
                await conn.execute(
                    f"INSERT INTO sets ({columns}) VALUES ({placeholders})",
                    tuple(data.values())
                )
            
            await conn.commit()
        
        return set_info
    
    async def get_all_codes(self) -> List[str]:
        """Get all set codes."""
        async with get_connection() as conn:
            cursor = await conn.execute("SELECT code FROM sets ORDER BY release_date DESC")
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
