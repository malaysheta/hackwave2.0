#!/usr/bin/env python3
"""
Test script to verify error fixes for LangGraph Memory System
"""

import os
import sys
import requests
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_backend_connection():
    """Test if backend is running and responding."""
    try:
        response = requests.get("http://localhost:2024/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and responding")
            return True
        else:
            print(f"❌ Backend responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_thread_context_endpoint():
    """Test the thread-context endpoint that was causing errors."""
    try:
        thread_id = "test_thread_123"
        response = requests.get(f"http://localhost:2024/api/thread-context/{thread_id}", timeout=10)
        
        print(f"📊 Thread context response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Thread context endpoint working")
            print(f"   - Thread ID: {data.get('thread_id')}")
            print(f"   - Has Context: {data.get('has_context')}")
            print(f"   - Conversation Count: {data.get('conversation_count')}")
            return True
        else:
            print(f"❌ Thread context endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Thread context test failed: {e}")
        return False

def test_langgraph_memory_endpoint():
    """Test the LangGraph memory endpoint."""
    try:
        thread_id = "test_thread_123"
        response = requests.get(f"http://localhost:2024/api/langgraph-memory/{thread_id}", timeout=10)
        
        print(f"📊 LangGraph memory response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ LangGraph memory endpoint working")
            print(f"   - Memory Entries: {len(data.get('memory_entries', []))}")
            print(f"   - Storage Type: {data.get('memory_stats', {}).get('storage_type', 'Unknown')}")
            return True
        else:
            print(f"❌ LangGraph memory endpoint failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ LangGraph memory test failed: {e}")
        return False

def test_memory_manager_import():
    """Test if memory manager can be imported without errors."""
    try:
        from src.agent.memory import create_memory_manager, create_langgraph_memory_manager
        
        # Test regular memory manager
        memory_manager = create_memory_manager()
        print("✅ Regular memory manager created successfully")
        
        # Test LangGraph memory manager
        langgraph_memory = create_langgraph_memory_manager()
        print("✅ LangGraph memory manager created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory manager import failed: {e}")
        return False

def test_graph_import():
    """Test if graph can be imported without logger errors."""
    try:
        from src.agent.graph import supervisor_node
        print("✅ Graph module imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Graph import failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Error Fixes for LangGraph Memory System")
    print("=" * 60)
    
    tests = [
        ("Memory Manager Import", test_memory_manager_import),
        ("Graph Import", test_graph_import),
        ("Backend Connection", test_backend_connection),
        ("Thread Context Endpoint", test_thread_context_endpoint),
        ("LangGraph Memory Endpoint", test_langgraph_memory_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Error fixes are working.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
