from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from dotenv import load_dotenv

from . import auth, schemas
from .chain import (
    NewsAnalysisChain,
    FinancialAnalysisChain,
    KnowledgeSearchChain,
    NewsAndFinancialsChain,
    NewsAndResearchChain,
    FinancialsAndResearchChain,
    FullAnalysisChain,
    MasterChain,
    CryptoAnalysisChain,
    EconomicAnalysisChain,
    GlobalMarketChain,
    CryptoHistoricalChain,
    NewsAndCryptoChain,
    FinancialsAndCryptoChain,
)
from .tools.custom_tool import NewsSearchTool

load_dotenv()
app = FastAPI(
    title="MarketMinds AI API (v4.0 - Global Markets)",
    description="A comprehensive API with a master router and specific endpoints for all asset classes.",
    version="4.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mock_users_db = {
    "user@example.com": {
        "username": "user@example.com",
        "hashed_password": auth.get_password_hash("password123"),
    }
}


def get_user(db, username: str):
    if username in db:
        return schemas.UserInDB(**db[username])


@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(mock_users_db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


news_tool_for_automation = NewsSearchTool()


@app.get("/api/internal/get-news/{search_query}", tags=["Internal Automation"])
def get_news_for_automation(search_query: str):
    try:
        return {
            "news_summary": news_tool_for_automation._run(search_query=search_query)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- All Endpoints ---
add_routes(app, NewsAnalysisChain, path="/api/v1/agents/news")
add_routes(app, FinancialAnalysisChain, path="/api/v1/agents/financials")
add_routes(app, KnowledgeSearchChain, path="/api/v1/agents/research")
add_routes(app, CryptoAnalysisChain, path="/api/v1/agents/crypto")
add_routes(app, CryptoHistoricalChain, path="/api/v1/agents/crypto_chart")
add_routes(app, EconomicAnalysisChain, path="/api/v1/agents/economics")
add_routes(app, GlobalMarketChain, path="/api/v1/agents/markets")
add_routes(app, NewsAndFinancialsChain, path="/api/v1/agents/news_and_financials")
add_routes(app, NewsAndResearchChain, path="/api/v1/agents/news_and_research")
add_routes(
    app, FinancialsAndResearchChain, path="/api/v1/agents/financials_and_research"
)
add_routes(app, NewsAndCryptoChain, path="/api/v1/agents/news_and_crypto")
add_routes(app, FinancialsAndCryptoChain, path="/api/v1/agents/financials_and_crypto")
add_routes(app, FullAnalysisChain, path="/api/v1/agents/full_analysis")
add_routes(app, MasterChain, path="/api/v1/chat")


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to MarketMinds v4.0. Go to /docs to see all endpoints."}
