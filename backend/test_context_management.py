#!/usr/bin/env python3
"""
Test script for context management functionality.
This script tests the conversation history and context persistence features.
"""

import requests
import json
import time
import uuid

# Configuration
API_BASE_URL = "http://localhost:2024"

def test_context_management():
    """Test the complete context management flow."""
    
    print("🧪 Testing Context Management System")
    print("=" * 50)
    
    # Generate a unique thread ID for testing
    thread_id = f"test_thread_{uuid.uuid4().hex[:8]}"
    print(f"📝 Using test thread ID: {thread_id}")
    
    # Test 1: Check initial context (should be empty)
    print("\n1️⃣ Testing initial context check...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/context/{thread_id}")
        if response.status_code == 200:
            context_data = response.json()
            print(f"✅ Context check successful")
            print(f"   Has context: {context_data.get('has_context', False)}")
            print(f"   Conversation count: {context_data.get('conversation_count', 0)}")
        else:
            print(f"❌ Context check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Context check error: {e}")
    
    # Test 2: Send first query
    print("\n2️⃣ Testing first query...")
    first_query = "Create a mobile app for food delivery"
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/refine-requirements",
            json={
                "query": first_query,
                "query_type": "general",
                "thread_id": thread_id
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ First query successful")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"   Answer length: {len(result.get('answer', ''))} chars")
        else:
            print(f"❌ First query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ First query error: {e}")
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Test 3: Check context after first query
    print("\n3️⃣ Testing context after first query...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/context/{thread_id}")
        if response.status_code == 200:
            context_data = response.json()
            print(f"✅ Context check successful")
            print(f"   Has context: {context_data.get('has_context', False)}")
            print(f"   Conversation count: {context_data.get('conversation_count', 0)}")
            if context_data.get('history'):
                print(f"   Latest query: {context_data['history'][0].get('user_query', 'N/A')[:50]}...")
        else:
            print(f"❌ Context check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Context check error: {e}")
    
    # Test 4: Send follow-up query
    print("\n4️⃣ Testing follow-up query...")
    followup_query = "What about the revenue model for this app?"
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/refine-requirements",
            json={
                "query": followup_query,
                "query_type": "revenue",
                "thread_id": thread_id
            }
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Follow-up query successful")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"   Is follow-up: {result.get('is_followup', False)}")
            print(f"   Answer length: {len(result.get('answer', ''))} chars")
        else:
            print(f"❌ Follow-up query failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Follow-up query error: {e}")
    
    # Wait a moment for processing
    time.sleep(2)
    
    # Test 5: Check final context
    print("\n5️⃣ Testing final context check...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/context/{thread_id}")
        if response.status_code == 200:
            context_data = response.json()
            print(f"✅ Final context check successful")
            print(f"   Has context: {context_data.get('has_context', False)}")
            print(f"   Conversation count: {context_data.get('conversation_count', 0)}")
            if context_data.get('history'):
                print(f"   Total conversations: {len(context_data['history'])}")
                for i, conv in enumerate(context_data['history'][:3]):  # Show first 3
                    print(f"   Conversation {i+1}: {conv.get('user_query', 'N/A')[:40]}...")
        else:
            print(f"❌ Final context check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final context check error: {e}")
    
    # Test 6: Test conversation history endpoint
    print("\n6️⃣ Testing conversation history endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/conversation-history/{thread_id}")
        if response.status_code == 200:
            history_data = response.json()
            print(f"✅ Conversation history successful")
            print(f"   History entries: {len(history_data.get('history', []))}")
        else:
            print(f"❌ Conversation history failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Conversation history error: {e}")
    
    # Test 7: Test default conversation history
    print("\n7️⃣ Testing default conversation history...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/conversation-history/default")
        if response.status_code == 200:
            default_history = response.json()
            print(f"✅ Default history successful")
            print(f"   Total entries: {len(default_history)}")
            if default_history:
                print(f"   Latest entry: {default_history[0].get('user_query', 'N/A')[:40]}...")
        else:
            print(f"❌ Default history failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Default history error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Context Management Test Complete!")
    print(f"📋 Test thread ID: {thread_id}")
    print("💡 Check the database to verify data persistence")

if __name__ == "__main__":
    test_context_management()
