from fastapi import APIRouter, HTTPException, Query

from app.schemas import SearchResponse
from app.services.data_service import search_all

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResponse)
def search(q: str = Query(min_length=1, max_length=80)) -> SearchResponse:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Search query must not be empty")

    results = search_all(query)
    return SearchResponse(query=query, total=len(results), results=results)
