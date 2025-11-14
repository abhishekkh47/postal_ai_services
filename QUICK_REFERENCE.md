# 🚀 Quick Reference - Postal AI Features

## Start Everything

```bash
# 1. Start AI Service
cd /Users/mind/Projects/Postal/postal_ai_services
docker-compose up -d

# 2. Initialize (first time only)
docker-compose exec ai_service python scripts/setup_vector_db.py
docker-compose exec ai_service python scripts/generate_initial_embeddings.py

# 3. Start Node.js Backend (in another terminal)
cd /Users/mind/Projects/Postal/Post_App
npm run start

# 4. Start Frontend (in another terminal)
cd /Users/mind/Projects/Postal/post_app_fe
npm run dev
```

## Check Status

```bash
# AI Service health
curl http://localhost:8000/health

# Check Docker containers
docker-compose ps

# View logs
docker-compose logs -f ai_service
```

## API Endpoints

### Backend (Node.js)

```bash
# User recommendations (AI-powered)
GET /api/users/explore?ai=true

# Post feed (AI-powered)
GET /api/posts/feed?type=recommended

# Post feed (chronological)
GET /api/posts/feed?type=latest

# Create post (with moderation)
POST /api/posts/create

# Create comment (with moderation)
POST /api/comments/create
```

### AI Service (Python)

```bash
# User recommendations
POST http://localhost:8000/api/recommendations/users
{
  "user_id": "USER_ID",
  "limit": 10
}

# Post recommendations
POST http://localhost:8000/api/recommendations/posts
{
  "user_id": "USER_ID",
  "limit": 20
}

# Semantic search
POST http://localhost:8000/api/search/posts
{
  "query": "fitness tips",
  "limit": 20
}

# Content moderation
POST http://localhost:8000/api/moderation/check
{
  "text": "Your text here",
  "check_toxicity": true,
  "check_spam": true
}
```

## Frontend Changes Needed

### 1. Explore Page
File: `post_app_fe/src/pages/Explore.tsx` or `post_app_fe/src/hooks/useFriends.ts`

```typescript
// Change API call from:
const response = await axios.get('/api/users/explore');

// To:
const response = await axios.get('/api/users/explore?ai=true');
```

### 2. Home Feed
File: `post_app_fe/src/pages/Home.tsx`

```typescript
const [feedType, setFeedType] = useState('latest');

// Add toggle buttons
<div className="flex gap-2 mb-4">
  <button 
    onClick={() => setFeedType('latest')}
    className={feedType === 'latest' ? 'active' : ''}
  >
    Latest
  </button>
  <button 
    onClick={() => setFeedType('recommended')}
    className={feedType === 'recommended' ? 'active' : ''}
  >
    For You ✨
  </button>
</div>

// Fetch with type
const response = await axios.get(`/api/posts/feed?type=${feedType}`);
```

### 3. Create Post Error Handling
File: `post_app_fe/src/components/post/CreatePost.tsx`

```typescript
try {
  await createPost(postData);
  toast.success('Post created!');
} catch (error) {
  if (error.response?.status === 400) {
    // Moderation error
    toast.error(error.response.data.message);
  } else {
    toast.error('Failed to create post');
  }
}
```

## Troubleshooting

### AI Service won't start
```bash
docker-compose down
docker-compose up -d --build
docker-compose logs ai_service
```

### No recommendations
```bash
# Regenerate embeddings
docker-compose exec ai_service python scripts/generate_initial_embeddings.py
```

### MongoDB connection error
Edit `postal_ai_services/.env`:
```env
MONGODB_URI=mongodb://host.docker.internal:27017/postal
```

### Check vector DB data
```bash
curl http://localhost:8000/health
# Look for user/post counts
```

## Useful Commands

```bash
# Stop AI service
docker-compose down

# Restart AI service
docker-compose restart ai_service

# View AI service logs
docker-compose logs -f ai_service

# Enter AI service container
docker-compose exec ai_service bash

# Remove all data and restart fresh
docker-compose down -v
docker-compose up -d
```

## Environment Variables

### `Post_App/.env`
```env
AI_SERVICE_URL=http://localhost:8000
```

### `postal_ai_services/.env`
```env
MONGODB_URI=mongodb://localhost:27017/postal
QDRANT_HOST=qdrant
QDRANT_PORT=6333
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

## Test Commands

```bash
# Test moderation
curl -X POST http://localhost:8000/api/moderation/check \
  -H "Content-Type: application/json" \
  -d '{"text": "You are stupid!", "check_toxicity": true}'

# Test through backend (need auth token)
curl "http://localhost:3000/api/users/explore?ai=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Documentation

- **Full Guide**: `INTEGRATION_GUIDE.md`
- **Summary**: `AI_IMPLEMENTATION_SUMMARY.md`
- **AI Service**: `postal_ai_services/README.md`
- **Quick Start**: `postal_ai_services/QUICKSTART.md`

## What's Working ✅

- ✅ AI microservice
- ✅ Vector database
- ✅ User recommendations (backend)
- ✅ Post feed ranking (backend)
- ✅ Content moderation (backend)
- ✅ Semantic search (backend)

## What's Pending ⏳

- ⏳ Frontend Explore page update
- ⏳ Frontend Home feed toggle
- ⏳ Frontend error handling
- ⏳ Frontend search toggle (optional)

---

**Need help?** Check the full documentation in `INTEGRATION_GUIDE.md`

