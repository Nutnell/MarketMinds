import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class MarketQuoteInput(BaseModel):
    """Input schema for the Market Quote Tool."""
    symbol: str = Field(..., description="The ticker symbol for the asset (e.g., 'GBPUSD', 'GOLD', '^IXIC' for NASDAQ).")

class MarketQuoteTool(BaseTool):
    name: str = "Forex, Commodity, and Index Quote Tool"
    description: str = "Retrieves the latest price quote for a given Forex pair, commodity, or stock market index."
    args_schema: Type[BaseModel] = MarketQuoteInput

    def _run(self, symbol: str) -> str:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json().get("Global Quote", {})
            if not data:
                return f"Error: No data found for symbol '{symbol}'. Ensure it's a valid Forex, commodity, or index ticker."

            return (
                f"Latest Quote for {data.get('01. symbol')}:\n"
                f"- Price: {data.get('05. price')}\n"
                f"- Last Trading Day: {data.get('07. latest trading day')}\n"
                f"- Change: {data.get('09. change')}\n"
                f"- Change Percent: {data.get('10. change percent')}"
            )
        except Exception as e:
            return f"Error fetching market data for {symbol}: {e}"