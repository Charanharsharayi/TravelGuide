from langchain_community.tools.tavily_search import TavilySearchResults
from app.core.config import settings
import os

# Ensure API key is set for the tool to work
os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY

def get_search_tool():
    """
    Returns the Tavily search tool instance.
    """
    return TavilySearchResults(max_results=5)
