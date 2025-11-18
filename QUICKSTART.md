# Quick Start Guide

## Step 1: Start the AI Service

```bash
cd /Users/mind/Projects/Postal/postal_ai_services

# Start services (Qdrant + AI Service)
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f ai_service
```

Wait for the message: **"Postal AI Service is ready!"**

## Step 2: Verify Service is Running

Open your browser and go to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use curl:
```bash
curl http://localhost:8000/health
```

## Step 3: Initialize Vector Database

```bash
# Enter the container
docker-compose exec ai_service bash

# Run setup script
python scripts/setup_vector_db.py

# Exit container
exit
```

## Step 4: Generate Embeddings for Existing Data

**Important**: Make sure your MongoDB (from the main Postal app) is running and accessible.

```bash
# Enter the container
docker-compose exec ai_service bash

# Generate embeddings (this may take a few minutes)
python scripts/generate_initial_embeddings.py

# Exit container
exit
```

This will:
- Fetch all users and posts from MongoDB
- Generate embeddings using AI
- Store them in Qdrant vector database

## Step 5: Test the Service

```bash
# Run test script
python test_service.py
```

## Step 6: Try the API

### Test Content Moderation (No data required)

```bash
curl -X POST http://localhost:8000/api/moderation/check \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a nice post!",
    "check_toxicity": true,
    "check_spam": true
  }'
```

### Test User Recommendations (Requires embeddings)

```bash
curl -X POST http://localhost:8000/api/recommendations/users \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "limit": 10,
    "exclude_following": true
  }'
```

### Test Semantic Search (Requires embeddings)

```bash
curl -X POST http://localhost:8000/api/search/posts \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fitness tips",
    "limit": 10
  }'
```

## Common Issues

### Issue: "Connection refused" error
**Solution**: Make sure Docker containers are running
```bash
docker-compose up -d
```

### Issue: "MongoDB connection error"
**Solution**: Update `.env` file with correct MongoDB URI
```bash
# Edit .env file
MONGODB_URI=mongodb://localhost:27017/postal
```

### Issue: "Collection not found"
**Solution**: Run the setup script
```bash
docker-compose exec ai_service python scripts/setup_vector_db.py
```

### Issue: "No recommendations returned"
**Solution**: Generate embeddings first
```bash
docker-compose exec ai_service python scripts/generate_initial_embeddings.py
```

## Next Steps

Once the AI service is working:

1. ✅ Integrate with Node.js backend
2. ✅ Update frontend to use AI features
3. ✅ Test end-to-end flow

See `README.md` for detailed documentation.

## Stopping the Service

```bash
# Stop services
docker-compose down

# Stop and remove volumes (clears vector DB data)
docker-compose down -v
```

## Useful Commands

```bash
# View all logs
docker-compose logs

# View only AI service logs
docker-compose logs ai_service

# View only Qdrant logs
docker-compose logs qdrant

# Restart AI service
docker-compose restart ai_service

# Rebuild after code changes
docker-compose up -d --build
```

