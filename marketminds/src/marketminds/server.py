from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .crew import MarketmindsCrewService

app = FastAPI(
    title="MarketMinds AI API",
    description="An AI-powered API for financial research and analysis.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CrewRequest(BaseModel):
    company: str
    company_ticker: str

crew_service = MarketmindsCrewService()

@app.get("/", tags=["Root"])
def read_root():
    """A simple endpoint to confirm the server is running."""
    return {"status": "ok", "message": "Welcome to the MarketMinds AI API!"}

@app.post("/api/v1/run-crew", tags=["Crew"])
def run_crew(request: CrewRequest):
    """
    Runs the multi-agent crew to perform financial analysis.
    """
    try:
        inputs = {
            'company': request.company,
            'company_ticker': request.company_ticker
        }
        result = crew_service.crew().kickoff(inputs=inputs)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))