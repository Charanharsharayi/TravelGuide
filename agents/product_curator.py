from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.agents.product_state import ProductSearchState
from app.models.schemas import ProductResult
import json

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY
)


def curator_node(state: ProductSearchState):
    """
    Filters products by budget, ranks by relevance and value,
    removes duplicates, and selects the top 8 results.
    """
    analyzed = state.get("analyzed_products", [])
    request = state["search_request"]

    if not analyzed:
        return {
            "curated_products": [],
            "feedback": "No products to curate.",
            "messages": [SystemMessage(content="Curator: No products to curate.")],
        }

    prompt = f"""You are a smart shopping assistant.

The user wants: {request.query}
Maximum budget: {request.max_price} {request.currency}
{f"Category: {request.category}" if request.category else ""}

Here are extracted products from e-commerce sites:
{json.dumps(analyzed, indent=2)}

YOUR TASK:
1. REMOVE products that are clearly above the budget of {request.max_price} {request.currency}.
   Parse prices like "₹2,499" or "$29.99" to compare with the budget.
   Products with "Check price on site" should be kept (give them lower priority).
2. REMOVE duplicate products (same product from different search queries).
3. RANK remaining products by:
   - Relevance to "{request.query}" (most relevant first)
   - Value for money (better products at lower prices rank higher)
4. Keep a MAXIMUM of {request.num_results} products.
5. Preserve the exact URL from the input — do NOT change URLs.

Output ONLY a JSON array of the curated products (same fields: title, price, url, source, snippet):
[
  {{
    "title": "...",
    "price": "...",
    "url": "...",
    "source": "...",
    "snippet": "..."
  }}
]

If no products pass the budget filter, return: []
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]

        curated_data = json.loads(content)

        curated_products = []
        for p in curated_data:
            try:
                curated_products.append(ProductResult(**p))
            except Exception:
                continue

        print(f"[Curator] Curated down to {len(curated_products)} products within budget")

        feedback = None if curated_products else "No products found within budget."

        return {
            "curated_products": curated_products,
            "feedback": feedback,
            "messages": [SystemMessage(content=f"Curator: {len(curated_products)} product(s) within budget.")],
        }
    except Exception as e:
        print(f"[Curator] Error: {e}")
        return {
            "curated_products": [],
            "feedback": f"Curation error: {str(e)}",
            "messages": [SystemMessage(content=f"Curator: Error — {str(e)}")],
        }
