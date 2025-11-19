from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import recommendations, search, moderation, embeddings, admin
from src.models.schemas import HealthCheckResponse
from src.core.config import settings
from src.core.dependencies import get_vector_db_service

# Create FastAPI app
app = FastAPI(
    title="Postal AI Service",
    description="AI-powered recommendations, search, and moderation for Postal social media app",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendations.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(moderation.router, prefix="/api")
app.include_router(embeddings.router, prefix="/api")
app.include_router(admin.router, prefix="/api")  # Admin endpoints


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 50)
    print("Starting Postal AI Service...")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"MongoDB URI: {settings.MONGODB_URI}")
    print(f"Qdrant: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
    print("=" * 50)
    
    # Initialize vector database collections
    try:
        vector_db = get_vector_db_service()
        vector_db.create_collections()
        print("✓ Vector database collections initialized")
    except Exception as e:
        print(f"✗ Error initializing vector database: {e}")
    
    print("=" * 50)
    print("Postal AI Service is ready!")
    print("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down Postal AI Service...")


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "api": "running",
            "embeddings": "ready",
            "vector_db": "connected",
            "mongodb": "connected"
        }
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check vector database
        vector_db = get_vector_db_service()
        users_info = vector_db.get_collection_info("users")
        posts_info = vector_db.get_collection_info("posts")
        
        return {
            "status": "healthy",
            "version": "1.0.0",
            "services": {
                "api": "running",
                "embeddings": "ready",
                "vector_db": f"connected ({users_info['points_count']} users, {posts_info['points_count']} posts)",
                "mongodb": "connected"
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "version": "1.0.0",
            "services": {
                "api": "running",
                "embeddings": "ready",
                "vector_db": f"error: {str(e)}",
                "mongodb": "unknown"
            }
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

