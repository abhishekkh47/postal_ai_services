# Postal AI Service

AI-powered recommendations, semantic search, and content moderation for the Postal social media application.

## Features

- **User Recommendations**: Suggest users based on profile similarity
- **Post Recommendations**: Personalized feed using content-based and collaborative filtering
- **Semantic Search**: Search posts and users by meaning, not just keywords
- **Content Moderation**: Toxicity and spam detection for posts and comments

## Tech Stack

- **FastAPI**: Python web framework
- **Qdrant**: Vector database for similarity search
- **Sentence Transformers**: Generate text embeddings
- **Detoxify**: Toxicity detection
- **MongoDB**: Data source (shared with main app)

## Setup

### 1. Prerequisites

- Docker Desktop installed
- Python 3.11+
- MongoDB running (from main Postal app)

### 2. Environment Setup

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and update MongoDB URI:

```env
MONGODB_URI=mongodb://localhost:27017/postal
```

### 3. Start Services

```bash
# Start Qdrant and AI service
docker-compose up -d

# Check logs
docker-compose logs -f ai_service
```

The AI service will be available at `http://localhost:8000`

### 4. Initialize Vector Database

```bash
# Enter the AI service container
docker-compose exec ai_service bash

# Run setup script
python scripts/setup_vector_db.py
```

### 5. Generate Initial Embeddings

```bash
# Still inside the container
python scripts/generate_initial_embeddings.py
```

This will:
- Fetch all users and posts from MongoDB
- Generate embeddings
- Store them in Qdrant

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Detailed health check

### Recommendations
- `POST /api/recommendations/users` - Get user recommendations
- `POST /api/recommendations/posts` - Get post recommendations
- `POST /api/recommendations/posts/collaborative` - Collaborative filtering

### Search
- `POST /api/search/posts` - Semantic post search
- `POST /api/search/users` - Semantic user search

### Moderation
- `POST /api/moderation/check` - Check content for toxicity/spam

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Run without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Start Qdrant separately
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Run the service
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test user recommendations
curl -X POST http://localhost:8000/api/recommendations/users \
  -H "Content-Type: application/json" \
  -d '{"user_id": "YOUR_USER_ID", "limit": 10}'
```

## Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Qdrant│  │MongoDB│
│Vector│  │ Data  │
│  DB  │  │Source │
└──────┘  └───────┘
```

## Troubleshooting

### Qdrant connection error
- Ensure Docker containers are running: `docker-compose ps`
- Check Qdrant logs: `docker-compose logs qdrant`

### MongoDB connection error
- Verify MongoDB URI in `.env`
- Ensure MongoDB is accessible from Docker container

### Model download issues
- First run downloads ML models (~500MB)
- Ensure stable internet connection
- Models are cached in `.cache/` directory

## Next Steps

1. Integrate with Node.js backend
2. Update frontend to use AI features
3. Monitor performance and tune parameters
4. Add caching for frequently requested recommendations
