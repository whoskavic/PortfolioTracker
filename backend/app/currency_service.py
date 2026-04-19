import httpx
import os
from datetime import datetime, timedelta, date, timezone
from typing import Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class CurrencyService:
    def __init__(self):
        self.exchange_api_key = os.getenv("EXCHANGE_RATE_API_KEY", "")
        self.cache: Dict[str, dict] = {}
        self.current_rate_ttl = timedelta(minutes=60)

    async def get_exchange_rate(
        self,
        from_currency: str = "IDR",
        to_currency: str = "USD",
        for_date: Optional[date] = None,
    ) -> Optional[float]:
        today = datetime.now(timezone.utc).date()
        use_historical = for_date is not None and for_date < today

        if use_historical:
            cache_key = f"{from_currency}_{to_currency}_{for_date.isoformat()}"
            # Historical rates never change — cache forever
            if cache_key in self.cache:
                return self.cache[cache_key]["rate"]
        else:
            cache_key = f"{from_currency}_{to_currency}"
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                if datetime.now(timezone.utc) - cached["timestamp"] < self.current_rate_ttl:
                    return cached["rate"]

        try:
            if use_historical:
                rate = await self._fetch_historical(from_currency, to_currency, for_date)
            else:
                rate = await self._fetch_current(from_currency, to_currency)

            self.cache[cache_key] = {"rate": rate, "timestamp": datetime.now(timezone.utc)}
            return rate
        except Exception as e:
            print(f"Error fetching exchange rate: {e}")
            return None

    async def _fetch_historical(
        self,
        from_currency: str,
        to_currency: str,
        for_date: date,
    ) -> float:
        """
        Fetch historical rate from currency-api.pages.dev (free, no key required).
        Falls back to the earliest available date if the requested date has no data.
        """
        date_str = for_date.isoformat()
        from_lower = from_currency.lower()
        to_lower = to_currency.lower()
        url = f"https://{date_str}.currency-api.pages.dev/v1/currencies/{from_lower}.json"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        rates = data.get(from_lower, {})
        if to_lower not in rates:
            raise Exception(f"Currency {to_currency} not found in historical data for {date_str}")
        return rates[to_lower]

    async def _fetch_current(
        self,
        from_currency: str,
        to_currency: str,
    ) -> float:
        """Fetch current rate from ExchangeRate-API (uses existing API key)."""
        if not self.exchange_api_key:
            return await self._fetch_current_free(from_currency, to_currency)

        url = (
            f"https://v6.exchangerate-api.com/v6/{self.exchange_api_key}"
            f"/pair/{from_currency}/{to_currency}"
        )
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        if data.get("result") == "success":
            return data["conversion_rate"]
        raise Exception(f"API Error: {data.get('error-type')}")

    async def _fetch_current_free(
        self,
        from_currency: str,
        to_currency: str,
    ) -> float:
        """Fallback: free currency-api for current rate (no key needed)."""
        from_lower = from_currency.lower()
        to_lower = to_currency.lower()
        url = f"https://latest.currency-api.pages.dev/v1/currencies/{from_lower}.json"

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        rates = data.get(from_lower, {})
        if to_lower not in rates:
            raise Exception(f"Currency {to_currency} not found")
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
