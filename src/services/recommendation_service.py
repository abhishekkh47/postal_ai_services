from typing import List, Dict, Any, Tuple
from src.services.embeddings_service import EmbeddingsService
from src.services.vector_db_service import VectorDBService
from src.services.mongo_service import MongoService


class RecommendationService:
    """Service for generating recommendations"""
    
    def __init__(
        self,
        embeddings_service: EmbeddingsService,
        vector_db_service: VectorDBService,
        mongo_service: MongoService
    ):
        """Initialize recommendation service with dependencies"""
        self.embeddings = embeddings_service
        self.vector_db = vector_db_service
        self.mongo = mongo_service
    
    def recommend_users(
        self,
        user_id: str,
        limit: int = 10,
        exclude_following: bool = True
    ) -> Tuple[List[str], List[float]]:
        """
        Recommend users based on profile similarity
        
        Args:
            user_id: ID of the user requesting recommendations
            limit: Number of recommendations to return
            exclude_following: Whether to exclude users already being followed
            
        Returns:
            Tuple of (user_ids, scores)
        """
        # Get the requesting user's data
        user = self.mongo.get_user_by_id(user_id)
        if not user:
            print(f"User {user_id} not found")
            return [], []
        
        # Generate embedding for the user
        user_embedding = self.embeddings.generate_user_embedding(user)
        
        # Get list of users to exclude
        exclude_ids = [user_id]  # Always exclude self
        if exclude_following:
            following = self.mongo.get_user_following(user_id)
            exclude_ids.extend(following)
        
        # Search for similar users in vector DB
        similar_users = self.vector_db.search_similar_users(
            embedding=user_embedding,
            limit=limit * 2,  # Get more to account for filtering
            exclude_user_ids=exclude_ids
        )
        
        # Extract user IDs and scores
        user_ids = [u["user_id"] for u in similar_users[:limit]]
        scores = [u["score"] for u in similar_users[:limit]]
        
        return user_ids, scores
    
    def recommend_posts(
        self,
        user_id: str,
        limit: int = 20
    ) -> Tuple[List[str], List[float]]:
        """
        Recommend posts based on user's interests and interaction history
        
        Args:
            user_id: ID of the user requesting recommendations
            limit: Number of posts to return
            
        Returns:
            Tuple of (post_ids, scores)
        """
        # Get user data
        user = self.mongo.get_user_by_id(user_id)
        if not user:
            print(f"User {user_id} not found")
            return [], []
        
        # Get user's interaction history
        interactions = self.mongo.get_user_interactions(user_id)
        liked_posts = interactions.get("liked_posts", [])
        
        # Strategy 1: Content-based filtering using user profile
        user_embedding = self.embeddings.generate_user_embedding(user)
        
        # Search for posts similar to user's interests
        similar_posts = self.vector_db.search_similar_posts(
            embedding=user_embedding,
            limit=limit,
            exclude_post_ids=liked_posts  # Don't recommend already liked posts
        )
        
        # Extract post IDs and scores
        post_ids = [p["post_id"] for p in similar_posts]
        scores = [p["score"] for p in similar_posts]
        
        return post_ids, scores
    
    def recommend_posts_collaborative(
        self,
        user_id: str,
        limit: int = 20
    ) -> Tuple[List[str], List[float]]:
        """
        Recommend posts using collaborative filtering
        (Based on what similar users liked)
        
        Args:
            user_id: ID of the user requesting recommendations
            limit: Number of posts to return
            
        Returns:
            Tuple of (post_ids, scores)
        """
        # Get similar users
        similar_user_ids, user_scores = self.recommend_users(
            user_id=user_id,
            limit=10,
            exclude_following=False
        )
        
        if not similar_user_ids:
            return [], []
        
        # Get posts liked by similar users
        all_post_ids = []
        post_score_map = {}
        
        for similar_user_id, user_score in zip(similar_user_ids, user_scores):
            interactions = self.mongo.get_user_interactions(similar_user_id)
            liked_posts = interactions.get("liked_posts", [])
            
            # Weight posts by how similar the user is
            for post_id in liked_posts:
                if post_id not in post_score_map:
                    post_score_map[post_id] = 0
                post_score_map[post_id] += user_score
        
        # Sort posts by aggregated score
        sorted_posts = sorted(
            post_score_map.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        post_ids = [p[0] for p in sorted_posts]
        scores = [p[1] for p in sorted_posts]
        
        return post_ids, scores
    
    def search_posts_semantic(
        self,
        query: str,
        limit: int = 20
    ) -> Tuple[List[str], List[float]]:
        """
        Search posts using semantic similarity
        
        Args:
            query: Search query text
            limit: Number of results to return
            
        Returns:
            Tuple of (post_ids, scores)
        """
        # Generate embedding for the search query
        query_embedding = self.embeddings.generate_embedding(query)
        
        # Search for similar posts
        similar_posts = self.vector_db.search_similar_posts(
            embedding=query_embedding,
            limit=limit
        )
        
        # Extract post IDs and scores
        post_ids = [p["post_id"] for p in similar_posts]
        scores = [p["score"] for p in similar_posts]
        
        return post_ids, scores
    
    def search_users_semantic(
        self,
        query: str,
        limit: int = 10
    ) -> Tuple[List[str], List[float]]:
        """
        Search users using semantic similarity
        
        Args:
            query: Search query text
            limit: Number of results to return
            
        Returns:
            Tuple of (user_ids, scores)
        """
        # Generate embedding for the search query
        query_embedding = self.embeddings.generate_embedding(query)
        
        # Search for similar users
        similar_users = self.vector_db.search_similar_users(
            embedding=query_embedding,
            limit=limit
        )
        
        # Extract user IDs and scores
        user_ids = [u["user_id"] for u in similar_users]
        scores = [u["score"] for u in similar_users]
        
        return user_ids, scores

