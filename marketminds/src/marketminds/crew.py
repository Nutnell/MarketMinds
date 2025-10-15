from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, tool
from marketminds.tools.custom_tool import NewsSearchTool

@CrewBase
class MarketmindsCrew():
    """Marketminds crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @tool
    def news_search_tool(self) -> NewsSearchTool:
        """Defines and makes the News Search Tool available to the crew."""
        return NewsSearchTool()

    @agent
    def news_and_sentiment_agent(self) -> Agent:
        """Defines the News and Sentiment Agent."""
        return Agent(
            config=self.agents_config['news_and_sentiment_agent'],
            tools=[self.news_search_tool()],
            verbose=True
        )

    @task
    def news_summary_task(self) -> Task:
        """Defines the News Summary Task."""
        return Task(
            config=self.tasks_config['news_summary_task'],
            agent=self.news_and_sentiment_agent(),
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Marketminds crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )