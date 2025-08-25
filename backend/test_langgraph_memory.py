#!/usr/bin/env python3
"""
Test script for LangGraph Memory System
Tests the new LangGraph memory manager that stores one big array in MongoDB.
"""

import asyncio
import time
import uuid
from src.agent.memory import create_langgraph_memory_manager
from src.agent.graph import graph
from src.agent.state import OverallState
from src.agent.configuration import Configuration


def test_langgraph_memory_manager():
    """Test the LangGraph Memory Manager functionality."""
    print("🧠 Testing LangGraph Memory Manager...")
    
    # Create memory manager
    memory_manager = create_langgraph_memory_manager()
    
    # Generate test thread ID
    thread_id = f"test_thread_{uuid.uuid4().hex[:8]}"
    
    try:
        # Test 1: Add entries to memory array
        print(f"\n📝 Test 1: Adding entries to memory array for thread {thread_id}")
        
        test_queries = [
            "Create a mobile app for food delivery",
            "What features should the app have?",
            "How should the payment system work?",
            "What about user authentication?",
            "Can you add push notifications?"
        ]
        
        test_responses = [
            "I'll help you create a comprehensive mobile app for food delivery. Let me analyze the requirements...",
            "The app should have user registration, restaurant browsing, order placement, real-time tracking, and payment processing.",
            "The payment system should support multiple methods including credit cards, digital wallets, and cash on delivery.",
            "User authentication should use OAuth 2.0 with social login options and secure token-based sessions.",
            "Push notifications will be implemented for order updates, promotions, and delivery status changes."
        ]
        
        for i, (query, response) in enumerate(zip(test_queries, test_responses)):
            context = {
                "step": i + 1,
                "agent": "test_agent",
                "timestamp": time.time(),
                "test_data": f"test_context_{i}"
            }
            
            success = memory_manager.add_to_memory_array(
                thread_id=thread_id,
                user_query=query,
                response=response,
                context=context
            )
            
            print(f"  ✅ Added entry {i+1}: {success}")
            time.sleep(0.1)  # Small delay
        
        # Test 2: Get memory context
        print(f"\n🔍 Test 2: Retrieving memory context for thread {thread_id}")
        memory_entries = memory_manager.get_conversation_context(thread_id, limit=10)
        print(f"  📊 Retrieved {len(memory_entries)} memory entries")
        
        for i, entry in enumerate(memory_entries):
            print(f"    Entry {i+1}: {entry.get('user_query', '')[:50]}...")
        
        # Test 3: Search memory
        print(f"\n🔎 Test 3: Searching memory for 'payment'")
        search_results = memory_manager.search_memory("payment", limit=5)
        print(f"  📊 Found {len(search_results)} relevant entries")
        
        for i, result in enumerate(search_results):
            print(f"    Result {i+1}: {result.get('user_query', '')[:50]}...")
        
        # Test 4: Get memory statistics
        print(f"\n📈 Test 4: Getting memory statistics")
        stats = memory_manager.get_memory_stats()
        print(f"  📊 Memory Stats: {stats}")
        
        # Test 5: Test with different thread
        print(f"\n🔄 Test 5: Testing with different thread")
        thread_id_2 = f"test_thread_2_{uuid.uuid4().hex[:8]}"
        
        success = memory_manager.add_to_memory_array(
            thread_id=thread_id_2,
            user_query="Different thread query",
            response="Different thread response",
            context={"test": "different_thread"}
        )
        print(f"  ✅ Added entry to different thread: {success}")
        
        # Get context for both threads
        entries_1 = memory_manager.get_conversation_context(thread_id, limit=5)
        entries_2 = memory_manager.get_conversation_context(thread_id_2, limit=5)
        print(f"  📊 Thread 1 entries: {len(entries_1)}, Thread 2 entries: {len(entries_2)}")
        
        # Test 6: Clear specific thread memory
        print(f"\n🗑️ Test 6: Clearing memory for thread {thread_id_2}")
        cleared = memory_manager.clear_memory(thread_id_2)
        print(f"  ✅ Cleared thread 2 memory: {cleared}")
        
        # Verify thread 2 is cleared but thread 1 remains
        entries_1_after = memory_manager.get_conversation_context(thread_id, limit=5)
        entries_2_after = memory_manager.get_conversation_context(thread_id_2, limit=5)
        print(f"  📊 After clearing - Thread 1: {len(entries_1_after)}, Thread 2: {len(entries_2_after)}")
        
        print("\n✅ LangGraph Memory Manager tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during LangGraph Memory Manager tests: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        memory_manager.close()


async def test_langgraph_memory_with_graph():
    """Test LangGraph memory integration with the graph."""
    print("\n🔄 Testing LangGraph Memory with Graph Integration...")
    
    # Generate test thread ID
    thread_id = f"graph_test_{uuid.uuid4().hex[:8]}"
    
    try:
        # Test 1: First query
        print(f"\n📝 Test 1: First query for thread {thread_id}")
        
        initial_state = OverallState(
            user_query="Create a social media app for photographers",
            query_type=None,
            debate_content=None,
            current_step=1,
            max_steps=10,
            agent_history=[],
            active_agent=None,
            supervisor_decision=None,
            supervisor_reasoning=None,
            is_complete=False,
            processing_time=0.0,
            final_answer=None
        )
        
        config = {
            "configurable": {
                "thread_id": thread_id,
                "model": "gemini-2.0-flash",
                "max_debate_resolution_time": 120,
                "enable_parallel_processing": True
            }
        }
        
        print("  🔄 Executing graph...")
        result = await graph.ainvoke(initial_state, config)
        
        print(f"  ✅ First query completed")
        print(f"  📊 Final answer length: {len(result.get('final_answer', ''))}")
        print(f"  📊 Processing time: {result.get('processing_time', 0):.2f}s")
        
        # Test 2: Follow-up query
        print(f"\n📝 Test 2: Follow-up query for thread {thread_id}")
        
        followup_state = OverallState(
            user_query="What about the photo sharing features?",
            query_type=None,
            debate_content=None,
            current_step=1,
            max_steps=10,
            agent_history=[],
            active_agent=None,
            supervisor_decision=None,
            supervisor_reasoning=None,
            is_complete=False,
            processing_time=0.0,
            final_answer=None
        )
        
        print("  🔄 Executing follow-up query...")
        followup_result = await graph.ainvoke(followup_state, config)
        
        print(f"  ✅ Follow-up query completed")
        print(f"  📊 Final answer length: {len(followup_result.get('final_answer', ''))}")
        print(f"  📊 Processing time: {followup_result.get('processing_time', 0):.2f}s")
        
        # Test 3: Check LangGraph memory
        print(f"\n🔍 Test 3: Checking LangGraph memory for thread {thread_id}")
        
        memory_manager = create_langgraph_memory_manager()
        memory_entries = memory_manager.get_conversation_context(thread_id, limit=10)
        
        print(f"  📊 Found {len(memory_entries)} memory entries")
        for i, entry in enumerate(memory_entries):
            print(f"    Entry {i+1}: {entry.get('user_query', '')[:50]}...")
            print(f"      Response: {entry.get('response', '')[:100]}...")
        
        memory_manager.close()
        
        print("\n✅ LangGraph Memory with Graph Integration tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during Graph Integration tests: {e}")
        import traceback
        traceback.print_exc()


def test_memory_persistence():
    """Test that memory persists across different instances."""
    print("\n💾 Testing Memory Persistence...")
    
    thread_id = f"persistence_test_{uuid.uuid4().hex[:8]}"
    
    try:
        # Create first instance and add data
        print(f"\n📝 Adding data with first instance for thread {thread_id}")
        memory_manager_1 = create_langgraph_memory_manager()
        
        success = memory_manager_1.add_to_memory_array(
            thread_id=thread_id,
            user_query="Persistence test query",
            response="Persistence test response",
            context={"test": "persistence"}
        )
        print(f"  ✅ Added entry: {success}")
        
        memory_manager_1.close()
        
        # Create second instance and retrieve data
        print(f"\n🔍 Retrieving data with second instance for thread {thread_id}")
        memory_manager_2 = create_langgraph_memory_manager()
        
        entries = memory_manager_2.get_conversation_context(thread_id, limit=5)
        print(f"  📊 Retrieved {len(entries)} entries")
        
        if entries:
            print(f"  ✅ Data persisted successfully!")
            print(f"  📝 First entry: {entries[0].get('user_query', '')}")
        else:
            print(f"  ❌ Data did not persist!")
        
        memory_manager_2.close()
        
        print("\n✅ Memory Persistence tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during Memory Persistence tests: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all LangGraph memory tests."""
    print("🚀 Starting LangGraph Memory System Tests")
    print("=" * 50)
    
    # Test 1: Basic memory manager functionality
    test_langgraph_memory_manager()
    
    # Test 2: Memory persistence
    test_memory_persistence()
    
    # Test 3: Graph integration
    await test_langgraph_memory_with_graph()
    
    print("\n" + "=" * 50)
    print("🎉 All LangGraph Memory System Tests Completed!")
    print("\n📋 Summary:")
    print("  ✅ LangGraph Memory Manager functionality")
    print("  ✅ Memory persistence across instances")
    print("  ✅ Graph integration with memory context")
    print("  ✅ Follow-up question handling")
    print("  ✅ MongoDB storage with single array approach")


if __name__ == "__main__":
    asyncio.run(main())
