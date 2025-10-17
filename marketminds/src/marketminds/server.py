from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Annotated
from .crew import MarketmindsCrewService
from . import auth, schemas
from .tools.custom_tool import NewsSearchTool
news_tool_for_automation = NewsSearchTool()

mock_users_db = {
    "nutnell00@gmail.com": {
        "username": "nutnell00@gmail.com",
        "hashed_password": auth.get_password_hash("password123"),
    }
}


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserInDB(**user_dict)

app = FastAPI(
    title="MarketMinds AI API",
    description="An AI-powered API for financial research and analysis.",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    """A simplified dependency to check for a valid bearer token."""

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.User(username="testuser")

class CrewRequest(BaseModel):
    company: str
    company_ticker: str
    research_query: str

crew_service = MarketmindsCrewService()

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok"}

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = get_user(mock_users_db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/run-crew", tags=["Crew"])
async def run_crew(
    request: CrewRequest,
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    """
    Runs the multi-agent crew. **Requires authentication.**
    """
    try:
        inputs = {
            "company": request.company,
            "company_ticker": request.company_ticker,
            "research_query": request.research_query,
        }
        result = crew_service.crew().kickoff(inputs=inputs)
        return {"result": result, "user": current_user.username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/internal/get-news/{search_query}", tags=["Internal Automation"])
def get_news_for_automation(search_query: str):
    """
    An unsecured internal endpoint for n8n to fetch news.
    """
    try:
        result = news_tool_for_automation._run(search_query=search_query)
        return {"news_summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))        
