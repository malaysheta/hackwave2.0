#!/usr/bin/env python3
"""
Test Follow-up Context Functionality
Tests if the context is properly maintained between queries.
"""

import asyncio
import time
import uuid
from src.agent.memory import create_langgraph_memory_manager, create_memory_manager
from src.agent.graph import graph
from src.agent.state import OverallState


async def test_followup_context():
    """Test if follow-up queries have proper context."""
    print("🔄 Testing Follow-up Context Functionality...")
    
    # Generate test thread ID
    thread_id = f"followup_test_{uuid.uuid4().hex[:8]}"
    print(f"📝 Using thread ID: {thread_id}")
    
    try:
        # Test 1: First query
        print(f"\n📝 Test 1: First query")
        
        initial_state = OverallState(
            user_query="Create a mobile app for food delivery",
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
        
        print("  🔄 Executing first query...")
        result = await graph.ainvoke(initial_state, config)
        
        print(f"  ✅ First query completed")
        print(f"  📊 Final answer length: {len(result.get('final_answer', ''))}")
        
        # Check if data was saved to both memory systems
        print(f"\n🔍 Checking memory storage...")
        
        # Check regular memory
        memory_manager = create_memory_manager()
        history = memory_manager.get_conversation_history(thread_id, limit=5)
        print(f"  📊 Regular memory entries: {len(history)}")
        
        # Check LangGraph memory
        langgraph_memory = create_langgraph_memory_manager()
        langgraph_entries = langgraph_memory.get_conversation_context(thread_id, limit=5)
        print(f"  📊 LangGraph memory entries: {len(langgraph_entries)}")
        
        memory_manager.close()
        langgraph_memory.close()
        
        # Test 2: Follow-up query
        print(f"\n📝 Test 2: Follow-up query")
        
        followup_state = OverallState(
            user_query="What about the payment system?",
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
        
        # Check if follow-up data was saved
        print(f"\n🔍 Checking follow-up memory storage...")
        
        # Check regular memory again
        memory_manager = create_memory_manager()
        history_after = memory_manager.get_conversation_history(thread_id, limit=5)
        print(f"  📊 Regular memory entries after follow-up: {len(history_after)}")
        
        # Check LangGraph memory again
        langgraph_memory = create_langgraph_memory_manager()
        langgraph_entries_after = langgraph_memory.get_conversation_context(thread_id, limit=5)
        print(f"  📊 LangGraph memory entries after follow-up: {len(langgraph_entries_after)}")
        
        # Show the actual entries
        print(f"\n📋 LangGraph Memory Entries:")
        for i, entry in enumerate(langgraph_entries_after):
            print(f"  Entry {i+1}:")
            print(f"    Query: {entry.get('user_query', '')[:50]}...")
            print(f"    Response: {entry.get('response', '')[:100]}...")
            print(f"    Context keys: {list(entry.get('context', {}).keys())}")
        
        memory_manager.close()
        langgraph_memory.close()
        
        print("\n✅ Follow-up Context Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during follow-up context test: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run the follow-up context test."""
    print("🚀 Starting Follow-up Context Test")
    print("=" * 50)
    
    await test_followup_context()
    
    print("\n" + "=" * 50)
    print("🎉 Follow-up Context Test Completed!")


if __name__ == "__main__":
    asyncio.run(main())
