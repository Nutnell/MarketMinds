import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


# --- Input Schema (reusable for all tools in this file) ---
class MarketSymbolInput(BaseModel):
    """Input schema for tools that take a market symbol."""

    symbol: str = Field(
        ...,
        description="The symbol for the asset (e.g., 'EUR/USD', 'XAU/USD' for Gold, '^IXIC' for NASDAQ).",
    )


# --- Tool 1 (Primary): Twelve Data ---
class TwelveDataQuoteTool(BaseTool):
    name: str = "Twelve Data Quote Tool"
    description: str = (
        "Primary tool to get the latest price quote for Forex pairs, commodities, and indices."
    )
    args_schema: Type[BaseModel] = MarketSymbolInput

    def _run(self, symbol: str) -> str:
        api_key = os.getenv("TWELVE_DATA_API_KEY")
        url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "code" in data and data.get("code") == 404:
                return f"Error from Twelve Data: Symbol '{symbol}' not found."

            return (
                f"Twelve Data Quote for {data.get('symbol')}:\n"
                f"- Price: ${float(data.get('close')):.2f}\n"
                f"- Change: ${float(data.get('change')):.2f}\n"
                f"- Percent Change: {data.get('percent_change')}%"
            )
        except Exception as e:
            return f"Error from Twelve Data: {e}. Try another tool."


# --- Tool 2 (Fallback): FMP ---
class FMPQuoteTool(BaseTool):
    name: str = "FMP Quote Tool"
    description: str = (
        "Secondary fallback tool for Forex (e.g., EURUSD), commodities (e.g., GCUSD for Gold), and indices (e.g., ^NDX)."
    )
    args_schema: Type[BaseModel] = MarketSymbolInput

    def _run(self, symbol: str) -> str:
        api_key = os.getenv("FMP_API_KEY")
        # FMP has different formats, so we adjust the symbol
        if "/" in symbol:
            symbol = symbol.replace("/", "")  # EUR/USD -> EURUSD

        url = (
            f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={api_key}"
        )
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()[0]
            return (
                f"FMP Quote for {data.get('symbol')}:\n"
                f"- Price: ${data.get('price')}\n"
                f"- Change: ${data.get('change')}\n"
                f"- Day High: ${data.get('dayHigh')}\n"
                f"- Day Low: ${data.get('dayLow')}"
            )
        except Exception as e:
            return f"Error from FMP: {e}. Try another tool."


# --- Tool 3 (Last Resort): Alpha Vantage ---
# This is your original MarketQuoteTool, renamed for clarity
class AlphaVantageMarketQuoteTool(BaseTool):
    name: str = "Alpha Vantage Market Quote Tool"
    description: str = (
        "A last-resort fallback tool to get a price quote for a given Forex pair, commodity, or stock market index."
    )
    args_schema: Type[BaseModel] = MarketSymbolInput

    def _run(self, symbol: str) -> str:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json().get("Global Quote", {})
            if not data:
                return f"Error: No data found for symbol '{symbol}' from Alpha Vantage."

            return (
                f"Latest Alpha Vantage Quote for {data.get('01. symbol')}:\n"
                f"- Price: {data.get('05. price')}\n"
                f"- Change: {data.get('09. change')}"
            )
        except Exception as e:
            return f"Error fetching market data from Alpha Vantage: {e}"
