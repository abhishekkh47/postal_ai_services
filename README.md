---
title: Postal AI Service
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
app_port: 8000
---

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

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Detailed health check

### Recommendations
- `POST /api/recommendations/users` - Get user recommendations
- `POST /api/recommendations/posts` - Get post recommendations

### Search
- `POST /api/search/posts` - Semantic post search
- `POST /api/search/users` - Semantic user search

### Moderation
- `POST /api/moderation/check` - Check content for toxicity/spam

## Documentation

Visit `/docs` for interactive API documentation (Swagger UI).
