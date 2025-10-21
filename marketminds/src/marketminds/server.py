import os
import requests
from fastapi import FastAPI, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated, Dict
from sqlalchemy.orm import Session
from langserve import add_routes
from dotenv import load_dotenv

from . import auth, schemas
from .chain import (
    NewsAnalysisChain, FinancialAnalysisChain, KnowledgeSearchChain,
    CryptoAnalysisChain, EconomicAnalysisChain, GlobalMarketChain, CryptoHistoricalChain,
    NewsAndFinancialsChain, NewsAndResearchChain, FinancialsAndResearchChain,
    NewsAndCryptoChain, FinancialsAndCryptoChain, FullAnalysisChain, MasterChain,
    SimpleInput
)
from .database import get_db
from .tools.custom_tool import NewsSearchTool

load_dotenv()
app = FastAPI(
    title="MarketMinds AI API (v4.0 - Final)",
    description="A comprehensive API with a master router and specific agent endpoints, backed by a persistent database.",
    version="4.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "https://marketminds-omega.vercel.app"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def trigger_onboarding_webhook(user_data: dict):
    webhook_url = os.getenv("N8N_ONBOARDING_WEBHOOK_URL")
    if webhook_url:
        try:
            payload = {"email": user_data.get("email")}
            requests.post(webhook_url, json=payload)
            print(f"INFO: Triggered onboarding webhook for {user_data.get('email')}")
        except Exception as e:
            print(f"ERROR: Failed to trigger n8n onboarding webhook. Error: {e}")

security = HTTPBearer()
async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Session = Depends(get_db)):
    """Decodes the JWT token and fetches the user from the PostgreSQL database."""
    token = credentials.credentials
    username = auth.decode_access_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    user = auth.get_user(db, username=username) # This now calls the database function
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user

def get_session_info(user: Annotated[schemas.User, Depends(get_current_user)]) -> Dict:
    return {"configurable": {"session_id": user.username}}

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to MarketMinds v4.0. Go to /docs to see all endpoints."}

@app.post("/signup", response_model=schemas.User, tags=["Authentication"])
async def signup(user_in: schemas.UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, username=user_in.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    auth.create_user(db=db, user=user_in)
    background_tasks.add_task(trigger_onboarding_webhook, {"email": user_in.email})
    return schemas.User(username=user_in.email)

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.get_user(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

news_tool_for_automation = NewsSearchTool()
@app.get("/api/internal/get-news/{search_query}", tags=["Internal Automation"])
def get_news_for_automation(search_query: str):
    try:
        return {"news_summary": news_tool_for_automation._run(search_query=search_query)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

add_routes(app, NewsAnalysisChain, path="/api/v1/agents/news")
add_routes(app, FinancialAnalysisChain, path="/api/v1/agents/financials")
add_routes(app, KnowledgeSearchChain, path="/api/v1/agents/research")
add_routes(app, CryptoAnalysisChain, path="/api/v1/agents/crypto")
add_routes(app, CryptoHistoricalChain, path="/api/v1/agents/crypto_chart")
add_routes(app, EconomicAnalysisChain, path="/api/v1/agents/economics")
add_routes(app, GlobalMarketChain, path="/api/v1/agents/markets")
add_routes(app, NewsAndFinancialsChain, path="/api/v1/agents/news_and_financials")
add_routes(app, NewsAndResearchChain, path="/api/v1/agents/news_and_research")
add_routes(app, FinancialsAndResearchChain, path="/api/v1/agents/financials_and_research")
add_routes(app, NewsAndCryptoChain, path="/api/v1/agents/news_and_crypto")
add_routes(app, FinancialsAndCryptoChain, path="/api/v1/agents/financials_and_crypto")
add_routes(app, FullAnalysisChain, path="/api/v1/agents/full_analysis")

@app.post("/api/v1/chat", tags=["Master Conversational AI"])
async def chat(
    request: SimpleInput,
    current_user: Annotated[schemas.User, Depends(get_current_user)]
):
    try:
        config = {"configurable": {"session_id": current_user.username}}
        response = await MasterChain.ainvoke({"input": request.input}, config=config)
        return response
    except Exception as e:
        print(f"An error occurred in the chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))