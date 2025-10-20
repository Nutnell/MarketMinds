import os
import requests
import yfinance as yf
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class StockTickerInput(BaseModel):
    """Input schema for tools that take a stock ticker."""

    ticker: str = Field(
        ..., description="The stock ticker symbol (e.g., 'AAPL', 'GOOGL')."
    )

class PolygonQuoteTool(BaseTool):
    name: str = "Polygon Stock Quote Tool"
    description: str = (
        "Primary tool to get the latest daily price quote for a stock. Use this first."
    )
    args_schema: Type[BaseModel] = StockTickerInput

    def _run(self, ticker: str) -> str:
        api_key = os.getenv("POLYGON_API_KEY")
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker.upper()}/prev?adjusted=true&apiKey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("resultsCount", 0) == 0:
                return f"Error: No data found for ticker '{ticker}' from Polygon.io."
            quote = data["results"][0]
            return f"Polygon Quote for {data['ticker']}: Open: ${quote.get('o')}, High: ${quote.get('h')}, Low: ${quote.get('l')}, Close: ${quote.get('c')}, Volume: {quote.get('v'):,}"
        except Exception as e:
            return f"Error from Polygon.io: {e}. Try another tool."

class YFinanceTool(BaseTool):
    name: str = "Yahoo Finance Data Tool"
    description: str = (
        "Secondary fallback tool to get a full company profile, including financials and quotes, from Yahoo Finance."
    )
    args_schema: Type[BaseModel] = StockTickerInput

    def _run(self, ticker: str) -> str:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            market_cap = info.get("marketCap")
            total_revenue = info.get("totalRevenue")
            net_income = info.get("netIncome")
            previous_close = info.get("previousClose")
            day_high = info.get("dayHigh")
            day_low = info.get("dayLow")

            formatted_market_cap = (
                f"${market_cap:,}" if market_cap is not None else "N/A"
            )
            formatted_total_revenue = (
                f"${total_revenue:,}" if total_revenue is not None else "N/A"
            )
            formatted_net_income = (
                f"${net_income:,}" if net_income is not None else "N/A"
            )
            formatted_previous_close = (
                f"${previous_close}" if previous_close is not None else "N/A"
            )
            formatted_day_high = f"${day_high}" if day_high is not None else "N/A"
            formatted_day_low = f"${day_low}" if day_low is not None else "N/A"

            return (
                f"Full Report for {info.get('longName', ticker.upper())} from Yahoo Finance:\n"
                f"Profile: Sector is {info.get('sector', 'N/A')}. Industry is {info.get('industry', 'N/A')}. Summary: {info.get('longBusinessSummary', 'N/A')}\n"
                f"Quote: Previous Close was {formatted_previous_close}. Day's range was {formatted_day_low} - {formatted_day_high}.\n"
                f"Financials: Market Cap is {formatted_market_cap}. Total Revenue is {formatted_total_revenue}. Net Income is {formatted_net_income}."
            )
        except Exception as e:
            return f"Error fetching data from yfinance for {ticker}: {e}. Try another tool."

class AlphaVantageProfileTool(BaseTool):
    name: str = "Alpha Vantage Profile Tool"
    description: str = (
        "A last-resort fallback tool to get a company's profile (description, industry, etc.)."
    )
    args_schema: Type[BaseModel] = StockTickerInput

    def _run(self, ticker: str) -> str:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            profile_data = response.json()
            if "Note" in profile_data or not profile_data:
                return f"Error from Alpha Vantage Profile: API limit reached or data not found."
            return f"Alpha Vantage Profile for {profile_data.get('Name')}: Industry is {profile_data.get('Industry')}. Description: {profile_data.get('Description')}"
        except Exception as e:
            return f"Error fetching from Alpha Vantage Profile: {e}."

class AlphaVantageFinancialsTool(BaseTool):
    name: str = "Alpha Vantage Financials Tool"
    description: str = (
        "A last-resort fallback tool to get a company's annual income statement."
    )
    args_schema: Type[BaseModel] = StockTickerInput

    def _run(self, ticker: str) -> str:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            if "Note" in data or not data.get("annualReports"):
                return "Error from Alpha Vantage Financials: API limit reached or data not found."
            report = data["annualReports"][0]
            return f"Alpha Vantage Financials for {ticker}: Total Revenue: ${int(report.get('totalRevenue')):,}, Net Income: ${int(report.get('netIncome')):,}"
        except Exception as e:
            return f"Error fetching from Alpha Vantage Financials: {e}."
