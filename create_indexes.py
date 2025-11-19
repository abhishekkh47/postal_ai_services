#!/usr/bin/env python3
"""
Create payload indexes for Qdrant collections
"""
import sys
sys.path.append('.')

from src.core.dependencies import get_vector_db_service
from qdrant_client.models import PayloadSchemaType

def main():
    print("=" * 50)
    print("Creating Qdrant Payload Indexes")
    print("=" * 50)
    
    try:
        vector_db = get_vector_db_service()
        
        # Create index for users collection
        print("\n1. Creating index on 'user_id' for users collection...")
        try:
            vector_db.client.create_payload_index(
                collection_name="users",
                field_name="user_id",
                field_schema=PayloadSchemaType.KEYWORD
            )
            print("   ✓ Index created successfully")
        except Exception as e:
            print(f"   Note: {e}")
            print("   (Index might already exist)")
        
        # Create index for posts collection
        print("\n2. Creating index on 'post_id' for posts collection...")
        try:
            vector_db.client.create_payload_index(
                collection_name="posts",
                field_name="post_id",
                field_schema=PayloadSchemaType.KEYWORD
            )
            print("   ✓ Index created successfully")
        except Exception as e:
            print(f"   Note: {e}")
            print("   (Index might already exist)")
        
        # Verify indexes
        print("\n3. Verifying indexes...")
        users_collection = vector_db.client.get_collection("users")
        posts_collection = vector_db.client.get_collection("posts")
        
        print(f"   Users collection: {users_collection}")
        print(f"   Posts collection: {posts_collection}")
        
        print("\n" + "=" * 50)
        print("✓ Indexes created successfully!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

