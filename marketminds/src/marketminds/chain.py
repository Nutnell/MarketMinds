from typing import Dict, Any
from pydantic import BaseModel
from langchain_core.runnables import Runnable, RunnableConfig
from crewai import Crew, Process

from .crew import MarketmindsCrewService

class SingleTaskRunnable(Runnable):
    task_name: str

    def __init__(self, task_name: str):
        self.task_name = task_name

    def invoke(self, input: str, config: RunnableConfig = None) -> Dict[str, Any]:
        crew_service = MarketmindsCrewService()

        try:
            task_method = getattr(crew_service, self.task_name)
            task = task_method()
        except AttributeError:
            return {"output": f"Error: Task method '{self.task_name}' not found in CrewService."}
            
        agent = task.agent

        inputs = {}
        if self.task_name == 'news_summary_task':
            inputs['company'] = input
        elif self.task_name == 'financial_analysis_task':
            inputs['company_ticker'] = input
        elif self.task_name == 'research_task':
            inputs['research_query'] = input

        single_task_crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

        result = single_task_crew.kickoff(inputs=inputs)
        return {"output": result}

class NewsInput(BaseModel):
    input: str
class FinancialInput(BaseModel):
    input: str
class ResearchInput(BaseModel):
    input: str

NewsAnalysisChain = SingleTaskRunnable(task_name="news_summary_task").with_types(input_type=NewsInput)
FinancialAnalysisChain = SingleTaskRunnable(task_name="financial_analysis_task").with_types(input_type=FinancialInput)
KnowledgeSearchChain = SingleTaskRunnable(task_name="research_task").with_types(input_type=ResearchInput)