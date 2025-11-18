"""
Script to initialize Qdrant vector database collections
Run this after starting the Docker containers
"""
import sys
sys.path.append('.')

from src.core.dependencies import get_vector_db_service


def main():
    """Initialize vector database collections"""
    print("=" * 50)
    print("Initializing Qdrant Vector Database")
    print("=" * 50)
    
    try:
        vector_db = get_vector_db_service()
        vector_db.create_collections()
        
        # Get collection info
        users_info = vector_db.get_collection_info("users")
        posts_info = vector_db.get_collection_info("posts")
        
        print("\n✓ Collections created successfully!")
        print(f"\nUsers collection: {users_info}")
        print(f"Posts collection: {posts_info}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()

