import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


# --- Crypto Tools ---
class CryptoInfoInput(BaseModel):
    coin_name: str = Field(
        ..., description="The name of the cryptocurrency (e.g., 'Bitcoin', 'Ethereum')."
    )


class CryptoInfoTool(BaseTool):
    name: str = "CoinGecko Crypto Profile Tool"
    description: str = (
        "Primary tool to retrieve detailed information about a cryptocurrency."
    )
    args_schema: Type[BaseModel] = CryptoInfoInput

    # ... (rest of the class is unchanged)
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
                f"Price (USD): ${data['market_data']['current_price']['usd']:,}\n"
                f"Market Cap (USD): ${data['market_data']['market_cap']['usd']:,}\n"
                f"Description: {data['description']['en'].split('.')[0]}."
            )
        except Exception as e:
            return f"Error from CoinGecko: {e}. Try another tool."


class CoinCapQuoteTool(BaseTool):
    name: str = "CoinCap Crypto Price Tool"
    description: str = "A fallback tool to get the real-time price of a cryptocurrency."
    args_schema: Type[BaseModel] = CryptoInfoInput  # Re-use the same input schema

    def _run(self, coin_name: str) -> str:
        url = f"https://api.coincap.io/v2/assets/{coin_name.lower()}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()["data"]
            price = float(data["priceUsd"])
            return f"CoinCap Quote for {data['name']} ({data['symbol']}): Price (USD): ${price:,.2f}"
        except Exception as e:
            return f"Error from CoinCap: {e}."


class CryptoHistoricalInput(BaseModel):
    coin_id: str = Field(
        ..., description="The CoinGecko ID for the cryptocurrency (e.g., 'bitcoin')."
    )
    days: int = Field(..., description="The number of past days of data to retrieve.")


class CryptoHistoricalTool(BaseTool):
    name: str = "Cryptocurrency Historical Chart Data"
    description: str = (
        "Fetches historical market data for a cryptocurrency over a specified number of days."
    )
    args_schema: Type[BaseModel] = CryptoHistoricalInput

    def _run(self, coin_id: str, days: int) -> str:
        # ... (implementation is unchanged)
        api_key = os.getenv("COINGECKO_API_KEY")
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&x_cg_demo_api_key={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            prices = data["prices"]
            if not prices:
                return f"No historical data found for {coin_id}."
            high = max(p[1] for p in prices)
            low = min(p[1] for p in prices)
            avg = sum(p[1] for p in prices) / len(prices)
            return f"Historical Data for {coin_id.capitalize()} ({days} days):\n- High: ${high:,.2f}\n- Low: ${low:,.2f}\n- Average: ${avg:,.2f}"
        except Exception as e:
            return f"Error fetching historical crypto data: {e}"


# --- Economic Tools ---
class EconomicIndicatorInput(BaseModel):
    indicator_name: str = Field(
        ...,
        description="The common name of the economic indicator (e.g., 'GDP', 'inflation').",
    )


class FREDEconomicTool(BaseTool):
    name: str = "FRED US Economic Data Tool"
    description: str = (
        "Primary tool for US economic indicators like GDP, inflation (CPI), and unemployment rate."
    )
    args_schema: Type[BaseModel] = EconomicIndicatorInput

    def _run(self, indicator_name: str) -> str:
        # ... (implementation is unchanged)
        api_key = os.getenv("FRED_API_KEY")
        indicator_map = {
            "gdp": "GDP",
            "inflation": "CPIAUCSL",
            "unemployment": "UNRATE",
        }
        series_id = indicator_map.get(indicator_name.lower())
        if not series_id:
            return f"Error: Unknown indicator '{indicator_name}'."
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            obs = response.json()["observations"][0]
            return f"Latest FRED data for {indicator_name.upper()}: Date: {obs['date']}, Value: {obs['value']}"
        except Exception as e:
            return f"Error from FRED: {e}. Try another tool."


class WorldBankInput(BaseModel):
    indicator_name: str = Field(
        ..., description="The economic indicator (e.g., 'GDP')."
    )
    country_code: str = Field(
        ...,
        description="The 3-letter ISO code for the country (e.g., 'USA', 'DEU' for Germany).",
    )


class WorldBankEconomicTool(BaseTool):
    name: str = "World Bank Global Economic Data Tool"
    description: str = (
        "A fallback tool to retrieve economic indicators for any country."
    )
    args_schema: Type[BaseModel] = WorldBankInput

    def _run(self, indicator_name: str, country_code: str) -> str:
        # ... (implementation is unchanged)
        indicator_map = {"gdp": "NY.GDP.MKTP.CD", "inflation": "FP.CPI.TOTL.ZG"}
        indicator_code = indicator_map.get(indicator_name.lower())
        if not indicator_code:
            return f"Error: Indicator '{indicator_name}' not supported."
        url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}?format=json&date=2020:2025&per_page=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()[1]
            if not data:
                return f"No World Bank data found."
            point = data[0]
            return f"Latest World Bank data for {point['indicator']['value']} in {point['country']['value']}:\n- Year: {point['date']}\n- Value: {point['value']:,.2f}"
        except Exception as e:
            return f"Error from World Bank: {e}."
