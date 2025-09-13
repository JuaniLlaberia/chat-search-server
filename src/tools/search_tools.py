import os
from langchain_tavily import TavilySearch

tavily_search = TavilySearch(
    max_results=15,
    search_depth="advanced",
    include_images=True,
    tavily_api_key=os.getenv("TAVILY_API_KEY", ""),
)