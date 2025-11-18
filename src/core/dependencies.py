from functools import lru_cache
from src.core.config import Settings, settings
from src.services.embeddings_service import EmbeddingsService
from src.services.vector_db_service import VectorDBService
from src.services.mongo_service import MongoService
from src.services.recommendation_service import RecommendationService
from src.services.moderation_service import ModerationService  # Real ML-based moderation
# from src.services.moderation_service_simple import ModerationService  # Simple moderation for testing


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return settings


# Service instances (singleton pattern)
_embeddings_service = None
_vector_db_service = None
_mongo_service = None
_recommendation_service = None
_moderation_service = None


def get_embeddings_service() -> EmbeddingsService:
    """Get embeddings service instance"""
    global _embeddings_service
    if _embeddings_service is None:
        _embeddings_service = EmbeddingsService()
    return _embeddings_service


def get_vector_db_service() -> VectorDBService:
    """Get vector database service instance"""
    global _vector_db_service
    if _vector_db_service is None:
        _vector_db_service = VectorDBService()
    return _vector_db_service


def get_mongo_service() -> MongoService:
    """Get MongoDB service instance"""
    global _mongo_service
    if _mongo_service is None:
        _mongo_service = MongoService()
    return _mongo_service


def get_recommendation_service() -> RecommendationService:
    """Get recommendation service instance"""
    global _recommendation_service
    if _recommendation_service is None:
        embeddings = get_embeddings_service()
        vector_db = get_vector_db_service()
        mongo = get_mongo_service()
        _recommendation_service = RecommendationService(embeddings, vector_db, mongo)
    return _recommendation_service


def get_moderation_service() -> ModerationService:
    """Get moderation service instance"""
    global _moderation_service
    if _moderation_service is None:
        _moderation_service = ModerationService()
    return _moderation_service

