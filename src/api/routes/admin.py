from fastapi import APIRouter, HTTPException, Header
from typing import Optional
import os

router = APIRouter(prefix="/admin", tags=["admin"])

# Set this as environment variable in production
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "change-this-in-production")


@router.post("/initialize-embeddings")
async def initialize_embeddings(
    authorization: Optional[str] = Header(None)
):
    """
    One-time initialization: Generate embeddings for all existing users and posts
    Requires admin authorization
    """
    # Check authorization
    if not authorization or authorization != f"Bearer {ADMIN_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        from src.core.dependencies import (
            get_embeddings_service,
            get_vector_db_service,
            get_mongo_service
        )
        
        embeddings_service = get_embeddings_service()
        vector_db = get_vector_db_service()
        mongo = get_mongo_service()
        
        # Create collections (ignore if already exist)
        try:
            vector_db.create_collections()
        except Exception as e:
            print(f"Collections might already exist: {e}")
            # Continue anyway - collections exist is fine
        
        # Process users
        users = mongo.get_all_users()
        user_count = 0
        
        for user in users:
            try:
                user_id = str(user['_id'])
                embedding = embeddings_service.generate_user_embedding(user)
                metadata = {
                    'firstName': user.get('firstName', ''),
                    'lastName': user.get('lastName', ''),
                    'bio': user.get('bio', ''),
                }
                vector_db.upsert_user_embedding(user_id, embedding, metadata)
                user_count += 1
            except Exception as e:
                print(f"Error processing user {user.get('_id')}: {e}")
        
        # Process posts
        posts = mongo.get_all_posts()
        post_count = 0
        
        for post in posts:
            try:
                post_id = str(post['_id'])
                embedding = embeddings_service.generate_post_embedding(post)
                metadata = {
                    'userId': str(post.get('userId', '')),
                    'type': post.get('type', 0),
                    'reactions': post.get('reactions', 0),
                    'comments': post.get('comments', 0),
                }
                vector_db.upsert_post_embedding(post_id, embedding, metadata)
                post_count += 1
            except Exception as e:
                print(f"Error processing post {post.get('_id')}: {e}")
        
        return {
            "success": True,
            "users_processed": user_count,
            "posts_processed": post_count,
            "message": "Embeddings initialized successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing embeddings: {str(e)}")


@router.get("/status")
async def admin_status(
    authorization: Optional[str] = Header(None)
):
    """
    Get system status
    Requires admin authorization
    """
    if not authorization or authorization != f"Bearer {ADMIN_SECRET}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        from src.core.dependencies import get_vector_db_service
        
        vector_db = get_vector_db_service()
        users_info = vector_db.get_collection_info("users")
        posts_info = vector_db.get_collection_info("posts")
        
        return {
            "users_in_vector_db": users_info.get('points_count', 0),
            "posts_in_vector_db": posts_info.get('points_count', 0),
            "status": "healthy"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

