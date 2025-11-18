from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.services.embeddings_service import EmbeddingsService
from src.services.vector_db_service import VectorDBService
from src.services.mongo_service import MongoService
from src.core.dependencies import get_embeddings_service, get_vector_db_service, get_mongo_service

router = APIRouter(prefix="/embeddings", tags=["embeddings"])


class UserEmbeddingRequest(BaseModel):
    user_id: str


class PostEmbeddingRequest(BaseModel):
    post_id: str


@router.post("/user")
async def generate_user_embedding(
    request: UserEmbeddingRequest,
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
    vector_db: VectorDBService = Depends(get_vector_db_service),
    mongo: MongoService = Depends(get_mongo_service)
):
    """
    Generate and store embedding for a single user
    Called when a new user registers
    """
    try:
        # Get user from MongoDB
        user = mongo.get_user_by_id(request.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate embedding
        embedding = embeddings_service.generate_user_embedding(user)
        
        # Store in vector database
        metadata = {
            'firstName': user.get('firstName', ''),
            'lastName': user.get('lastName', ''),
            'bio': user.get('bio', ''),
        }
        vector_db.upsert_user_embedding(request.user_id, embedding, metadata)
        
        return {
            "success": True,
            "message": f"Embedding generated for user {request.user_id}",
            "dimension": len(embedding)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")


@router.post("/post")
async def generate_post_embedding(
    request: PostEmbeddingRequest,
    embeddings_service: EmbeddingsService = Depends(get_embeddings_service),
    vector_db: VectorDBService = Depends(get_vector_db_service),
    mongo: MongoService = Depends(get_mongo_service)
):
    """
    Generate and store embedding for a single post
    Called when a new post is created
    """
    try:
        # Get post from MongoDB
        post = mongo.get_post_by_id(request.post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Generate embedding
        embedding = embeddings_service.generate_post_embedding(post)
        
        # Store in vector database
        metadata = {
            'userId': str(post.get('userId', '')),
            'type': post.get('type', 0),
            'reactions': post.get('reactions', 0),
            'comments': post.get('comments', 0),
        }
        vector_db.upsert_post_embedding(request.post_id, embedding, metadata)
        
        return {
            "success": True,
            "message": f"Embedding generated for post {request.post_id}",
            "dimension": len(embedding)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

