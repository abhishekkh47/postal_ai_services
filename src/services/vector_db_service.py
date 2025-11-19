from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
from src.core.config import settings
import uuid
import os


class VectorDBService:
    """Service for Qdrant vector database operations"""
    
    # Collection names
    USERS_COLLECTION = "users"
    POSTS_COLLECTION = "posts"
    
    def __init__(self):
        """Initialize Qdrant client"""
        # Check if using Qdrant Cloud (has API key)
        qdrant_api_key = os.getenv('QDRANT_API_KEY') or settings.QDRANT_API_KEY
        
        if qdrant_api_key:
            # Qdrant Cloud connection (uses HTTPS, no port)
            qdrant_url = f"https://{settings.QDRANT_HOST}"
            print(f"Connecting to Qdrant Cloud at {qdrant_url}")
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )
        else:
            # Local Qdrant connection (uses host:port)
            print(f"Connecting to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
            self.client = QdrantClient(
                host=settings.QDRANT_HOST,
                port=settings.QDRANT_PORT
            )
        
        print("Qdrant connected successfully")
    
    def create_collections(self):
        """Create collections for users and posts if they don't exist"""
        from qdrant_client.models import PayloadSchemaType
        
        collections = [self.USERS_COLLECTION, self.POSTS_COLLECTION]
        
        for collection_name in collections:
            try:
                # Check if collection exists
                self.client.get_collection(collection_name)
                print(f"Collection '{collection_name}' already exists")
            except Exception:
                # Create collection
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=settings.EMBEDDING_DIMENSION,
                        distance=Distance.COSINE
                    )
                )
                print(f"Collection '{collection_name}' created successfully")
            
            # Create payload indexes for filtering
            try:
                if collection_name == self.USERS_COLLECTION:
                    self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name="user_id",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    print(f"Created index on 'user_id' for {collection_name}")
                elif collection_name == self.POSTS_COLLECTION:
                    self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name="post_id",
                        field_schema=PayloadSchemaType.KEYWORD
                    )
                    print(f"Created index on 'post_id' for {collection_name}")
            except Exception as e:
                print(f"Index might already exist or error creating: {e}")
    
    def upsert_user_embedding(self, user_id: str, embedding: List[float], metadata: Optional[Dict] = None):
        """
        Insert or update user embedding
        
        Args:
            user_id: User ID
            embedding: Embedding vector
            metadata: Additional metadata to store
        """
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "user_id": user_id,
                **(metadata or {})
            }
        )
        
        self.client.upsert(
            collection_name=self.USERS_COLLECTION,
            points=[point]
        )
    
    def upsert_post_embedding(self, post_id: str, embedding: List[float], metadata: Optional[Dict] = None):
        """
        Insert or update post embedding
        
        Args:
            post_id: Post ID
            embedding: Embedding vector
            metadata: Additional metadata to store
        """
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "post_id": post_id,
                **(metadata or {})
            }
        )
        
        self.client.upsert(
            collection_name=self.POSTS_COLLECTION,
            points=[point]
        )
    
    def search_similar_users(
        self, 
        embedding: List[float], 
        limit: int = 10,
        exclude_user_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar users based on embedding
        
        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            exclude_user_ids: List of user IDs to exclude from results
            
        Returns:
            List of similar users with scores
        """
        # Build filter if needed
        search_filter = None
        if exclude_user_ids:
            search_filter = Filter(
                must_not=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=uid)
                    ) for uid in exclude_user_ids
                ]
            )
        
        results = self.client.search(
            collection_name=self.USERS_COLLECTION,
            query_vector=embedding,
            limit=limit,
            query_filter=search_filter
        )
        
        return [
            {
                "user_id": result.payload.get("user_id"),
                "score": result.score,
                "metadata": result.payload
            }
            for result in results
        ]
    
    def search_similar_posts(
        self, 
        embedding: List[float], 
        limit: int = 20,
        exclude_post_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar posts based on embedding
        
        Args:
            embedding: Query embedding vector
            limit: Maximum number of results
            exclude_post_ids: List of post IDs to exclude from results
            
        Returns:
            List of similar posts with scores
        """
        # Build filter if needed
        search_filter = None
        if exclude_post_ids:
            search_filter = Filter(
                must_not=[
                    FieldCondition(
                        key="post_id",
                        match=MatchValue(value=pid)
                    ) for pid in exclude_post_ids
                ]
            )
        
        results = self.client.search(
            collection_name=self.POSTS_COLLECTION,
            query_vector=embedding,
            limit=limit,
            query_filter=search_filter
        )
        
        return [
            {
                "post_id": result.payload.get("post_id"),
                "score": result.score,
                "metadata": result.payload
            }
            for result in results
        ]
    
    def delete_user_embedding(self, user_id: str):
        """Delete user embedding by user ID"""
        self.client.delete(
            collection_name=self.USERS_COLLECTION,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "user_id",
                            "match": {"value": user_id}
                        }
                    ]
                }
            }
        )
    
    def delete_post_embedding(self, post_id: str):
        """Delete post embedding by post ID"""
        self.client.delete(
            collection_name=self.POSTS_COLLECTION,
            points_selector={
                "filter": {
                    "must": [
                        {
                            "key": "post_id",
                            "match": {"value": post_id}
                        }
                    ]
                }
            }
        )
    
    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get information about a collection"""
        try:
            # Use the count API which is more reliable
            from qdrant_client.models import CountRequest
            
            count_result = self.client.count(
                collection_name=collection_name,
                exact=True
            )
            
            return {
                "name": collection_name,
                "points_count": count_result.count,
                "status": "ready"
            }
        except Exception as e:
            import traceback
            print(f"Error getting collection info: {traceback.format_exc()}")
            return {
                "name": collection_name,
                "error": str(e),
                "status": "error"
            }

