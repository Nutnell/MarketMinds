import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class CompanyProfileInput(BaseModel):
    """Input schema for the Company Profile Tool."""
    ticker: str = Field(..., description="The stock ticker symbol of the company (e.g., 'AAPL').")

class CompanyProfileTool(BaseTool):
    name: str = "Company Profile Search"
    description: str = "Retrieves a detailed profile of a public company given its stock ticker."
    args_schema: Type[BaseModel] = CompanyProfileInput

    def _run(self, ticker: str) -> str:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={api_key}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            profile_data = response.json()

            if "Note" in profile_data:
                 return f"Error: Alpha Vantage API limit reached or invalid ticker. Response: {profile_data.get('Note')}"
            
            if not profile_data:
                return f"No profile data found for {ticker}."

            formatted_profile = (
                f"Company: {profile_data.get('Name')} ({profile_data.get('Symbol')})\n"
                f"Industry: {profile_data.get('Industry')}\n"
                f"Sector: {profile_data.get('Sector')}\n"
                f"Market Cap: ${int(profile_data.get('MarketCapitalization')):,}\n"
                f"Description: {profile_data.get('Description')}"
            )
            return formatted_profile
        except Exception as e:
            return f"Error fetching company overview for {ticker}: {e}"

class FinancialStatementInput(BaseModel):
    """Input schema for the Financial Statements Tool."""
    ticker: str = Field(..., description="The stock ticker symbol of the company (e.g., 'AAPL').")

class FinancialStatementsTool(BaseTool):
    name: str = "Financial Statements Search"
    description: str = "Retrieves the most recent annual income statement for a public company."
    args_schema: Type[BaseModel] = FinancialStatementInput

    def _run(self, ticker: str) -> str:
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={api_key}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "Note" in data:
                 return f"Error: Alpha Vantage API limit reached. Response: {data.get('Note')}"

            report = data.get('annualReports', [])[0]

            formatted_report = (
                f"Latest Annual Income Statement for {ticker} (Fiscal Year Ending {report.get('fiscalDateEnding')}):\n"
                f"- Total Revenue: ${int(report.get('totalRevenue')):,}\n"
                f"- Gross Profit: ${int(report.get('grossProfit')):,}\n"
                f"- Operating Income: ${int(report.get('operatingIncome')):,}\n"
                f"- Net Income: ${int(report.get('netIncome')):,}"
            )
            return formatted_report
        except Exception as e:
            return f"Error fetching income statement for {ticker}: {e}. The API might have usage limits."