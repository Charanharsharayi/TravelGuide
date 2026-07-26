from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ProductSearchRequest, ProductSearchResponse
from app.core.security import get_current_user
from app.agents.product_graph import product_graph

router = APIRouter()


@router.post("/search", response_model=ProductSearchResponse)
async def search_products(
    request: ProductSearchRequest, user: dict = Depends(get_current_user)
):
    """
    Multi-agent product search pipeline:
    Researcher (Tavily e-commerce search) → Analyzer (Gemini extraction)
    → Curator (budget filter & ranking) → Finalizer
    """
    try:
        initial_state = {
            "search_request": request,
            "messages": [],
            "raw_results": "",
            "analyzed_products": [],
            "curated_products": [],
            "iteration": 0,
            "feedback": None,
        }

        result = await product_graph.ainvoke(initial_state)

        curated = result.get("curated_products", [])

        if not curated:
            return ProductSearchResponse(
                query=request.query,
                results=[],
                message="No products found matching your criteria. Try a different search or higher budget.",
            )

        return ProductSearchResponse(
            query=request.query,
            results=curated,
            message=f"Found {len(curated)} product(s) from e-commerce sites within your budget.",
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in search_products: {e}")
        raise HTTPException(status_code=500, detail=str(e))
