import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class CryptoInfoInput(BaseModel):
    """Input schema for the Crypto Info Tool."""

    coin_name: str = Field(
        ..., description="The name of the cryptocurrency (e.g., 'Bitcoin', 'Ethereum')."
    )


class CryptoInfoTool(BaseTool):
    name: str = "Cryptocurrency Information Search"
    description: str = (
        "Retrieves detailed information about a specific cryptocurrency, including price, market cap, and a project summary."
    )
    args_schema: Type[BaseModel] = CryptoInfoInput

    def _run(self, coin_name: str) -> str:
        api_key = os.getenv("COINGECKO_API_KEY")
        search_url = f"https://api.coingecko.com/api/v3/search?query={coin_name.lower()}&x_cg_demo_api_key={api_key}"
        try:
            search_response = requests.get(search_url)
            search_response.raise_for_status()
            coins = search_response.json().get("coins", [])
            if not coins:
                return f"Error: Could not find a cryptocurrency named '{coin_name}'."
            coin_id = coins[0]["id"]

            data_url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?x_cg_demo_api_key={api_key}"
            data_response = requests.get(data_url)
            data_response.raise_for_status()
            data = data_response.json()

            return (
                f"Name: {data['name']} ({data['symbol'].upper()})\n"
                f"Current Price (USD): ${data['market_data']['current_price']['usd']:,}\n"
                f"Market Cap (USD): ${data['market_data']['market_cap']['usd']:,}\n"
                f"Market Cap Rank: #{data['market_cap_rank']}\n"
                f"Description Snippet: {data['description']['en'].split('.')[0]}."
            )
        except Exception as e:
            return f"Error fetching crypto data: {e}"

class MacroEconomicInput(BaseModel):
    """Input schema for the Macroeconomic Data Tool."""

    indicator_name: str = Field(
        ...,
        description="The common name of the economic indicator (e.g., 'GDP', 'inflation', 'unemployment').",
    )


class MacroEconomicTool(BaseTool):
    name: str = "Macroeconomic Data Search"
    description: str = (
        "Retrieves the most recent value for major US economic indicators like GDP, inflation (CPI), and unemployment rate."
    )
    args_schema: Type[BaseModel] = MacroEconomicInput

    def _run(self, indicator_name: str) -> str:
        api_key = os.getenv("FRED_API_KEY")
        indicator_map = {
            "gdp": "GDP",
            "inflation": "CPIAUCSL",
            "unemployment": "UNRATE",
        }
        series_id = indicator_map.get(indicator_name.lower())
        if not series_id:
            return f"Error: Unknown indicator '{indicator_name}'. Try 'GDP', 'inflation', or 'unemployment'."

        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            observation = data["observations"][0]
            return f"Latest data for {indicator_name.upper()} ({series_id}):\n- Date: {observation['date']}\n- Value: {observation['value']}"
        except Exception as e:
            return f"Error fetching economic data: {e}"


class CryptoHistoricalInput(BaseModel):
    """Input schema for the Crypto Historical Data Tool."""

    coin_id: str = Field(
        ...,
        description="The CoinGecko API ID for the cryptocurrency (e.g., 'bitcoin', 'ethereum').",
    )
    days: int = Field(
        ..., description="The number of past days of data to retrieve (e.g., 7, 30)."
    )


class CryptoHistoricalTool(BaseTool):
    name: str = "Cryptocurrency Historical Chart Data"
    description: str = (
        "Fetches historical market data (price, volume) for a cryptocurrency over a specified number of days."
    )
    args_schema: Type[BaseModel] = CryptoHistoricalInput

    def _run(self, coin_id: str, days: int) -> str:
        api_key = os.getenv("COINGECKO_API_KEY")
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&x_cg_demo_api_key={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            prices = data["prices"]
            if not prices:
                return f"No historical data found for {coin_id}."

            high_price = max(p[1] for p in prices)
            low_price = min(p[1] for p in prices)
            avg_price = sum(p[1] for p in prices) / len(prices)

            return (
                f"Historical Data for {coin_id.capitalize()} over the last {days} days:\n"
                f"- Highest Price (USD): ${high_price:,.2f}\n"
                f"- Lowest Price (USD): ${low_price:,.2f}\n"
                f"- Average Price (USD): ${avg_price:,.2f}"
            )
        except Exception as e:
            return f"Error fetching historical crypto data: {e}"
