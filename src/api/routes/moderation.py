from fastapi import APIRouter, Depends, HTTPException
from src.models.schemas import ModerationRequest, ModerationResponse
from src.services.moderation_service import ModerationService
from src.core.dependencies import get_moderation_service

router = APIRouter(prefix="/moderation", tags=["moderation"])


@router.post("/check", response_model=ModerationResponse)
async def moderate_content(
    request: ModerationRequest,
    moderation_service: ModerationService = Depends(get_moderation_service)
):
    """
    Check content for toxicity and spam
    """
    try:
        results = moderation_service.moderate_content(
            text=request.text,
            check_toxicity=request.check_toxicity,
            check_spam=request.check_spam
        )
        
        return ModerationResponse(
            is_safe=results['is_safe'],
            toxicity_score=results['toxicity_score'],
            spam_score=results['spam_score'],
            categories=results['categories'],
            flagged_reasons=results['flagged_reasons']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error moderating content: {str(e)}")

