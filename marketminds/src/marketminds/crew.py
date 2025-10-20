import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool

from marketminds.tools.custom_tool import NewsSearchTool
from marketminds.tools.stock_analysis_tools import (
    PolygonQuoteTool,
    YFinanceTool,
    AlphaVantageProfileTool,
    AlphaVantageFinancialsTool,
)
from marketminds.tools.rag_tools import RAGTool
from marketminds.tools.crypto_economic_tools import (
    CryptoInfoTool,
    CryptoHistoricalTool,
    CoinCapQuoteTool,
    FREDEconomicTool,
    WorldBankEconomicTool,
)

from marketminds.tools.market_data_tools import (
    TwelveDataQuoteTool,
    FMPQuoteTool,
    AlphaVantageMarketQuoteTool,
)


def get_config_path(file_name):
    return os.path.join(os.path.dirname(__file__), "config", file_name)


@CrewBase
class MarketmindsCrewService:
    agents_config = get_config_path("agents.yaml")
    tasks_config = get_config_path("tasks.yaml")

    @tool
    def news_search_tool(self) -> NewsSearchTool:
        return NewsSearchTool()

    @tool
    def knowledge_base_tool(self) -> RAGTool:
        return RAGTool()

    @tool
    def crypto_info_tool(self) -> CryptoInfoTool:
        return CryptoInfoTool()

    @tool
    def crypto_historical_tool(self) -> CryptoHistoricalTool:
        return CryptoHistoricalTool()

    @tool
    def polygon_quote_tool(self) -> PolygonQuoteTool:
        return PolygonQuoteTool()

    @tool
    def yfinance_tool(self) -> YFinanceTool:
        return YFinanceTool()

    @tool
    def alpha_vantage_profile_tool(self) -> AlphaVantageProfileTool:
        return AlphaVantageProfileTool()

    @tool
    def alpha_vantage_financials_tool(self) -> AlphaVantageFinancialsTool:
        return AlphaVantageFinancialsTool()

    @tool
    def coingecko_crypto_profile_tool(self) -> CryptoInfoTool:
        return CryptoInfoTool()

    @tool
    def coincap_crypto_price_tool(self) -> CoinCapQuoteTool:
        return CoinCapQuoteTool()

    @tool
    def fred_economic_tool(self) -> FREDEconomicTool:
        return FREDEconomicTool()

    @tool
    def world_bank_economic_tool(self) -> WorldBankEconomicTool:
        return WorldBankEconomicTool()

    @tool
    def twelve_data_quote_tool(self) -> TwelveDataQuoteTool:
        return TwelveDataQuoteTool()

    @tool
    def alpha_vantage_market_quote_tool(self) -> AlphaVantageMarketQuoteTool:
        return AlphaVantageMarketQuoteTool()

    @tool
    def fmp_quote_tool(self) -> FMPQuoteTool:
        return FMPQuoteTool()

    @agent
    def news_and_sentiment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["news_and_sentiment_agent"],
            tools=[self.news_search_tool()],
        )

    @agent
    def stock_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_analyst_agent"],
            tools=[
                self.polygon_quote_tool(),
                self.yfinance_tool(),
                self.alpha_vantage_profile_tool(),
                self.alpha_vantage_financials_tool(),
            ],
        )

    @agent
    def research_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["research_analyst_agent"],
            tools=[self.knowledge_base_tool()],
        )

    @agent
    def crypto_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["crypto_analyst_agent"],
            tools=[
                self.coingecko_crypto_profile_tool(),
                self.crypto_historical_tool(),
                self.coincap_crypto_price_tool(),
            ],
        )

    @agent
    def economic_indicator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["economic_indicator_agent"],
            tools=[self.fred_economic_tool(), self.world_bank_economic_tool()],
        )

    @agent
    def global_markets_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["global_markets_agent"],
            tools=[
                self.twelve_data_quote_tool(),
                self.fmp_quote_tool(),
                self.alpha_vantage_market_quote_tool(),
            ],
        )

    @task
    def news_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["news_summary_task"],
            agent=self.news_and_sentiment_agent(),
        )

    @task
    def financial_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["financial_analysis_task"],
            agent=self.stock_analyst_agent(),
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
            agent=self.research_analyst_agent(),
        )

    @task
    def crypto_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["crypto_analysis_task"],
            agent=self.crypto_analyst_agent(),
        )

    @task
    def economic_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["economic_analysis_task"],
            agent=self.economic_indicator_agent(),
        )

    @task
    def global_market_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["global_market_analysis_task"],
            agent=self.global_markets_agent(),
        )

    @task
    def crypto_historical_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["crypto_historical_analysis_task"],
            agent=self.crypto_analyst_agent(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
