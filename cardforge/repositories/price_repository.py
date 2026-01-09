"""
CardForge Price Repository
Price history tracking and retrieval
"""

from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime, timedelta

from cardforge.models import PriceRecord
from cardforge.database import get_connection
from .base_repository import BaseRepository


class PriceRepository(BaseRepository[PriceRecord]):
    """Repository for price history tracking."""
    
    table_name = "price_history"
    model_class = PriceRecord
    
    async def add_price_record(
        self,
        card_id: int,
        source: str,
        price_usd: Optional[Decimal] = None,
        price_usd_foil: Optional[Decimal] = None,
        price_eur: Optional[Decimal] = None,
    ) -> PriceRecord:
        """Add a price record."""
        record = PriceRecord(
            card_id=card_id,
            source=source,
            price_usd=price_usd,
            price_usd_foil=price_usd_foil,
            price_eur=price_eur,
            recorded_at=datetime.now(),
        )
        return await self.create(record)
    
    async def get_history(
        self, 
        card_id: int, 
        days: int = 30,
        source: Optional[str] = None
    ) -> List[PriceRecord]:
        """Get price history for a card."""
        cutoff = datetime.now() - timedelta(days=days)
        
        sql = """
            SELECT * FROM price_history
            WHERE card_id = ? AND recorded_at >= ?
        """
        params = [card_id, cutoff.isoformat()]
        
        if source:
            sql += " AND source = ?"
            params.append(source)
        
        sql += " ORDER BY recorded_at DESC"
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, tuple(params))
            rows = await cursor.fetchall()
            return [PriceRecord.from_row(row) for row in rows]
    
    async def get_latest_prices(self, card_ids: List[int]) -> Dict[int, PriceRecord]:
        """Get latest price record for multiple cards."""
        if not card_ids:
            return {}
        
        placeholders = ', '.join('?' * len(card_ids))
        sql = f"""
            SELECT ph.* FROM price_history ph
            INNER JOIN (
                SELECT card_id, MAX(recorded_at) as max_date
                FROM price_history
                WHERE card_id IN ({placeholders})
                GROUP BY card_id
            ) latest ON ph.card_id = latest.card_id AND ph.recorded_at = latest.max_date
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, tuple(card_ids))
            rows = await cursor.fetchall()
            
            return {
                row['card_id']: PriceRecord.from_row(row)
                for row in rows
            }
    
    async def get_price_trend(
        self, 
        card_id: int, 
        days: int = 30
    ) -> Dict[str, Decimal]:
        """Calculate price trend for a card."""
        history = await self.get_history(card_id, days=days)
        
        if len(history) < 2:
            return {
                'current': history[0].price_usd if history else Decimal('0'),
                'change': Decimal('0'),
                'change_pct': Decimal('0'),
            }
        
        current = history[0].price_usd or Decimal('0')
        oldest = history[-1].price_usd or Decimal('0')
        
        change = current - oldest
        change_pct = (change / oldest * 100) if oldest else Decimal('0')
        
        return {
            'current': current,
            'oldest': oldest,
            'change': change,
            'change_pct': change_pct,
            'high': max(r.price_usd or Decimal('0') for r in history),
            'low': min(r.price_usd or Decimal('0') for r in history if r.price_usd),
        }
    
    async def get_biggest_movers(
        self, 
        days: int = 7, 
        limit: int = 10,
        direction: str = 'up'
    ) -> List[Dict]:
        """Get cards with biggest price changes."""
        cutoff = datetime.now() - timedelta(days=days)
        
        sql = f"""
            WITH price_changes AS (
                SELECT 
                    ph.card_id,
                    c.name,
                    c.set_code,
                    FIRST_VALUE(ph.price_usd) OVER (
                        PARTITION BY ph.card_id ORDER BY ph.recorded_at DESC
                    ) as current_price,
                    FIRST_VALUE(ph.price_usd) OVER (
                        PARTITION BY ph.card_id ORDER BY ph.recorded_at ASC
                    ) as old_price
                FROM price_history ph
                JOIN cards c ON ph.card_id = c.id
                WHERE ph.recorded_at >= ?
            )
            SELECT DISTINCT
                card_id,
                name,
                set_code,
                current_price,
                old_price,
                (current_price - old_price) as change,
                ((current_price - old_price) / old_price * 100) as change_pct
            FROM price_changes
            WHERE old_price > 0
            ORDER BY change {'DESC' if direction == 'up' else 'ASC'}
            LIMIT ?
        """
        
        async with get_connection() as conn:
            cursor = await conn.execute(sql, (cutoff.isoformat(), limit))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def cleanup_old_records(self, days_to_keep: int = 365) -> int:
        """Delete price records older than specified days."""
        cutoff = datetime.now() - timedelta(days=days_to_keep)
        
        async with get_connection() as conn:
            cursor = await conn.execute(
                "DELETE FROM price_history WHERE recorded_at < ?",
                (cutoff.isoformat(),)
            )
            await conn.commit()
            return cursor.rowcount
