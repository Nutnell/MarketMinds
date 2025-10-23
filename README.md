# MarketMinds AI  
**An Intelligent, Multi-Agent Investment Research Co-Pilot**

[![Built with FastAPI](https://img.shields.io/badge/Built%20with-FastAPI-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Frontend-Next.js](https://img.shields.io/badge/Frontend-Next.js-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![Deployed on Vercel](https://img.shields.io/badge/Deployed%20on-Vercel-black?style=flat-square&logo=vercel)](https://vercel.com/)
[![Database-PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-316192?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Automation-n8n](https://img.shields.io/badge/Automation-n8n-EA4C89?style=flat-square&logo=n8n)](https://n8n.io/)

---

## Overview  
**MarketMinds AI** is a production-grade, full-stack application designed as an **AI-powered co-pilot for retail investors**.  
It solves the problem of **information overload** by providing a **single conversational interface** to a **multi-agent backend** capable of:

- Retrieving and analyzing real-time market data  
- Summarizing financial news  
- Performing technical and sentiment analysis  
- Synthesizing expert-level insights and investment briefings  

This system unites **LLM reasoning**, **retrieval-augmented knowledge**, and **workflow automation** for a truly intelligent investment experience.

---

## Table of Contents  
1. [Key Features](#key-features)  
2. [Tech Stack & Architecture](#tech-stack--architecture)  
3. [Backend Intelligence](#backend-intelligence)  
4. [Automation with n8n](#automation-with-n8n)  
5. [API Documentation](#api-documentation)  
6. [Local Setup](#local-setup)  
7. [Deployment](#deployment)  
8. [Future Roadmap](#future-roadmap)

---

## Key Features  

### Conversational Interface  
Ask multi-layered questions naturally:  
> “Give me the news and financials for NVIDIA and explain growth investing.”

### Multi-Agent System  
A coordinated crew of specialized AI agents:  
- **Stock Analyst Agent** - Evaluates company fundamentals using a prioritized fallback strategy across Polygon, Yahoo Finance, and Alpha Vantage tools.  
- **News & Sentiment Agent** - Summarizes recent news and market sentiment using real-time search tools.  
- **Research Analyst Agent** - Explains investment philosophies by querying an internal knowledge base, with fallback to general expertise.
- **Crypto Analyst Agent** - Provides token profiles, price data, and historical charts using CoinGecko, CoinCap, and charting tools. 
- **Economic Indicator Agent** - Reports macroeconomic signals using FRED (US) and World Bank (global) datasets.
- **Global Markets Agent** - Delivers Forex and commodity prices using Twelve Data, FMP, and Alpha Vantage.
- **Market Reasoning Agent** - Synthesizes insights from other agents to answer high-level “why” and “what if” market questions.

### Resilient Data Retrieval  
If one API fails, others (e.g., Polygon, yfinance, Alpha Vantage) automatically take over — ensuring uninterrupted results.

### RAG Knowledge Engine  
Answers concept-level queries using a **ChromaDB vector store**, trained on curated investment literature.

### Hierarchical Reasoning Crew  
Complex questions activate a **Manager Agent**, which dynamically orchestrates other agents and synthesizes a coherent, expert-level conclusion.

### Automated User Engagement  
Via **n8n webhooks**, users automatically receive personalized onboarding reports and periodic AI market updates.

---

## Tech Stack & Architecture  

| Layer | Technology |
|-------|-------------|
| **Backend** | FastAPI, LangServe, CrewAI, LangChain, SQLAlchemy |
| **Frontend** | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui |
| **AI Models** | OpenAI `gpt-4o-mini` |
| **Database** | PostgreSQL |
| **Vector Store** | ChromaDB |
| **Deployment** | Docker, Render (Backend & DB), Vercel (Frontend) |
| **Automation** | n8n |

### Architecture Overview  
The Next.js frontend interacts with the FastAPI backend through a secure REST API.  
The backend orchestrates:

- AI chains and multi-agent crews  
- SQLAlchemy ORM with PostgreSQL  
- ChromaDB for contextual retrieval  
- External APIs for market data and sentiment  

This decoupled, modular design enables high scalability and resilience.

---

## Backend Intelligence  

### Master Router Chain  
Every request to `/api/v1/chat/invoke` is analyzed by a **Router Chain**, which classifies user intent (e.g. `news_analysis`, `reasoning_query`).

### Specialized Branches  
- **Single-Agent Runnable:** Handles focused queries like *“Current gold price?”*  
- **Multi-Agent Runnable:** Merges data from multiple agents (e.g. *Apple news + financials*)  
- **Hierarchical Crew Runnable:** Manages complex analytical workflows (*“Impact of inflation on growth stocks”*)  

This architecture ensures optimal routing between reasoning, retrieval, and synthesis tasks.

---

## Automation with n8n  

MarketMinds integrates seamlessly with **n8n** to demonstrate proactive AI engagement.

| Stage | Action |
|--------|---------|
| **Trigger** | New user signs up via `/signup` |
| **Webhook** | Backend sends data to n8n workflow |
| **Generate** | After 5 minutes, n8n calls `/api/v1/agents/news_and_financials` to generate a sample report (e.g. for AAPL) |
| **Engage** | Personalized welcome email sent to the user containing the full AI-generated report |

> This automation highlights the platform’s ability to autonomously engage and educate users.

---

## API Documentation 

### Main Endpoint  
`POST /chat/invoke`  
- **Description:** Accepts natural language investment queries  
- **Auth:** JWT required  
- **Example:**

```json
{
  "query": "Summarize Tesla’s latest earnings and news sentiment."
}
```

 Example Direct Agent Endpoint
POST /agents/financials/invoke

Description: Fetches stock data directly via FinancialsAgent

```json
{
  "ticker": "AAPL"
}
```

 Full API documentation available at /docs.

## Local Setup
Prerequisites
Python 3.11+

Node.js & npm

Docker Desktop

 Backend Setup
```bash
### Clone the repository
git clone <repo_url>
cd marketminds
```

### Configure environment
cp .env.example .env
### Add your API keys, JWT_SECRET_KEY, DATABASE_URL

### Install dependencies
pip install -r requirements.txt

### Start backend
uvicorn app.main:app --reload
Backend runs on → http://localhost:8000

### Frontend Setup
```bash
cd frontend
cp .env.local.example .env.local
# Set: NEXT_PUBLIC_API_URL=http://localhost:8000

npm install
npm run dev
```

Frontend runs on → http://localhost:3000

## Deployment
Component	Platform	Notes
Backend	Render	Dockerized FastAPI app
Database	Render	Managed PostgreSQL instance
Frontend	Vercel	Deployed with env vars for backend connection
Automation	n8n Cloud / Self-hosted	Handles user onboarding and AI triggers

CI/CD: Enabled via GitHub Actions — auto-deploys on push to main.

## Future Roadmap
 Daily AI Briefings: Automated scheduled reports for user watchlists

 Advanced Technical Indicators: RSI, Bollinger Bands, Fibonacci via pandas-ta

 Persistent Watchlists: Database-backed portfolios with real-time sync

 OAuth Login: Secure Google and GitHub sign-in support

© 2025 MarketMinds AI — Building smarter markets with intelligent automation.

---













