"""
CardForge Collection Repository
Collection and CollectionCard data access
"""

from typing import Optional, List, Dict
from decimal import Decimal

from cardforge.models import Collection, CollectionCard, OwnershipInfo, CollectionStats
from cardforge.database import get_connection
from .base_repository import BaseRepository


class CollectionRepository(BaseRepository[Collection]):
    """Repository for collection management."""
    
    table_name = "collections"
    model_class = Collection
    
    async def get_default(self) -> Optional[Collection]:
        """Get the default collection."""
        return await self.find_one_by(is_default=True)
    
    async def get_or_create_default(self, name: str = "Main Collection") -> Collection:
        """Get default collection or create it."""
        default = await self.get_default()
        if default:
            return default
        
        collection = Collection(
            name=name,
            description="Primary card collection",
            is_default=True
        )
        return await self.create(collection)
    
    async def get_by_name(self, name: str) -> Optional[Collection]:
        """Get collection by name."""
        return await self.find_one_by(name=name)
    
    async def get_with_cards(
        self, 
        collection_id: int,
        limit: int = 1000,
        offset: int = 0
    ) -> Optional[Collection]:
        """Get collection with cards loaded."""
        collection = await self.get(collection_id)
        if not collection:
            return None
        
        card_repo = CollectionCardRepository()
        collection.cards = await card_repo.get_by_collection(
            collection_id, limit=limit, offset=offset
        )
        
        return collection
    
    async def get_stats(self, collection_id: int) -> Optional[CollectionStats]:
        """Get collection statistics."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM v_collection_stats WHERE collection_id = ?",
                (collection_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return CollectionStats(
                collection_id=row['collection_id'],
                collection_name=row['collection_name'],
                unique_cards=row['unique_cards'] or 0,
                total_cards=row['total_cards'] or 0,
                total_value=Decimal(str(row['total_value'] or 0)),
                avg_card_value=Decimal(str(row['avg_card_value'] or 0)),
                foil_count=row['foil_count'] or 0,
                unique_sets=row['unique_sets'] or 0,
            )


class CollectionCardRepository(BaseRepository[CollectionCard]):
    """Repository for collection card entries."""
    
    table_name = "collection_cards"
    model_class = CollectionCard
    
    async def get_by_collection(
        self, 
        collection_id: int,
        limit: int = 1000,
        offset: int = 0
    ) -> List[CollectionCard]:
        """Get all cards in a collection."""
        async with get_connection() as conn:
            cursor = await conn.execute(
                f"SELECT * FROM {self.table_name} WHERE collection_id = ? LIMIT ? OFFSET ?",
                (collection_id, limit, offset)
            )
            rows = await cursor.fetchall()
            return [self.model_class.from_row(row) for row in rows]
    
    async def get_with_card_data(
        self, 
        collection_id: int,
        limit: int = 1000,
        offset: int = 0
    ) -> List[CollectionCard]:
        """Get collection cards with full card data loaded."""
        sql = """
            SELECT 
                cc.*,
                c.name as card_name,
                c.set_code,
                c.scryfall_id,
                c.oracle_id,
                c.rarity,
                c.type_line,
                c.mana_cost,
                c.cmc,
                c.colors,
                c.image_uris,
                c.prices_json
            FROM collection_cards cc
            JOIN cards c ON cc.card_id = c.id
            WHERE cc.collection_id = ?
            ORDER BY c.name
            LIMIT ? OFFSET ?
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (collection_id, limit, offset))
            rows = await cursor.fetchall()
            
            from cardforge.models import Card
            
            results = []
            for row in rows:
                cc = CollectionCard.from_row(row)
                # Create card object from joined data
                cc.card = Card(
                    id=row['card_id'],
                    name=row['card_name'],
                    set_code=row['set_code'],
                    scryfall_id=row['scryfall_id'],
                    oracle_id=row['oracle_id'],
                    rarity=row['rarity'],
                    type_line=row['type_line'],
                    mana_cost=row['mana_cost'],
                    cmc=row['cmc'],
                    colors=row['colors'],
                    image_uris=row['image_uris'],
                    prices_json=row['prices_json'],
                )
                results.append(cc)
            
            return results
    
    async def add_card(
        self,
        collection_id: int,
        card_id: int,
        quantity: int = 1,
        foil: str = "normal",
        condition: str = "NM",
        language: str = "en",
        purchase_price: Optional[Decimal] = None,
        manabox_id: Optional[str] = None,
    ) -> CollectionCard:
        """Add a card to collection (or update quantity if exists)."""
        # Check if exists with same attributes
        existing = await self.find_one_by(
            collection_id=collection_id,
            card_id=card_id,
            foil=foil,
            condition=condition,
            language=language
        )
        
        if existing:
            # Update quantity
            existing.quantity += quantity
            return await self.update(existing)
        
        # Create new entry
        cc = CollectionCard(
            collection_id=collection_id,
            card_id=card_id,
            quantity=quantity,
            foil=foil,
            condition=condition,
            language=language,
            purchase_price=purchase_price,
            manabox_id=manabox_id,
        )
        return await self.create(cc)
    
    async def update_quantity(
        self, 
        collection_card_id: int, 
        new_quantity: int
    ) -> Optional[CollectionCard]:
        """Update quantity (delete if 0)."""
        if new_quantity <= 0:
            await self.delete(collection_card_id)
            return None
        
        cc = await self.get(collection_card_id)
        if cc:
            cc.quantity = new_quantity
            return await self.update(cc)
        return None
    
    async def check_ownership(self, card_name: str) -> OwnershipInfo:
        """Check ownership of a card across all collections."""
        sql = """
            SELECT 
                c.name,
                c.oracle_id,
                c.scryfall_id,
                c.set_code,
                cc.quantity,
                cc.foil,
                cc.condition,
                cc.location,
                CASE 
                    WHEN cc.foil = 'foil' THEN json_extract(c.prices_json, '$.usd_foil')
                    ELSE json_extract(c.prices_json, '$.usd')
                END as price
            FROM collection_cards cc
            JOIN cards c ON cc.card_id = c.id
            WHERE c.name = ? OR c.oracle_id IN (
                SELECT oracle_id FROM cards WHERE name = ?
            )
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (card_name, card_name))
            rows = await cursor.fetchall()
        
        if not rows:
            return OwnershipInfo(card_name=card_name, total_quantity=0)
        
        # Aggregate data
        by_condition: Dict[str, int] = {}
        by_foil: Dict[str, int] = {}
        by_set: Dict[str, int] = {}
        locations: List[str] = []
        total_qty = 0
        total_value = Decimal('0')
        oracle_id = None
        scryfall_id = None
        
        for row in rows:
            qty = row['quantity']
            total_qty += qty
            
            oracle_id = oracle_id or row['oracle_id']
            scryfall_id = scryfall_id or row['scryfall_id']
            
            # By condition
            cond = row['condition']
            by_condition[cond] = by_condition.get(cond, 0) + qty
            
            # By foil
            foil = row['foil']
            by_foil[foil] = by_foil.get(foil, 0) + qty
            
            # By set
            set_code = row['set_code']
            by_set[set_code] = by_set.get(set_code, 0) + qty
            
            # Location
            if row['location'] and row['location'] not in locations:
                locations.append(row['location'])
            
            # Value
            if row['price']:
                total_value += Decimal(str(row['price'])) * qty
        
        return OwnershipInfo(
            card_name=card_name,
            oracle_id=oracle_id,
            scryfall_id=scryfall_id,
            total_quantity=total_qty,
            by_condition=by_condition,
            by_foil=by_foil,
            by_set=by_set,
            locations=locations,
            total_value=total_value,
        )
    
    async def find_duplicates(
        self,
        min_count: int = 2,
        min_value: Decimal = Decimal('0.50'),
        exclude_basic_lands: bool = True,
    ) -> List[Dict]:
        """Find duplicate cards eligible for selling."""
        sql = """
            SELECT 
                c.oracle_id,
                c.name,
                SUM(cc.quantity) as total_copies,
                GROUP_CONCAT(DISTINCT c.set_code) as printings,
                MAX(CAST(json_extract(c.prices_json, '$.usd') AS REAL)) as highest_price
            FROM collection_cards cc
            JOIN cards c ON cc.card_id = c.id
            WHERE 1=1
        """
        
        params = []
        
        if exclude_basic_lands:
            sql += " AND c.type_line NOT LIKE '%Basic Land%'"
        
        sql += """
            GROUP BY c.oracle_id
            HAVING SUM(cc.quantity) >= ?
            AND MAX(CAST(json_extract(c.prices_json, '$.usd') AS REAL)) >= ?
            ORDER BY highest_price DESC
        """
        params.extend([min_count, float(min_value)])
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, tuple(params))
            rows = await cursor.fetchall()
            
            return [
                {
                    'oracle_id': row['oracle_id'],
                    'name': row['name'],
                    'total_copies': row['total_copies'],
                    'printings': row['printings'].split(',') if row['printings'] else [],
                    'highest_price': Decimal(str(row['highest_price'] or 0)),
                }
                for row in rows
            ]
    
    async def get_total_value(self, collection_id: int) -> Decimal:
        """Get total collection value."""
        sql = """
            SELECT SUM(
                cc.quantity * CASE 
                    WHEN cc.foil = 'foil' THEN COALESCE(json_extract(c.prices_json, '$.usd_foil'), 0)
                    ELSE COALESCE(json_extract(c.prices_json, '$.usd'), 0)
                END
            ) as total
            FROM collection_cards cc
            JOIN cards c ON cc.card_id = c.id
            WHERE cc.collection_id = ?
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (collection_id,))
            row = await cursor.fetchone()
            return Decimal(str(row[0] or 0))
    
    async def get_by_manabox_id(self, manabox_id: str) -> Optional[CollectionCard]:
        """Find collection card by ManaBox ID."""
        return await self.find_one_by(manabox_id=manabox_id)
