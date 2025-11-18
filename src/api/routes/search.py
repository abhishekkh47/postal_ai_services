from fastapi import APIRouter, Depends, HTTPException
from src.models.schemas import SemanticSearchRequest, SemanticSearchResponse
from src.services.recommendation_service import RecommendationService
from src.core.dependencies import get_recommendation_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/posts", response_model=SemanticSearchResponse)
async def semantic_search_posts(
    request: SemanticSearchRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Search posts using semantic similarity
    """
    try:
        post_ids, scores = recommendation_service.search_posts_semantic(
            query=request.query,
            limit=request.limit
        )
        
        return SemanticSearchResponse(
            results=post_ids,
            scores=scores,
            total=len(post_ids)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing semantic search: {str(e)}")


@router.post("/users", response_model=SemanticSearchResponse)
async def semantic_search_users(
    request: SemanticSearchRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Search users using semantic similarity
    """
    try:
        user_ids, scores = recommendation_service.search_users_semantic(
            query=request.query,
            limit=request.limit
        )
        
        return SemanticSearchResponse(
            results=user_ids,
            scores=scores,
            total=len(user_ids)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing semantic search: {str(e)}")

