from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage
from app.core.config import settings
from app.agents.product_state import ProductSearchState
import os

os.environ["TAVILY_API_KEY"] = settings.TAVILY_API_KEY

# E-commerce domains to search directly
ECOMMERCE_DOMAINS = [
    "amazon.in",
    "amazon.com",
    "flipkart.com",
    "myntra.com",
    "croma.com",
    "jiomart.com",
    "snapdeal.com",
    "meesho.com",
    "ajio.com",
    "tatacliq.com",
]


def _get_ecommerce_search_tool():
    """Returns a Tavily search tool restricted to e-commerce domains."""
    return TavilySearchResults(
        max_results=8,
        include_domains=ECOMMERCE_DOMAINS,
    )


def researcher_node(state: ProductSearchState):
    """
    Searches e-commerce sites (Amazon, Flipkart, etc.) for products
    matching the user's description and budget.
    """
    request = state["search_request"]
    search_tool = _get_ecommerce_search_tool()

    category_str = f" {request.category}" if request.category else ""

    # Targeted search queries for actual product listings
    queries = [
        f"{request.query}{category_str} under {request.max_price} {request.currency}",
        f"buy {request.query}{category_str} price",
        f"{request.query}{category_str} best price online",
    ]

    all_results = []

    for query in queries:
        try:
            print(f"[Researcher] Tavily e-commerce search: {query}")
            results = search_tool.invoke(query)

            if isinstance(results, list):
                for r in results:
                    if isinstance(r, dict):
                        url = r.get("url", "")
                        title = r.get("title", "")
                        content = r.get("content", "")
                        if url and content:
                            all_results.append(
                                f"TITLE: {title}\n"
                                f"URL: {url}\n"
                                f"CONTENT: {content[:600]}"
                            )
                    else:
                        all_results.append(str(r)[:600])
            elif isinstance(results, str):
                all_results.append(results[:600])
        except Exception as e:
            print(f"[Researcher] Search error for '{query}': {e}")

    raw_text = "\n\n===RESULT===\n\n".join(all_results) if all_results else ""

    if not raw_text:
        return {
            "raw_results": "",
            "messages": [SystemMessage(content="Researcher: No results found from e-commerce sites.")],
            "iteration": state.get("iteration", 0) + 1,
        }

    print(f"[Researcher] Found {len(all_results)} raw results from e-commerce sites")
    return {
        "raw_results": raw_text,
        "messages": [SystemMessage(content=f"Researcher: Found {len(all_results)} results from e-commerce sites.")],
        "iteration": state.get("iteration", 0) + 1,
    }
