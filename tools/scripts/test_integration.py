"""
End-to-end integration test for ASTRA prototype.
"""
import sys
import os

# Add schemas to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'schemas')))

from models import DetectionRequest


def test_file_ingestion():
    """Test ingestion service with file connector."""
    import requests
    
    print("\n=== Testing File Ingestion ===")
    response = requests.post(
        "http://localhost:8001/ingest",
        json={
            "connector_type": "file",
            "config": {
                "path": "../../data/samples",
                "pattern": "*.txt"
            }
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_detection():
    """Test detection service."""
    import requests
    
    print("\n=== Testing Detection Service ===")
    test_text = "This is a test message that might be AI-generated or human-written."
    
    response = requests.post(
        "http://localhost:8002/detect",
        json={"text": test_text}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_analytics_sync():
    """Test analytics sync from ingestion."""
    import requests
    
    print("\n=== Testing Analytics Sync ===")
    response = requests.post("http://localhost:8003/sync-from-ingestion")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_analytics_stats():
    """Test analytics statistics endpoint."""
    import requests
    
    print("\n=== Testing Analytics Stats ===")
    response = requests.get("http://localhost:8003/stats")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


if __name__ == "__main__":
    print("ASTRA Prototype Integration Test")
    print("=" * 50)
    print("\nMake sure all services are running:")
    print("  - Ingestion: http://localhost:8001")
    print("  - Detection: http://localhost:8002")
    print("  - Analytics: http://localhost:8003")
    print("\n" + "=" * 50)
    
    try:
        tests = [
            ("Detection Service", test_detection),
            ("Analytics Statistics", test_analytics_stats)
        ]
        
        results = []
        for name, test_func in tests:
            try:
                success = test_func()
                results.append((name, success))
            except Exception as e:
                print(f"\n❌ {name} failed: {e}")
                results.append((name, False))
        
        print("\n" + "=" * 50)
        print("Test Results:")
        print("=" * 50)
        for name, success in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {name}")
        
        all_passed = all(success for _, success in results)
        print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️  Some tests failed"))
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
