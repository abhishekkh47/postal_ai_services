from fastapi import APIRouter, Depends, HTTPException
from src.models.schemas import (
    UserRecommendationRequest,
    UserRecommendationResponse,
    PostRecommendationRequest,
    PostRecommendationResponse
)
from src.services.recommendation_service import RecommendationService
from src.core.dependencies import get_recommendation_service

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/users", response_model=UserRecommendationResponse)
async def get_user_recommendations(
    request: UserRecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get user recommendations based on profile similarity
    """
    try:
        user_ids, scores = recommendation_service.recommend_users(
            user_id=request.user_id,
            limit=request.limit,
            exclude_following=request.exclude_following
        )
        
        return UserRecommendationResponse(
            user_ids=user_ids,
            scores=scores,
            total=len(user_ids)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


@router.post("/posts", response_model=PostRecommendationResponse)
async def get_post_recommendations(
    request: PostRecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get post recommendations for user's feed
    """
    try:
        post_ids, scores = recommendation_service.recommend_posts(
            user_id=request.user_id,
            limit=request.limit
        )
        
        return PostRecommendationResponse(
            post_ids=post_ids,
            scores=scores,
            total=len(post_ids),
            page=request.page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating post recommendations: {str(e)}")


@router.post("/posts/collaborative", response_model=PostRecommendationResponse)
async def get_collaborative_post_recommendations(
    request: PostRecommendationRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Get post recommendations using collaborative filtering
    (Based on what similar users liked)
    """
    try:
        post_ids, scores = recommendation_service.recommend_posts_collaborative(
            user_id=request.user_id,
            limit=request.limit
        )
        
        return PostRecommendationResponse(
            post_ids=post_ids,
            scores=scores,
            total=len(post_ids),
            page=request.page
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating collaborative recommendations: {str(e)}")

