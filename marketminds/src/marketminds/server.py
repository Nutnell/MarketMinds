from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from langserve import add_routes
from dotenv import load_dotenv

from . import auth, schemas

from .chain import NewsAnalysisChain, FinancialAnalysisChain, KnowledgeSearchChain
from .tools.custom_tool import NewsSearchTool

load_dotenv()
app = FastAPI(
    title="MarketMinds AI API (v2.1 - Composable)",
    description="A flexible API with distinct endpoints for each AI agent.",
    version="2.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

add_routes(app, NewsAnalysisChain, path="/api/v1/agents/news")
add_routes(app, FinancialAnalysisChain, path="/api/v1/agents/financials")
add_routes(app, KnowledgeSearchChain, path="/api/v1/agents/research")


@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to MarketMinds v2.1. Go to /docs to see the new agent-specific endpoints."
    }
