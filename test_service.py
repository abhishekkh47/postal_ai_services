"""
Quick test script to verify AI service is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint"""
    print("\n" + "=" * 50)
    print("Testing Health Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_user_recommendations(user_id: str):
    """Test user recommendations endpoint"""
    print("\n" + "=" * 50)
    print("Testing User Recommendations")
    print("=" * 50)
    
    try:
        payload = {
            "user_id": user_id,
            "limit": 5,
            "exclude_following": True
        }
        response = requests.post(
            f"{BASE_URL}/api/recommendations/users",
            json=payload
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_moderation():
    """Test content moderation endpoint"""
    print("\n" + "=" * 50)
    print("Testing Content Moderation")
    print("=" * 50)
    
    test_texts = [
        "Hello, this is a nice post!",
        "You are stupid and I hate you!",
        "Click here to win $1000000 now!!!"
    ]
    
    for text in test_texts:
        print(f"\nTesting: '{text}'")
        try:
            payload = {
                "text": text,
                "check_toxicity": True,
                "check_spam": True
            }
            response = requests.post(
                f"{BASE_URL}/api/moderation/check",
                json=payload
            )
            result = response.json()
            print(f"  Safe: {result['is_safe']}")
            print(f"  Toxicity: {result['toxicity_score']:.3f}")
            print(f"  Spam: {result['spam_score']:.3f}")
            if result['flagged_reasons']:
                print(f"  Flagged: {', '.join(result['flagged_reasons'])}")
        except Exception as e:
            print(f"  Error: {e}")


def test_semantic_search():
    """Test semantic search endpoint"""
    print("\n" + "=" * 50)
    print("Testing Semantic Search")
    print("=" * 50)
    
    try:
        payload = {
            "query": "fitness and health tips",
            "limit": 5,
            "search_type": "posts"
        }
        response = requests.post(
            f"{BASE_URL}/api/search/posts",
            json=payload
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Postal AI Service - Quick Test")
    print("=" * 50)
    print(f"\nTesting service at: {BASE_URL}")
    
    # Test health
    health_ok = test_health()
    
    if not health_ok:
        print("\n❌ Service is not healthy. Please check if it's running:")
        print("   docker-compose up -d")
        return
    
    print("\n✅ Service is healthy!")
    
    # Test moderation (doesn't require data)
    test_moderation()
    
    # Test other endpoints (requires data)
    print("\n" + "=" * 50)
    print("Note: User recommendations and search require:")
    print("1. MongoDB data")
    print("2. Generated embeddings (run generate_initial_embeddings.py)")
    print("=" * 50)
    
    # Uncomment these after running generate_initial_embeddings.py
    # test_user_recommendations("YOUR_USER_ID_HERE")
    # test_semantic_search()
    
    print("\n" + "=" * 50)
    print("Tests Complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()

