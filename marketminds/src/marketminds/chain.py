from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from crewai import Crew, Process

from .crew import MarketmindsCrewService


class ExtractedInputs(BaseModel):
    company: str = Field(description="The name of the company mentioned.")
    company_ticker: str = Field(description="The stock ticker symbol for the company.")
    research_query: str = Field(description="The specific research question or topic.")


extractor_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
extractor_prompt = ChatPromptTemplate.from_template(
    "Extract the company name, stock ticker, and research query from the user's request. "
    "Infer the ticker if possible. Be intelligent about defaults. "
    "User request: '{input}'"
)
InputExtractorChain = (
    extractor_prompt
    | extractor_llm.with_structured_output(ExtractedInputs)
    | RunnableLambda(lambda x: x.dict())
)


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
            verbose=2,
        )
        result = dual_task_crew.kickoff(inputs=extracted_inputs)
        combined_output = "\n\n---\n\n".join(
            [task_output.raw for task_output in result.tasks_output]
        )
        return {"output": combined_output}


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
            verbose=1,
        )

        result = full_crew.kickoff(inputs=extracted_inputs)
        combined_output = "\n\n---\n\n".join(
            [task_output.raw for task_output in result.tasks_output]
        )
        return {"output": combined_output}


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
            agents=[agent], tasks=[task], process=Process.sequential, verbose=2
        )
        result = single_task_crew.kickoff(inputs=inputs)
        return {"output": result}


class SimpleInput(BaseModel):
    input: str


NewsAnalysisChain = SingleTaskRunnable(task_name="news_summary_task").with_types(
    input_type=SimpleInput
)
FinancialAnalysisChain = SingleTaskRunnable(
    task_name="financial_analysis_task"
).with_types(input_type=SimpleInput)
KnowledgeSearchChain = SingleTaskRunnable(task_name="research_task").with_types(
    input_type=SimpleInput
)

NewsAndFinancialsChain = (
    InputExtractorChain
    | DualTaskRunnable(task_names=["news_summary_task", "financial_analysis_task"])
).with_types(input_type=SimpleInput)
NewsAndResearchChain = (
    InputExtractorChain
    | DualTaskRunnable(task_names=["news_summary_task", "research_task"])
).with_types(input_type=SimpleInput)
FinancialsAndResearchChain = (
    InputExtractorChain
    | DualTaskRunnable(task_names=["financial_analysis_task", "research_task"])
).with_types(input_type=SimpleInput)

FullAnalysisChain = (
    InputExtractorChain
    | TripleTaskRunnable(
        task_names=["news_summary_task", "financial_analysis_task", "research_task"]
    )
).with_types(input_type=SimpleInput)
