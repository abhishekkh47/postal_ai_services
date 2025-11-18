from pymongo import MongoClient
from typing import List, Dict, Optional, Any
from src.core.config import settings
from bson import ObjectId


class MongoService:
    """Service for MongoDB operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        print(f"Connecting to MongoDB: {settings.MONGODB_URI}")
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client.get_default_database()
        print("MongoDB connected successfully")
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User document or None
        """
        try:
            return self.db.users.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            print(f"Error fetching user {user_id}: {e}")
            return None
    
    def get_all_users(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all users
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of user documents
        """
        query = self.db.users.find()
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_users_by_ids(self, user_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple users by IDs
        
        Args:
            user_ids: List of user IDs
            
        Returns:
            List of user documents
        """
        try:
            object_ids = [ObjectId(uid) for uid in user_ids]
            return list(self.db.users.find({"_id": {"$in": object_ids}}))
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    def get_post_by_id(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        Get post by ID
        
        Args:
            post_id: Post ID
            
        Returns:
            Post document or None
        """
        try:
            return self.db.posts.find_one({"_id": ObjectId(post_id)})
        except Exception as e:
            print(f"Error fetching post {post_id}: {e}")
            return None
    
    def get_all_posts(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all posts
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            List of post documents
        """
        query = self.db.posts.find()
        if limit:
            query = query.limit(limit)
        return list(query)
    
    def get_posts_by_ids(self, post_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get multiple posts by IDs
        
        Args:
            post_ids: List of post IDs
            
        Returns:
            List of post documents
        """
        try:
            object_ids = [ObjectId(pid) for pid in post_ids]
            return list(self.db.posts.find({"_id": {"$in": object_ids}}))
        except Exception as e:
            print(f"Error fetching posts: {e}")
            return []
    
    def get_user_following(self, user_id: str) -> List[str]:
        """
        Get list of user IDs that a user is following
        
        Args:
            user_id: User ID
            
        Returns:
            List of user IDs being followed
        """
        try:
            # Assuming you have a 'friends' or 'follows' collection
            # Adjust based on your actual schema
            follows = self.db.friends.find({
                "senderId": ObjectId(user_id),
                "status": 2  # Assuming status 2 means accepted/following
            })
            return [str(f["receiverId"]) for f in follows]
        except Exception as e:
            print(f"Error fetching following list: {e}")
            return []
    
    def get_user_interactions(self, user_id: str) -> Dict[str, List[str]]:
        """
        Get user's interaction history (liked posts, commented posts)
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with 'liked_posts' and 'commented_posts'
        """
        try:
            # Get liked posts
            liked_posts = self.db.postreactions.find({
                "userId": ObjectId(user_id)
            })
            liked_post_ids = [str(p["postId"]) for p in liked_posts]
            
            # Get commented posts
            commented_posts = self.db.comments.find({
                "userId": ObjectId(user_id)
            })
            commented_post_ids = [str(c["postId"]) for c in commented_posts]
            
            return {
                "liked_posts": liked_post_ids,
                "commented_posts": commented_post_ids
            }
        except Exception as e:
            print(f"Error fetching user interactions: {e}")
            return {"liked_posts": [], "commented_posts": []}
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        print("MongoDB connection closed")

