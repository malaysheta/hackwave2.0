#!/usr/bin/env python3
"""
Test Supervisor Context Retrieval
Tests if the supervisor properly retrieves and uses context from LangGraph memory.
"""

import asyncio
import time
import uuid
from src.agent.memory import create_langgraph_memory_manager, create_memory_manager
from src.agent.graph import graph
from src.agent.state import OverallState


async def test_supervisor_context():
    """Test if supervisor properly retrieves context."""
    print("🔄 Testing Supervisor Context Retrieval...")
    
    # Generate test thread ID
    thread_id = f"supervisor_test_{uuid.uuid4().hex[:8]}"
    print(f"📝 Using thread ID: {thread_id}")
    
    try:
        # Test 1: First query
        print(f"\n📝 Test 1: First query")
        
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
        
        print("  🔄 Executing first query...")
        result = await graph.ainvoke(initial_state, config)
        
        print(f"  ✅ First query completed")
        print(f"  📊 Final answer length: {len(result.get('final_answer', ''))}")
        
        # Wait a moment
        await asyncio.sleep(1)
        
        # Test 2: Follow-up query with specific context reference
        print(f"\n📝 Test 2: Follow-up query with context reference")
        
        followup_state = OverallState(
            user_query="What about the photo sharing features I mentioned earlier?",
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
        
        # Check the final answer to see if it references previous context
        final_answer = followup_result.get('final_answer', '')
        print(f"\n📋 Final Answer Preview:")
        print(f"  {final_answer[:200]}...")
        
        # Check if the answer mentions previous context
        context_indicators = [
            "previously", "earlier", "mentioned", "before", "previous",
            "photographers", "social media", "photo sharing"
        ]
        
        context_found = any(indicator.lower() in final_answer.lower() for indicator in context_indicators)
        print(f"\n🔍 Context Analysis:")
        print(f"  Context indicators found: {context_found}")
        
        # Check memory entries
        print(f"\n🔍 Memory Analysis:")
        
        # Check LangGraph memory
        langgraph_memory = create_langgraph_memory_manager()
        langgraph_entries = langgraph_memory.get_conversation_context(thread_id, limit=5)
        print(f"  📊 LangGraph memory entries: {len(langgraph_entries)}")
        
        # Show memory entries
        for i, entry in enumerate(langgraph_entries):
            print(f"  Entry {i+1}:")
            print(f"    Query: {entry.get('user_query', '')}")
            print(f"    Response preview: {entry.get('response', '')[:100]}...")
            print(f"    Context keys: {list(entry.get('context', {}).keys())}")
        
        langgraph_memory.close()
        
        print("\n✅ Supervisor Context Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during supervisor context test: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Run the supervisor context test."""
    print("🚀 Starting Supervisor Context Test")
    print("=" * 50)
    
    await test_supervisor_context()
    
    print("\n" + "=" * 50)
    print("🎉 Supervisor Context Test Completed!")


if __name__ == "__main__":
    asyncio.run(main())
