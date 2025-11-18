"""
Script to generate embeddings for existing users and posts in MongoDB
and store them in Qdrant vector database

Run this after:
1. Starting Docker containers (docker-compose up)
2. Running setup_vector_db.py
"""
import sys
sys.path.append('.')

from src.core.dependencies import (
    get_embeddings_service,
    get_vector_db_service,
    get_mongo_service
)
from tqdm import tqdm


def generate_user_embeddings():
    """Generate and store embeddings for all users"""
    print("\n" + "=" * 50)
    print("Generating User Embeddings")
    print("=" * 50)
    
    embeddings_service = get_embeddings_service()
    vector_db = get_vector_db_service()
    mongo = get_mongo_service()
    
    # Get all users from MongoDB
    users = mongo.get_all_users()
    print(f"\nFound {len(users)} users in database")
    
    if not users:
        print("No users found. Skipping user embeddings.")
        return
    
    # Generate embeddings for each user
    success_count = 0
    print(f"\nStarting to process {len(users)} users...")
    
    for idx, user in enumerate(users, 1):
        try:
            user_id = str(user['_id'])
            print(f"\n[{idx}/{len(users)}] Processing user: {user_id}")
            
            # Generate embedding
            print(f"  → Generating embedding...")
            embedding = embeddings_service.generate_user_embedding(user)
            print(f"  → Embedding generated: {len(embedding)} dimensions")
            
            # Store in vector database
            print(f"  → Storing in vector DB...")
            metadata = {
                'firstName': user.get('firstName', ''),
                'lastName': user.get('lastName', ''),
                'bio': user.get('bio', ''),
            }
            vector_db.upsert_user_embedding(user_id, embedding, metadata)
            print(f"  ✓ User {idx}/{len(users)} stored successfully")
            
            success_count += 1
        except Exception as e:
            import traceback
            print(f"\n✗ Error processing user {user.get('_id')}: {e}")
            print(traceback.format_exc())
            # Continue with next user instead of stopping
            continue
    
    print(f"\n✓ Successfully processed {success_count}/{len(users)} users")


def generate_post_embeddings():
    """Generate and store embeddings for all posts"""
    print("\n" + "=" * 50)
    print("Generating Post Embeddings")
    print("=" * 50)
    
    embeddings_service = get_embeddings_service()
    vector_db = get_vector_db_service()
    mongo = get_mongo_service()
    
    # Get all posts from MongoDB
    posts = mongo.get_all_posts()
    print(f"\nFound {len(posts)} posts in database")
    
    if not posts:
        print("No posts found. Skipping post embeddings.")
        return
    
    # Generate embeddings for each post
    success_count = 0
    print(f"\nStarting to process {len(posts)} posts...")
    
    for idx, post in enumerate(posts, 1):
        try:
            post_id = str(post['_id'])
            print(f"\n[{idx}/{len(posts)}] Processing post: {post_id}")
            
            # Generate embedding
            print(f"  → Generating embedding...")
            embedding = embeddings_service.generate_post_embedding(post)
            print(f"  → Embedding generated: {len(embedding)} dimensions")
            
            # Store in vector database
            print(f"  → Storing in vector DB...")
            metadata = {
                'userId': str(post.get('userId', '')),
                'type': post.get('type', 0),
                'reactions': post.get('reactions', 0),
                'comments': post.get('comments', 0),
            }
            vector_db.upsert_post_embedding(post_id, embedding, metadata)
            print(f"  ✓ Post {idx}/{len(posts)} stored successfully")
            
            success_count += 1
        except Exception as e:
            import traceback
            print(f"\n✗ Error processing post {post.get('_id')}: {e}")
            print(traceback.format_exc())
            continue
    
    print(f"\n✓ Successfully processed {success_count}/{len(posts)} posts")


def main():
    """Main function to generate all embeddings"""
    print("=" * 50)
    print("Generating Initial Embeddings")
    print("=" * 50)
    print("\nThis script will:")
    print("1. Fetch all users and posts from MongoDB")
    print("2. Generate embeddings using sentence-transformers")
    print("3. Store embeddings in Qdrant vector database")
    print("\nThis may take a while depending on data size...")
    
    try:
        # Generate user embeddings
        generate_user_embeddings()
        
        # Generate post embeddings
        generate_post_embeddings()
        
        # Get final statistics
        from src.core.dependencies import get_vector_db_service
        vector_db = get_vector_db_service()
        users_info = vector_db.get_collection_info("users")
        posts_info = vector_db.get_collection_info("posts")
        
        print("\n" + "=" * 50)
        print("Summary")
        print("=" * 50)
        print(f"Users in vector DB: {users_info.get('points_count', 0)}")
        print(f"Posts in vector DB: {posts_info.get('points_count', 0)}")
        print("\n✓ All embeddings generated successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

