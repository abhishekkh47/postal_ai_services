# Postal AI Integration Guide

This guide explains how the AI features have been integrated into your Postal social media application.

## 🎯 What's Been Implemented

### Backend (Node.js) Integration

#### 1. **AI Service Client** (`Post_App/src/services/ai.service.ts`)
- Communicates with Python AI microservice
- Handles all AI operations with error handling and fallbacks
- Methods:
  - `getUserRecommendations()` - Get similar users
  - `getPostRecommendations()` - Get personalized posts
  - `searchPosts()` - Semantic search
  - `moderateContent()` - Toxicity/spam detection

#### 2. **User Recommendations** (`Post_App/src/controllers/user.controller.ts`)
- **Endpoint**: `GET /api/users/explore?ai=true`
- Uses AI to recommend users based on profile similarity
- Falls back to random users if AI service is unavailable
- Response includes `ai_powered` flag

#### 3. **Post Feed Ranking** (`Post_App/src/controllers/post.controller.ts`)
- **Endpoint**: `GET /api/posts/feed?type=recommended`
- Two feed types:
  - `type=latest` - Chronological feed (default)
  - `type=recommended` - AI-powered personalized feed
- Falls back to chronological if AI fails

#### 4. **Content Moderation**
- **Posts**: Checks toxicity before creating post
- **Comments**: Checks toxicity before creating comment
- Rejects content with high toxicity score
- Logs warnings for moderate toxicity
- Fails open (allows content) if AI service is down

---

## 🚀 How to Use

### Step 1: Start the AI Service

```bash
cd /Users/mind/Projects/Postal/postal_ai_services

# Start Docker containers
docker-compose up -d

# Check if running
docker-compose ps

# View logs
docker-compose logs -f ai_service
```

### Step 2: Initialize Vector Database

```bash
# Enter container
docker-compose exec ai_service bash

# Create collections
python scripts/setup_vector_db.py

# Exit
exit
```

### Step 3: Generate Embeddings

**Important**: Make sure your MongoDB is running first!

```bash
# Enter container
docker-compose exec ai_service bash

# Generate embeddings for existing data
python scripts/generate_initial_embeddings.py

# This will:
# - Fetch all users from MongoDB
# - Generate AI embeddings for each user
# - Store in vector database
# - Same for posts

# Exit
exit
```

### Step 4: Add Environment Variable to Node.js Backend

Edit `/Users/mind/Projects/Postal/Post_App/.env`:

```env
AI_SERVICE_URL=http://localhost:8000
```

### Step 5: Restart Node.js Backend

```bash
cd /Users/mind/Projects/Postal/Post_App
npm run start
```

---

## 📡 API Usage Examples

### 1. Get AI-Powered User Recommendations

```bash
# Frontend makes this call
GET /api/users/explore?ai=true

# Response:
{
  "users": [...],
  "ai_powered": true,
  "total": 10
}
```

### 2. Get AI-Powered Feed

```bash
# Frontend makes this call
GET /api/posts/feed?type=recommended&page=1

# Response:
{
  "posts": [...],
  "feed_type": "recommended",
  "ai_powered": true,
  "currentPage": 1
}
```

### 3. Create Post (with automatic moderation)

```bash
POST /api/posts/create
{
  "post": "This is my post content"
}

# If toxic content detected:
{
  "status": 400,
  "message": "Your post contains inappropriate content. Reasons: high_toxicity"
}
```

---

## 🎨 Frontend Integration (Next Steps)

### 1. Update Explore Page

File: `post_app_fe/src/pages/Explore.tsx`

```typescript
// Add AI toggle or automatically use AI
const { loading, friendSuggestions } = useFriends(true); // Pass useAI flag

// Or modify the API call in useFriends hook
const response = await axios.get('/api/users/explore?ai=true');
```

### 2. Update Home Feed

File: `post_app_fe/src/pages/Home.tsx`

Add tabs to switch between feeds:

```typescript
const [feedType, setFeedType] = useState('latest'); // or 'recommended'

// Fetch feed based on type
const response = await axios.get(`/api/posts/feed?type=${feedType}`);

// UI:
<div className="flex space-x-2 mb-4">
  <button onClick={() => setFeedType('latest')}>Latest</button>
  <button onClick={() => setFeedType('recommended')}>For You ✨</button>
</div>
```

### 3. Handle Moderation Errors

File: `post_app_fe/src/components/post/CreatePost.tsx`

```typescript
try {
  await createPost(postData);
} catch (error) {
  if (error.response?.status === 400) {
    // Show moderation error to user
    showToast(error.response.data.message, 'error');
  }
}
```

---

## 🔧 Configuration

### AI Service Settings

File: `postal_ai_services/.env`

```env
# MongoDB (must match your main app)
MONGODB_URI=mongodb://localhost:27017/postal

# Qdrant (vector database)
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# AI Model Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
MAX_RESULTS=10
```

### Node.js Backend Settings

File: `Post_App/.env`

```env
AI_SERVICE_URL=http://localhost:8000
```

---

## 🧪 Testing

### Test AI Service Directly

```bash
# Health check
curl http://localhost:8000/health

# Test moderation
curl -X POST http://localhost:8000/api/moderation/check \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!", "check_toxicity": true, "check_spam": true}'

# Test user recommendations (replace USER_ID)
curl -X POST http://localhost:8000/api/recommendations/users \
  -H "Content-Type: application/json" \
  -d '{"user_id": "YOUR_USER_ID", "limit": 10}'
```

### Test Through Node.js Backend

```bash
# Get AI recommendations
curl http://localhost:3000/api/users/explore?ai=true \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get AI feed
curl "http://localhost:3000/api/posts/feed?type=recommended" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 How It Works

### User Recommendations Flow

```
1. User visits Explore page
2. Frontend calls: GET /api/users/explore?ai=true
3. Node.js backend calls AI service
4. AI service:
   - Gets user's profile from MongoDB
   - Generates embedding (vector representation)
   - Searches vector DB for similar users
   - Returns user IDs sorted by similarity
5. Node.js fetches full user details
6. Frontend displays recommended users
```

### Content Moderation Flow

```
1. User creates post/comment
2. Frontend sends to Node.js
3. Node.js calls AI service moderation
4. AI service:
   - Analyzes text for toxicity
   - Checks for spam patterns
   - Returns safety scores
5. If unsafe:
   - Node.js rejects with error message
   - Frontend shows error to user
6. If safe:
   - Post/comment is created
   - Success response sent
```

---

## 🔄 Keeping Embeddings Updated

### When New Users Register

Add this to your user registration flow:

```typescript
// After user is created in MongoDB
try {
  await AIService.generateUserEmbedding(userId);
} catch (error) {
  console.error('Failed to generate user embedding:', error);
  // Non-critical, can be done later
}
```

### When New Posts are Created

Add this to your post creation flow:

```typescript
// After post is created in MongoDB
try {
  await AIService.generatePostEmbedding(postId);
} catch (error) {
  console.error('Failed to generate post embedding:', error);
  // Non-critical, can be done later
}
```

### Batch Update (Recommended)

Run this periodically (e.g., daily via cron job):

```bash
docker-compose exec ai_service python scripts/generate_initial_embeddings.py
```

---

## 🐛 Troubleshooting

### AI Service Not Responding

```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs ai_service

# Restart service
docker-compose restart ai_service
```

### MongoDB Connection Error

- Ensure MongoDB is running
- Check `MONGODB_URI` in `postal_ai_services/.env`
- If MongoDB is in Docker, use `host.docker.internal` instead of `localhost`

```env
MONGODB_URI=mongodb://host.docker.internal:27017/postal
```

### No Recommendations Returned

- Ensure embeddings have been generated
- Check vector DB has data:

```bash
curl http://localhost:8000/health
# Look for "users" and "posts" counts
```

### Moderation Always Passes

- Check AI service logs
- Test moderation directly:

```bash
curl -X POST http://localhost:8000/api/moderation/check \
  -H "Content-Type: application/json" \
  -d '{"text": "You are stupid!", "check_toxicity": true}'
```

---

## 📈 Performance Tips

1. **Caching**: AI recommendations are not cached by default. Consider adding Redis caching for frequently requested recommendations.

2. **Batch Processing**: Generate embeddings in batches during low-traffic periods.

3. **Fallback Strategy**: The system is designed to fail gracefully. If AI service is down, it falls back to non-AI features.

4. **Monitoring**: Monitor AI service response times and adjust timeouts if needed.

---

## 🎓 What You've Learned

✅ Vector databases (Qdrant)  
✅ Text embeddings with sentence-transformers  
✅ Semantic similarity search  
✅ Content moderation with ML  
✅ Microservices architecture  
✅ FastAPI (Python web framework)  
✅ Docker containerization  
✅ Graceful degradation patterns  

---

## 🚀 Next Steps

1. **Frontend Integration**: Update React components to use AI features
2. **Add Search**: Implement semantic search in the search bar
3. **Analytics**: Track which recommendations users click on
4. **Tuning**: Adjust similarity thresholds based on user feedback
5. **Scaling**: Add load balancing for multiple AI service instances

---

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Detoxify (Toxicity Detection)](https://github.com/unitaryai/detoxify)

---

Need help? Check the logs:
- AI Service: `docker-compose logs ai_service`
- Node.js: Check your Node.js console
- MongoDB: Check MongoDB logs

Happy coding! 🎉

