import os
import requests
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class NewsSearchToolInput(BaseModel):
    """Input schema for the News Search Tool."""
    search_query: str = Field(..., description="The company name or topic to search for news about.")

class NewsSearchTool(BaseTool):
    name: str = "Financial News Search Tool"
    description: str = "Searches for recent news articles about a specific company or financial topic."
    args_schema: Type[BaseModel] = NewsSearchToolInput

    def _run(self, search_query: str) -> str:
        """The tool's main execution logic."""
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return "Error: NEWS_API_KEY environment variable not set."

        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': search_query,
            'apiKey': api_key,
            'sortBy': 'publishedAt',
            'pageSize': 5,
            'language': 'en'
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            
            if not articles:
                return f"No recent news found for '{search_query}'."

            formatted_articles = []
            for article in articles:
                formatted_articles.append(
                    f"Title: {article['title']}\n"
                    f"Source: {article['source']['name']}\n"
                    f"Snippet: {article.get('description', 'N/A')}\n"
                    "-----------------"
                )
            return "\n\n".join(formatted_articles)

        except requests.exceptions.RequestException as e:
            return f"Error fetching news: {e}"