# Postal AI Service - Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                           │
│                     (React Frontend)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    NODE.JS BACKEND                               │
│                  (Express + TypeScript)                          │
│                                                                  │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐         │
│  │   User      │  │    Post      │  │   Comment     │         │
│  │ Controller  │  │  Controller  │  │  Controller   │         │
│  └──────┬──────┘  └──────┬───────┘  └───────┬───────┘         │
│         │                │                   │                  │
│         └────────────────┴───────────────────┘                  │
│                          │                                      │
│                  ┌───────▼────────┐                             │
│                  │  AI Service    │                             │
│                  │    Client      │                             │
│                  └───────┬────────┘                             │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP/REST
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼──────┐  ┌────────▼─────────┐  ┌────▼──────┐
│   MongoDB    │  │   AI SERVICE     │  │  Qdrant   │
│              │  │   (FastAPI)      │  │ Vector DB │
│  - users     │◄─┤                  ├─►│           │
│  - posts     │  │  - Embeddings    │  │ - Users   │
│  - comments  │  │  - Recommendations│  │ - Posts   │
│  - reactions │  │  - Search        │  │           │
└──────────────┘  │  - Moderation    │  └───────────┘
                  └──────────────────┘
```

## Data Flow Examples

### 1. User Recommendations Flow

```
┌─────────┐
│  User   │ Visits Explore Page
└────┬────┘
     │
     ▼
┌─────────────────┐
│   Frontend      │ GET /api/users/explore?ai=true
└────┬────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   Node.js Backend                                   │
│                                                     │
│   1. Receive request                                │
│   2. Extract user ID from auth token                │
│   3. Call AI Service                                │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   AI Service (Python)                               │
│                                                     │
│   1. Fetch user profile from MongoDB                │
│      - firstName, lastName, bio                     │
│                                                     │
│   2. Generate embedding                             │
│      "John Doe fitness enthusiast" → [0.23, -0.45, │
│      0.67, ..., 0.12] (384 dimensions)             │
│                                                     │
│   3. Query Qdrant vector DB                         │
│      - Find users with similar embeddings           │
│      - Exclude already following                    │
│      - Return top 10 matches                        │
└────┬────────────────────────────────────────────────┘
     │
     │ Returns: {user_ids: [...], scores: [...]}
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   Node.js Backend                                   │
│                                                     │
│   4. Fetch full user details from MongoDB           │
│   5. Return to frontend                             │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────┐
│   Frontend      │ Display recommended users
└─────────────────┘
```

### 2. Content Moderation Flow

```
┌─────────┐
│  User   │ Creates post: "You are stupid!"
└────┬────┘
     │
     ▼
┌─────────────────┐
│   Frontend      │ POST /api/posts/create
└────┬────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   Node.js Backend                                   │
│                                                     │
│   1. Receive post content                           │
│   2. Call AI Service for moderation                 │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   AI Service (Python)                               │
│                                                     │
│   1. Run Detoxify model                             │
│      - Toxicity: 0.92 (HIGH!)                       │
│      - Insult: 0.88                                 │
│      - Threat: 0.15                                 │
│                                                     │
│   2. Check spam patterns                            │
│      - No spam detected                             │
│                                                     │
│   3. Evaluate safety                                │
│      - is_safe: false                               │
│      - flagged_reasons: ["high_toxicity", "insult"] │
└────┬────────────────────────────────────────────────┘
     │
     │ Returns: {is_safe: false, ...}
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   Node.js Backend                                   │
│                                                     │
│   3. Check if safe                                  │
│   4. Reject post with error message                 │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────┐
│   Frontend      │ Show error: "Your post contains
└─────────────────┘ inappropriate content"
```

### 3. AI-Powered Feed Flow

```
┌─────────┐
│  User   │ Opens Home page, clicks "For You"
└────┬────┘
     │
     ▼
┌─────────────────┐
│   Frontend      │ GET /api/posts/feed?type=recommended
└────┬────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   Node.js Backend                                   │
│                                                     │
│   1. Receive request with type=recommended          │
│   2. Call AI Service                                │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   AI Service (Python)                               │
│                                                     │
│   1. Get user's profile & interaction history       │
│      - Liked posts about: fitness, travel           │
│      - Follows users interested in: tech, cooking   │
│                                                     │
│   2. Generate user interest embedding               │
│      Combine profile + interaction patterns         │
│                                                     │
│   3. Query Qdrant for similar posts                 │
│      - Find posts matching user interests           │
│      - Exclude already liked posts                  │
│      - Rank by relevance score                      │
│                                                     │
│   4. Optional: Collaborative filtering              │
│      - Find similar users                           │
│      - Get posts they liked                         │
│      - Merge with content-based results             │
└────┬────────────────────────────────────────────────┘
     │
     │ Returns: {post_ids: [...], scores: [...]}
     │
     ▼
┌─────────────────────────────────────────────────────┐
│   Node.js Backend                                   │
│                                                     │
│   3. Fetch full post details from MongoDB           │
│   4. Return to frontend                             │
└────┬────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────┐
│   Frontend      │ Display personalized feed
└─────────────────┘
```

## Component Responsibilities

### Frontend (React)
- User interface
- API calls to Node.js backend
- Display recommendations
- Handle errors

### Node.js Backend
- Authentication & authorization
- Business logic
- Database operations (MongoDB)
- AI service client
- Fallback logic if AI fails

### AI Service (Python/FastAPI)
- Generate embeddings
- Vector similarity search
- Content moderation
- Recommendation algorithms
- No direct database writes

### Qdrant (Vector DB)
- Store embeddings
- Fast similarity search
- KNN (K-Nearest Neighbors)

### MongoDB
- User data
- Posts & comments
- Relationships
- Source of truth

## Embedding Generation

### What is an Embedding?

```
Text: "John Doe, fitness enthusiast who loves travel"
         ↓ (Sentence Transformer Model)
Embedding: [0.23, -0.45, 0.67, 0.12, ..., -0.34]
           (384 numbers representing meaning)
```

### Why Embeddings?

```
Traditional Search:
  Query: "fitness"
  Matches: Posts containing word "fitness"
  Misses: Posts about "gym", "workout", "exercise"

Semantic Search (with embeddings):
  Query: "fitness" → [0.45, -0.23, ...]
  Matches: All posts with similar meaning
  Finds: "gym", "workout", "exercise", "health"
```

### Similarity Calculation

```
User A embedding: [0.5, 0.3, 0.8]
User B embedding: [0.6, 0.2, 0.7]
User C embedding: [-0.3, 0.9, -0.5]

Cosine Similarity:
  A ↔ B: 0.95 (very similar!)
  A ↔ C: 0.12 (not similar)
  
Result: Recommend User B to User A
```

## Scalability Considerations

### Current Setup (Development)
- Single AI service instance
- Local Qdrant instance
- CPU-based inference
- Good for: 100-1000 users

### Production Setup (Future)
```
┌──────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴───┬───────┬───────┐
   │       │       │       │
┌──▼──┐ ┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│ AI  │ │ AI  │ │ AI  │ │ AI  │
│ Svc │ │ Svc │ │ Svc │ │ Svc │
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   │       │       │       │
   └───┬───┴───────┴───────┘
       │
┌──────▼──────────┐
│ Qdrant Cluster  │
│ (Distributed)   │
└─────────────────┘
```

Good for: 10,000+ users

## Security Considerations

### API Authentication
- All Node.js endpoints require JWT token
- AI service is internal (not exposed to internet)
- Frontend never calls AI service directly

### Data Privacy
- Embeddings don't contain original text
- Can't reverse-engineer user data from embeddings
- Vector DB stores only numerical representations

### Moderation
- Fails open (allows content if service down)
- Prevents false positives from blocking users
- Logs all moderation decisions

## Performance Metrics

### Typical Response Times
- Embedding generation: 50-100ms
- Vector search: 10-50ms
- Moderation check: 100-200ms
- Total AI operation: 200-400ms

### Resource Usage
- RAM: ~2-4GB (models + vectors)
- CPU: Moderate (no GPU needed)
- Disk: ~1GB (models + vector storage)

## Monitoring & Debugging

### Health Checks
```bash
# AI Service health
curl http://localhost:8000/health

# Response includes:
{
  "status": "healthy",
  "services": {
    "api": "running",
    "embeddings": "ready",
    "vector_db": "connected (150 users, 450 posts)",
    "mongodb": "connected"
  }
}
```

### Logs
```bash
# AI Service logs
docker-compose logs -f ai_service

# Node.js logs
npm run start  # Check console

# Frontend logs
Browser console (F12)
```

### Debugging Tips
1. Check AI service health first
2. Verify embeddings exist in vector DB
3. Test AI endpoints directly
4. Check Node.js logs for errors
5. Verify MongoDB connection

---

## Summary

This architecture provides:
- ✅ Scalable AI features
- ✅ Clean separation of concerns
- ✅ Graceful degradation
- ✅ Easy to maintain
- ✅ Production-ready

All using free, open-source tools! 🎉

