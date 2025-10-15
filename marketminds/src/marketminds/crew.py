from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool

from marketminds.tools.custom_tool import NewsSearchTool

from marketminds.tools.stock_analysis_tools import (
    CompanyProfileTool,
    FinancialStatementsTool,
)


@CrewBase
class MarketmindsCrewService:
    """Marketminds crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @tool
    def news_search_tool(self) -> NewsSearchTool:
        return NewsSearchTool()

    @tool
    def company_profile_tool(self) -> CompanyProfileTool:
        return CompanyProfileTool()

    @tool
    def financial_statements_tool(self) -> FinancialStatementsTool:
        return FinancialStatementsTool()

    @agent
    def news_and_sentiment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["news_and_sentiment_agent"],
            tools=[self.news_search_tool()],
            verbose=True,
        )

    @agent
    def stock_analyst_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["stock_analyst_agent"],
            tools=[self.company_profile_tool(), self.financial_statements_tool()],
            verbose=True,
        )

    @task
    def news_summary_task(self) -> Task:
        return Task(
            config=self.tasks_config["news_summary_task"],
            agent=self.news_and_sentiment_agent(),
            output_file="report.md",
        )

    @task
    def financial_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["financial_analysis_task"],
            agent=self.stock_analyst_agent(),
            output_file="analysis.md",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Marketminds crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
