from typing import TypedDict, List, Annotated, Any, Optional
from langgraph.graph.message import add_messages
from app.models.schemas import ProductSearchRequest, ProductResult


class ProductSearchState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    search_request: Optional[ProductSearchRequest]
    raw_results: Optional[str]          # Raw Tavily search output text
    analyzed_products: List[dict]       # Products extracted by analyzer
    curated_products: List[ProductResult]  # Final filtered/ranked products
    iteration: int
    feedback: Optional[str]
