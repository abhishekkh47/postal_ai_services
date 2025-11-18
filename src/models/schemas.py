from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ==================== User Models ====================
class UserRecommendationRequest(BaseModel):
    """Request model for user recommendations"""
    user_id: str = Field(..., description="ID of the user requesting recommendations")
    limit: int = Field(default=10, ge=1, le=50, description="Number of recommendations to return")
    exclude_following: bool = Field(default=True, description="Exclude users already being followed")


class UserRecommendationResponse(BaseModel):
    """Response model for user recommendations"""
    user_ids: List[str] = Field(..., description="List of recommended user IDs")
    scores: List[float] = Field(..., description="Similarity scores for each recommendation")
    total: int = Field(..., description="Total number of recommendations")


# ==================== Post Models ====================
class PostRecommendationRequest(BaseModel):
    """Request model for post recommendations"""
    user_id: str = Field(..., description="ID of the user requesting recommendations")
    limit: int = Field(default=20, ge=1, le=100, description="Number of posts to return")
    page: int = Field(default=1, ge=1, description="Page number for pagination")


class PostRecommendationResponse(BaseModel):
    """Response model for post recommendations"""
    post_ids: List[str] = Field(..., description="List of recommended post IDs")
    scores: List[float] = Field(..., description="Relevance scores for each post")
    total: int = Field(..., description="Total number of recommendations")
    page: int = Field(..., description="Current page number")


# ==================== Search Models ====================
class SemanticSearchRequest(BaseModel):
    """Request model for semantic search"""
    query: str = Field(..., min_length=1, description="Search query text")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results to return")
    search_type: str = Field(default="posts", description="Type of search: 'posts' or 'users'")


class SemanticSearchResponse(BaseModel):
    """Response model for semantic search"""
    results: List[str] = Field(..., description="List of result IDs (post or user IDs)")
    scores: List[float] = Field(..., description="Relevance scores for each result")
    total: int = Field(..., description="Total number of results")


# ==================== Moderation Models ====================
class ModerationRequest(BaseModel):
    """Request model for content moderation"""
    text: str = Field(..., min_length=1, description="Text content to moderate")
    check_toxicity: bool = Field(default=True, description="Check for toxic content")
    check_spam: bool = Field(default=True, description="Check for spam")


class ModerationResponse(BaseModel):
    """Response model for content moderation"""
    is_safe: bool = Field(..., description="Whether the content is safe")
    toxicity_score: float = Field(..., description="Toxicity score (0-1, higher is more toxic)")
    spam_score: float = Field(..., description="Spam score (0-1, higher is more likely spam)")
    categories: Dict[str, float] = Field(default={}, description="Detailed toxicity categories")
    flagged_reasons: List[str] = Field(default=[], description="Reasons why content was flagged")


# ==================== Embedding Models ====================
class EmbeddingRequest(BaseModel):
    """Request model for generating embeddings"""
    text: str = Field(..., min_length=1, description="Text to generate embedding for")
    entity_type: str = Field(..., description="Type of entity: 'user' or 'post'")
    entity_id: str = Field(..., description="ID of the entity")


class EmbeddingResponse(BaseModel):
    """Response model for embeddings"""
    embedding: List[float] = Field(..., description="Generated embedding vector")
    dimension: int = Field(..., description="Dimension of the embedding")


# ==================== Health Check ====================
class HealthCheckResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    services: Dict[str, str] = Field(..., description="Status of dependent services")

