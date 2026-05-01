import httpx
from datetime import datetime, timedelta, date, timezone
from typing import Optional, Dict


BASE_URL = "https://{date}.currency-api.pages.dev/v1/currencies/{currency}.json"


class CurrencyService:
    def __init__(self):
        self.cache: Dict[str, dict] = {}
        self.current_rate_ttl = timedelta(minutes=60)

    async def get_exchange_rate(
        self,
        from_currency: str = "IDR",
        to_currency: str = "USD",
        for_date: Optional[date] = None,
    ) -> Optional[float]:
        today = datetime.now(timezone.utc).date()
        is_historical = for_date is not None and for_date < today
        date_key = for_date.isoformat() if is_historical else "latest"
        cache_key = f"{from_currency}_{to_currency}_{date_key}"

        if cache_key in self.cache:
            cached = self.cache[cache_key]
            # Historical rates never change — always valid
            # Current rates expire after TTL
            if is_historical or datetime.now(timezone.utc) - cached["timestamp"] < self.current_rate_ttl:
                return cached["rate"]

        try:
            rate = await self._fetch(from_currency, to_currency, date_key)
            self.cache[cache_key] = {"rate": rate, "timestamp": datetime.now(timezone.utc)}
            return rate
        except Exception as e:
            print(f"Error fetching exchange rate ({from_currency}->{to_currency} @ {date_key}): {e}")
            return None

    async def _fetch(self, from_currency: str, to_currency: str, date_key: str) -> float:
        from_lower = from_currency.lower()
        to_lower = to_currency.lower()
        url = BASE_URL.format(date=date_key, currency=from_lower)

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        rates = data.get(from_lower, {})
        if to_lower not in rates:
            raise Exception(f"{to_currency} not found for {date_key}")
        return rates[to_lower]

    async def convert_amount(
        self,
        amount: float,
        from_currency: str = "IDR",
        to_currency: str = "USD",
        for_date: Optional[date] = None,
    ) -> Optional[float]:
        rate = await self.get_exchange_rate(from_currency, to_currency, for_date=for_date)
        return amount * rate if rate else None


# Global instance
currency_service = CurrencyService()


async def idr_to_usd(amount: float, for_date: Optional[date] = None) -> Optional[float]:
    return await currency_service.convert_amount(amount, "IDR", "USD", for_date=for_date)

async def usd_to_idr(amount: float, for_date: Optional[date] = None) -> Optional[float]:
    return await currency_service.convert_amount(amount, "USD", "IDR", for_date=for_date)

async def get_current_idr_usd_rate() -> Optional[float]:
    return await currency_service.get_exchange_rate("IDR", "USD")
