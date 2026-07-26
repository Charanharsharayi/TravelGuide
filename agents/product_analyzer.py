from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.agents.product_state import ProductSearchState
import json

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY
)


def analyzer_node(state: ProductSearchState):
    """
    Takes raw e-commerce search results and uses Gemini to extract
    structured product data (title, price, URL, source, snippet).
    Filters out non-product pages like category listings or blog posts.
    """
    raw_results = state.get("raw_results", "")
    request = state["search_request"]

    if not raw_results:
        return {
            "analyzed_products": [],
            "messages": [SystemMessage(content="Analyzer: No raw results to analyze.")],
        }

    prompt = f"""You are a product data extraction specialist.

The user is looking for: {request.query}
Budget: up to {request.max_price} {request.currency}
{f"Category: {request.category}" if request.category else ""}

Below are raw search results from e-commerce sites (Amazon, Flipkart, Myntra, etc.).
Your job is to extract REAL INDIVIDUAL PRODUCTS from these results.

--- RAW E-COMMERCE RESULTS ---
{raw_results}
--- END RESULTS ---

STRICT RULES:
1. Extract ONLY actual product listings — NOT category pages, search results pages, review articles, or blog posts.
2. Each product MUST have a direct product page URL (containing /dp/, /p/, /product/, or a specific product slug).
3. URLs must come from the raw results EXACTLY as they appear. NEVER invent or modify URLs.
4. Extract the price as shown in the search results. If no clear price is shown, write "Check price on site".
5. The "source" must be the real site name: "Amazon", "Flipkart", "Myntra", "Croma", "JioMart", etc.
6. Write a brief 1-2 sentence product description for the "snippet" field.
7. Skip duplicate products (same product from same source).

Output ONLY a valid JSON array:
[
  {{
    "title": "Exact Product Name",
    "price": "₹X,XXX",
    "url": "https://exact-url-from-results",
    "source": "Amazon",
    "snippet": "Brief product description"
  }}
]

If no valid individual products can be extracted, return: []
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]

        products = json.loads(content)

        if not isinstance(products, list):
            products = []

        print(f"[Analyzer] Extracted {len(products)} products from raw results")
        return {
            "analyzed_products": products,
            "messages": [SystemMessage(content=f"Analyzer: Extracted {len(products)} products.")],
        }
    except Exception as e:
        print(f"[Analyzer] Error: {e}")
        return {
            "analyzed_products": [],
            "messages": [SystemMessage(content=f"Analyzer: Error extracting products — {str(e)}")],
        }
