"""
CardForge TCGPlayer Client
Async TCGPlayer API integration for pricing
"""

from typing import Optional, List, Dict, Any
from datetime import timedelta
from decimal import Decimal

from .base_client import BaseAPIClient


class TCGPlayerClient(BaseAPIClient):
    """
    Async TCGPlayer API client.
    
    Requires API credentials (Public Key and Private Key).
    Rate limit: Varies by subscription tier.
    """
    
    base_url = "https://api.tcgplayer.com"
    rate_limit = 5.0  # Conservative default
    cache_ttl = timedelta(hours=1)  # Prices update frequently
    
    def __init__(
        self,
        public_key: str,
        private_key: str,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._public_key = public_key
        self._private_key = private_key
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None
    
    async def _ensure_authenticated(self):
        """Ensure we have a valid access token."""
        import time
        
        if self._access_token and self._token_expires_at:
            if time.time() < self._token_expires_at - 60:  # 60s buffer
                return
        
        await self._authenticate()
    
    async def _authenticate(self):
        """Get access token from TCGPlayer."""
        import time
        import aiohttp
        
        auth_url = f"{self.base_url}/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self._public_key,
            "client_secret": self._private_key,
        }
        
        async with self.session.post(
            auth_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            response.raise_for_status()
            result = await response.json()
        
        self._access_token = result["access_token"]
        self._token_expires_at = time.time() + result.get("expires_in", 3600)
        
        # Update headers with token
        self._headers["Authorization"] = f"Bearer {self._access_token}"
    
    async def _request(self, method: str, endpoint: str, **kwargs):
        """Override to add authentication."""
        await self._ensure_authenticated()
        return await super()._request(method, endpoint, **kwargs)
    
    async def health_check(self) -> bool:
        """Check if TCGPlayer API is reachable."""
        try:
            await self._ensure_authenticated()
            return True
        except Exception:
            return False
    
    # =====================
    # Category Methods
    # =====================
    
    async def get_categories(self) -> List[Dict[str, Any]]:
        """Get all product categories (Magic is categoryId 1)."""
        result = await self.get("/catalog/categories")
        return result.get("results", [])
    
    async def get_mtg_category_id(self) -> int:
        """Get the MTG category ID (should be 1)."""
        return 1  # Magic: The Gathering
    
    # =====================
    # Product/Card Methods
    # =====================
    
    async def search_products(
        self,
        query: str,
        category_id: int = 1,  # MTG
        limit: int = 50,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Search for products by name."""
        params = {
            "categoryId": category_id,
            "productName": query,
            "limit": limit,
            "offset": offset,
        }
        return await self.get("/catalog/products", params=params)
    
    async def get_product(self, product_id: int) -> Dict[str, Any]:
        """Get a specific product by ID."""
        return await self.get(f"/catalog/products/{product_id}")
    
    async def get_products(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple products by IDs (max 250)."""
        if len(product_ids) > 250:
            raise ValueError("Maximum 250 product IDs per request")
        
        ids_str = ",".join(str(id) for id in product_ids)
        result = await self.get(f"/catalog/products/{ids_str}")
        return result.get("results", [])
    
    async def get_product_skus(self, product_id: int) -> List[Dict[str, Any]]:
        """Get SKUs (variants) for a product."""
        result = await self.get(f"/catalog/products/{product_id}/skus")
        return result.get("results", [])
    
    # =====================
    # Pricing Methods
    # =====================
    
    async def get_product_prices(self, product_ids: List[int]) -> List[Dict[str, Any]]:
        """Get prices for products."""
        if len(product_ids) > 250:
            raise ValueError("Maximum 250 product IDs per request")
        
        ids_str = ",".join(str(id) for id in product_ids)
        result = await self.get(f"/pricing/product/{ids_str}")
        return result.get("results", [])
    
    async def get_sku_prices(self, sku_ids: List[int]) -> List[Dict[str, Any]]:
        """Get prices for specific SKUs."""
        if len(sku_ids) > 250:
            raise ValueError("Maximum 250 SKU IDs per request")
        
        ids_str = ",".join(str(id) for id in sku_ids)
        result = await self.get(f"/pricing/sku/{ids_str}")
        return result.get("results", [])
    
    async def get_market_prices(
        self, 
        product_ids: List[int]
    ) -> Dict[int, Dict[str, Decimal]]:
        """
        Get market prices for products formatted nicely.
        
        Returns dict mapping product_id to price dict.
        """
        prices_data = await self.get_product_prices(product_ids)
        
        result = {}
        for price in prices_data:
            product_id = price.get("productId")
            if product_id:
                result[product_id] = {
                    "low": Decimal(str(price.get("lowPrice", 0) or 0)),
                    "mid": Decimal(str(price.get("midPrice", 0) or 0)),
                    "high": Decimal(str(price.get("highPrice", 0) or 0)),
                    "market": Decimal(str(price.get("marketPrice", 0) or 0)),
                    "direct_low": Decimal(str(price.get("directLowPrice", 0) or 0)),
                }
        
        return result
    
    # =====================
    # Group/Set Methods  
    # =====================
    
    async def get_groups(
        self, 
        category_id: int = 1,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get product groups (sets) in a category."""
        params = {
            "categoryId": category_id,
            "limit": limit,
            "offset": offset,
        }
        return await self.get("/catalog/groups", params=params)
    
    async def get_group(self, group_id: int) -> Dict[str, Any]:
        """Get a specific group (set) by ID."""
        return await self.get(f"/catalog/groups/{group_id}")
    
    # =====================
    # Buylist Methods
    # =====================
    
    async def get_buylist_prices(self, sku_ids: List[int]) -> List[Dict[str, Any]]:
        """Get buylist prices for SKUs."""
        if len(sku_ids) > 250:
            raise ValueError("Maximum 250 SKU IDs per request")
        
        ids_str = ",".join(str(id) for id in sku_ids)
        result = await self.get(f"/pricing/buy/sku/{ids_str}")
        return result.get("results", [])
    
    async def get_product_buylist_prices(
        self, 
        product_ids: List[int]
    ) -> Dict[int, Decimal]:
        """
        Get buylist prices for products.
        
        Returns dict mapping product_id to buylist price.
        """
        prices_data = await self.get_buylist_prices(product_ids)
        
        return {
            price.get("productId"): Decimal(str(price.get("buyPrice", 0) or 0))
            for price in prices_data
            if price.get("productId")
        }
    
    # =====================
    # Condition Methods
    # =====================
    
    async def get_conditions(self, category_id: int = 1) -> List[Dict[str, Any]]:
        """Get condition options for a category."""
        result = await self.get(f"/catalog/categories/{category_id}/conditions")
        return result.get("results", [])
    
    async def get_printings(self, category_id: int = 1) -> List[Dict[str, Any]]:
        """Get printing types (foil, non-foil, etc.)."""
        result = await self.get(f"/catalog/categories/{category_id}/printings")
        return result.get("results", [])
