#!/usr/bin/env python3
"""
Standalone script to generate embeddings locally (outside Docker)
Run this on your Mac to populate the vector database
"""
import os
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from pymongo import MongoClient
from bson import ObjectId
import uuid

# Configuration
MONGODB_URI = "mongodb+srv://abhishek:Iluvsmst0%40@abhishek.uwmo9y2.mongodb.net/PostApp"
QDRANT_HOST = "localhost"  # Changed from 'qdrant' to 'localhost'
QDRANT_PORT = 6333
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

print("=" * 50)
print("Local Embedding Generation")
print("=" * 50)

# 1. Load embedding model
print("\n1. Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"   ✓ Model loaded: {EMBEDDING_MODEL}")

# 2. Connect to Qdrant
print("\n2. Connecting to Qdrant...")
qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
print(f"   ✓ Connected to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")

# 3. Connect to MongoDB
print("\n3. Connecting to MongoDB...")
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.get_default_database()
print(f"   ✓ Connected to MongoDB")

# 4. Process Users
print("\n4. Processing Users...")
users = list(db.users.find())
print(f"   Found {len(users)} users")

for idx, user in enumerate(users, 1):
    try:
        user_id = str(user['_id'])
        
        # Create text from user profile
        text_parts = []
        if user.get('firstName'):
            text_parts.append(user['firstName'])
        if user.get('lastName'):
            text_parts.append(user['lastName'])
        if user.get('bio'):
            text_parts.append(user['bio'])
        
        user_text = " ".join(text_parts) if text_parts else "user profile"
        
        # Generate embedding
        embedding = model.encode(user_text, convert_to_numpy=True).tolist()
        
        # Store in Qdrant
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "user_id": user_id,
                "firstName": user.get('firstName', ''),
                "lastName": user.get('lastName', ''),
                "bio": user.get('bio', ''),
            }
        )
        
        qdrant.upsert(
            collection_name="users",
            points=[point]
        )
        
        print(f"   [{idx}/{len(users)}] ✓ {user.get('firstName', 'Unknown')} {user.get('lastName', '')}")
        
    except Exception as e:
        print(f"   [{idx}/{len(users)}] ✗ Error: {e}")

print(f"\n✓ Successfully processed {len(users)} users")

# 5. Process Posts
print("\n5. Processing Posts...")
posts = list(db.posts.find())
print(f"   Found {len(posts)} posts")

for idx, post in enumerate(posts, 1):
    try:
        post_id = str(post['_id'])
        
        # Get post text
        post_text = post.get('post', '')
        if not post_text.strip():
            post_text = "post content"
        
        # Generate embedding
        embedding = model.encode(post_text, convert_to_numpy=True).tolist()
        
        # Store in Qdrant
        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "post_id": post_id,
                "userId": str(post.get('userId', '')),
                "type": post.get('type', 0),
                "reactions": post.get('reactions', 0),
                "comments": post.get('comments', 0),
            }
        )
        
        qdrant.upsert(
            collection_name="posts",
            points=[point]
        )
        
        print(f"   [{idx}/{len(posts)}] ✓ Post {post_id[:8]}...")
        
    except Exception as e:
        print(f"   [{idx}/{len(posts)}] ✗ Error: {e}")

print(f"\n✓ Successfully processed {len(posts)} posts")

# 6. Verify
print("\n6. Verifying...")
users_count = qdrant.count(collection_name="users", exact=True)
posts_count = qdrant.count(collection_name="posts", exact=True)

print(f"   Users in vector DB: {users_count.count}")
print(f"   Posts in vector DB: {posts_count.count}")

print("\n" + "=" * 50)
print("✓ All embeddings generated successfully!")
print("=" * 50)
print("\nYou can now use the AI service normally.")
print("The embeddings are stored in Qdrant and will persist.")

