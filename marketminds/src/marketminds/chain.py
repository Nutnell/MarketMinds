from typing import Dict, Any, List, Literal
from pydantic import BaseModel, Field
from langchain_core.runnables import (
    Runnable,
    RunnableConfig,
    RunnableLambda,
    RunnableBranch,
    RunnablePassthrough,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from crewai import Crew, Process

from .crew import MarketmindsCrewService
from .templates import MASTER_ROUTER_PROMPT


class ExtractedInputs(BaseModel):
    company: str = Field(description="The name of the company mentioned.")
    company_ticker: str = Field(description="The stock ticker symbol for the company.")
    research_query: str = Field(description="The specific research question or topic.")


extractor_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extractor_prompt = ChatPromptTemplate.from_template(
    "Extract the company name, stock ticker, and research query from the user's request. Infer the ticker. User request: '{input}'"
)
InputExtractorChain = (
    extractor_prompt
    | extractor_llm.with_structured_output(ExtractedInputs)
    | RunnableLambda(lambda x: x.dict())
)


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
            return {"output": f"Error: Task method '{self.task_name}' not found."}
        agent = task.agent
        inputs = {}
        if self.task_name == "news_summary_task":
            inputs["company"] = input
        elif self.task_name == "financial_analysis_task":
            inputs["company_ticker"] = input
        elif self.task_name == "research_task":
            inputs["research_query"] = input
        single_task_crew = Crew(
            agents=[agent], tasks=[task], process=Process.sequential, verbose=0
        )
        result = single_task_crew.kickoff(inputs=inputs)
        return {"output": result.raw}


class DualTaskRunnable(Runnable):
    task_names: List[str]

    def __init__(self, task_names: List[str]):
        if len(task_names) != 2:
            raise ValueError("DualTaskRunnable requires exactly two task names.")
        self.task_names = task_names

    def invoke(
        self, extracted_inputs: Dict, config: RunnableConfig = None
    ) -> Dict[str, Any]:
        crew_service = MarketmindsCrewService()
        task1_method = getattr(crew_service, self.task_names[0])
        task2_method = getattr(crew_service, self.task_names[1])
        task1 = task1_method()
        task2 = task2_method()
        dual_task_crew = Crew(
            agents=[task1.agent, task2.agent],
            tasks=[task1, task2],
            process=Process.sequential,
            verbose=0,
        )
        result = dual_task_crew.kickoff(inputs=extracted_inputs)
        return {
            "output": "\n\n---\n\n".join(
                [task_output.raw for task_output in result.tasks_output]
            )
        }


class TripleTaskRunnable(Runnable):
    task_names: List[str]

    def __init__(self, task_names: List[str]):
        if len(task_names) != 3:
            raise ValueError("TripleTaskRunnable requires exactly three task names.")
        self.task_names = task_names

    def invoke(
        self, extracted_inputs: Dict, config: RunnableConfig = None
    ) -> Dict[str, Any]:
        crew_service = MarketmindsCrewService()
        task1_method = getattr(crew_service, self.task_names[0])
        task2_method = getattr(crew_service, self.task_names[1])
        task3_method = getattr(crew_service, self.task_names[2])
        task1 = task1_method()
        task2 = task2_method()
        task3 = task3_method()
        full_crew = Crew(
            agents=[task1.agent, task2.agent, task3.agent],
            tasks=[task1, task2, task3],
            process=Process.sequential,
            verbose=0,
        )
        result = full_crew.kickoff(inputs=extracted_inputs)
        return {
            "output": "\n\n---\n\n".join(
                [task_output.raw for task_output in result.tasks_output]
            )
        }


class SimpleInput(BaseModel):
    input: str


NewsAnalysisChain = SingleTaskRunnable(task_name="news_summary_task")
FinancialAnalysisChain = SingleTaskRunnable(task_name="financial_analysis_task")
KnowledgeSearchChain = SingleTaskRunnable(task_name="research_task")
NewsAndFinancialsChain = InputExtractorChain | DualTaskRunnable(
    task_names=["news_summary_task", "financial_analysis_task"]
)
NewsAndResearchChain = InputExtractorChain | DualTaskRunnable(
    task_names=["news_summary_task", "research_task"]
)
FinancialsAndResearchChain = InputExtractorChain | DualTaskRunnable(
    task_names=["financial_analysis_task", "research_task"]
)
FullAnalysisChain = InputExtractorChain | TripleTaskRunnable(
    task_names=["news_summary_task", "financial_analysis_task", "research_task"]
)


class RouteQuery(BaseModel):
    route: Literal[
        "news_analysis",
        "financial_analysis",
        "knowledge_base_query",
        "news_and_financials",
        "news_and_research",
        "financials_and_research",
        "full_analysis",
    ]


router_llm = ChatOpenAI(model="gpt-4o", temperature=0)
RouterChain = MASTER_ROUTER_PROMPT | router_llm.with_structured_output(RouteQuery)

MasterBranch = RunnableBranch(
    (
        lambda x: x["route"].route == "news_analysis",
        RunnableLambda(lambda x: x["input"]) | NewsAnalysisChain,
    ),
    (
        lambda x: x["route"].route == "financial_analysis",
        RunnableLambda(lambda x: x["input"]) | FinancialAnalysisChain,
    ),
    (
        lambda x: x["route"].route == "knowledge_base_query",
        RunnableLambda(lambda x: x["input"]) | KnowledgeSearchChain,
    ),
    (
        lambda x: x["route"].route == "news_and_financials",
        RunnableLambda(lambda x: x["input"]) | NewsAndFinancialsChain,
    ),
    (
        lambda x: x["route"].route == "news_and_research",
        RunnableLambda(lambda x: x["input"]) | NewsAndResearchChain,
    ),
    (
        lambda x: x["route"].route == "financials_and_research",
        RunnableLambda(lambda x: x["input"]) | FinancialsAndResearchChain,
    ),
    (
        lambda x: x["route"].route == "full_analysis",
        RunnableLambda(lambda x: x["input"]) | FullAnalysisChain,
    ),
    NewsAnalysisChain,
)

MasterChain = (
    RunnablePassthrough.assign(
        route=RunnableLambda(lambda x: {"question": x["input"]}) | RouterChain
    )
    | MasterBranch
).with_types(input_type=SimpleInput)
