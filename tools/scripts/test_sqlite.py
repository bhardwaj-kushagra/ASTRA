"""
Test script for SQLite integration.
"""
import sys
import os
import asyncio

# Setup paths
sys.path.insert(0, os.path.join(os.getcwd(), 'services', 'ingestion'))
sys.path.insert(0, os.path.join(os.getcwd(), 'data', 'schemas'))

from sqlite_publisher import SQLitePublisher


async def test_publisher():
    """Test the SQLite publisher."""
    print("Testing SQLite Publisher...")
    print("=" * 50)
    
    publisher = SQLitePublisher()
    
    # Test count
    count = await publisher.count_events()
    print(f"✓ Current events in database: {count}")
    
    # Test get_all
    events = await publisher.get_all_events()
    print(f"✓ Retrieved {len(events)} events")
    
    if events:
        print(f"\nSample event:")
        print(f"  ID: {events[0].id}")
        print(f"  Source: {events[0].source}")
        print(f"  Text preview: {events[0].text[:100]}...")
    
    print("\n✅ SQLite Publisher test passed!")


if __name__ == "__main__":
    asyncio.run(test_publisher())
