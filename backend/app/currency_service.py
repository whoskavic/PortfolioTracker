import httpx
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()

class CurrencyService:
    """
    Service untuk convert currency secara real-time
    """
    def __init__(self):
        self.exchange_api_key = os.getenv("EXCHANGE_RATE_API_KEY", "")
        self.cache: Dict[str, dict] = {}
        self.cache_duration = timedelta(minutes=60)  # Cache 1 jam
        
    async def get_exchange_rate(
        self, 
        from_currency: str = "IDR", 
        to_currency: str = "USD"
    ) -> Optional[float]:
        """
        Get exchange rate dari from_currency ke to_currency
        
        Args:
            from_currency: Currency asal (default: IDR)
            to_currency: Currency tujuan (default: USD)
            
        Returns:
            Exchange rate atau None jika gagal
        """
        cache_key = f"{from_currency}_{to_currency}"
        
        # Check cache
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.utcnow() - cached["timestamp"] < self.cache_duration:
                return cached["rate"]
        
        try:
            rate = await self._fetch_from_exchangerate_api(from_currency, to_currency)
            
            # Cache result
            self.cache[cache_key] = {
                "rate": rate,
                "timestamp": datetime.utcnow()
            }
            
            return rate
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return None
    
    async def _fetch_from_exchangerate_api(
        self, 
        from_currency: str, 
        to_currency: str
    ) -> float:
        """
        Fetch dari ExchangeRate-API
        """
        if not self.exchange_api_key:
            raise ValueError("EXCHANGE_RATE_API_KEY not set in .env")
        
        url = f"https://v6.exchangerate-api.com/v6/{self.exchange_api_key}/pair/{from_currency}/{to_currency}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if data.get("result") == "success":
                return data["conversion_rate"]
            else:
                raise Exception(f"API Error: {data.get('error-type')}")
    
    async def _fetch_from_free_api(
        self, 
        from_currency: str, 
        to_currency: str
    ) -> float:
        """
        Fallback: Fetch dari Free Currency API (no API key needed)
        """
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if to_currency in data["rates"]:
                return data["rates"][to_currency]
            else:
                raise Exception(f"Currency {to_currency} not found")
    
    async def convert_amount(
        self, 
        amount: float, 
        from_currency: str = "IDR", 
        to_currency: str = "USD"
    ) -> Optional[float]:
        """
        Convert amount dari satu currency ke currency lain
        
        Args:
            amount: Jumlah yang akan diconvert
            from_currency: Currency asal
            to_currency: Currency tujuan
            
        Returns:
            Converted amount atau None jika gagal
        """
        rate = await self.get_exchange_rate(from_currency, to_currency)
        if rate:
            return amount * rate
        return None
    
    async def get_multiple_rates(self, base_currency: str = "USD") -> Dict[str, float]:
        """
        Get multiple exchange rates untuk base currency
        """
        if not self.exchange_api_key:
            # Use free API
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        else:
            url = f"https://v6.exchangerate-api.com/v6/{self.exchange_api_key}/latest/{base_currency}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            if self.exchange_api_key:
                return data.get("conversion_rates", {})
            else:
                return data.get("rates", {})

# Global instance
currency_service = CurrencyService()


# ============ Helper Functions ============

async def idr_to_usd(amount: float) -> Optional[float]:
    """Quick helper: Convert IDR to USD"""
    return await currency_service.convert_amount(amount, "IDR", "USD")

async def usd_to_idr(amount: float) -> Optional[float]:
    """Quick helper: Convert USD to IDR"""
    return await currency_service.convert_amount(amount, "USD", "IDR")

async def get_current_idr_usd_rate() -> Optional[float]:
    """Quick helper: Get current IDR to USD rate"""
    return await currency_service.get_exchange_rate("IDR", "USD")