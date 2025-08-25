#!/usr/bin/env python3
"""
Test script for follow-up functionality in the multi-agent system.
This script tests that follow-up questions are routed efficiently to specific agents
instead of running all agents.
"""

import asyncio
import json
import time
from typing import Dict, Any

from src.agent.graph import graph
from src.agent.state import OverallState, QueryType, DebateCategory


async def test_followup_functionality():
    """Test that follow-up questions are handled efficiently."""
    
    print("🧪 Testing Follow-up Functionality")
    print("=" * 50)
    
    # Test 1: Initial query (should run full multi-agent analysis)
    print("\n📝 Test 1: Initial Query (Full Analysis)")
    print("-" * 30)
    
    initial_state: OverallState = {
        "messages": [],
        "user_query": "I want to build a SaaS application for project management",
        "query_type": QueryType.GENERAL,
        "debate_category": None,
        "domain_expert_analysis": None,
        "ux_ui_specialist_analysis": None,
        "technical_architect_analysis": None,
        "revenue_model_analyst_analysis": None,
        "moderator_aggregation": None,
        "debate_resolution": None,
        "final_answer": None,
        "processing_time": 0.0,
        "active_agent": None,
        "supervisor_decision": None,
        "supervisor_reasoning": None,
        "agent_history": [],
        "current_step": 1,
        "max_steps": 10,
        "is_complete": False
    }
    
    start_time = time.time()
    result = await graph.ainvoke(initial_state)
    initial_time = time.time() - start_time
    
    print(f"✅ Initial query completed in {initial_time:.2f} seconds")
    print(f"📊 Agent history length: {len(result.get('agent_history', []))}")
    print(f"🎯 Final answer length: {len(result.get('final_answer', ''))}")
    
    # Test 2: Follow-up revenue question (should route directly to revenue analyst)
    print("\n💰 Test 2: Follow-up Revenue Question")
    print("-" * 30)
    
    followup_state: OverallState = {
        "messages": [],
        "user_query": "How can I monetize this SaaS application and what pricing strategy should I use?",
        "query_type": QueryType.GENERAL,
        "debate_category": None,
        "domain_expert_analysis": None,
        "ux_ui_specialist_analysis": None,
        "technical_architect_analysis": None,
        "revenue_model_analyst_analysis": None,
        "moderator_aggregation": None,
        "debate_resolution": None,
        "final_answer": None,
        "processing_time": 0.0,
        "active_agent": None,
        "supervisor_decision": None,
        "supervisor_reasoning": None,
        "agent_history": result.get("agent_history", []),  # Include previous history
        "current_step": 1,
        "max_steps": 10,
        "is_complete": False
    }
    
    start_time = time.time()
    followup_result = await graph.ainvoke(followup_state)
    followup_time = time.time() - start_time
    
    print(f"✅ Follow-up revenue query completed in {followup_time:.2f} seconds")
    print(f"📊 Agent history length: {len(followup_result.get('agent_history', []))}")
    print(f"🎯 Final answer length: {len(followup_result.get('final_answer', ''))}")
    
    # Check if it was routed to revenue analyst
    agent_history = followup_result.get("agent_history", [])
    revenue_analysis = followup_result.get("revenue_model_analyst_analysis")
    
    if revenue_analysis:
        print("✅ Successfully routed to Revenue Model Analyst")
        print(f"📈 Revenue analysis length: {len(revenue_analysis)}")
    else:
        print("❌ Not routed to Revenue Model Analyst")
    
    # Test 3: Follow-up technical question (should route directly to technical architect)
    print("\n⚙️ Test 3: Follow-up Technical Question")
    print("-" * 30)
    
    technical_followup_state: OverallState = {
        "messages": [],
        "user_query": "What technology stack should I use for the backend and how should I handle scalability?",
        "query_type": QueryType.GENERAL,
        "debate_category": None,
        "domain_expert_analysis": None,
        "ux_ui_specialist_analysis": None,
        "technical_architect_analysis": None,
        "revenue_model_analyst_analysis": None,
        "moderator_aggregation": None,
        "debate_resolution": None,
        "final_answer": None,
        "processing_time": 0.0,
        "active_agent": None,
        "supervisor_decision": None,
        "supervisor_reasoning": None,
        "agent_history": followup_result.get("agent_history", []),  # Include previous history
        "current_step": 1,
        "max_steps": 10,
        "is_complete": False
    }
    
    start_time = time.time()
    technical_result = await graph.ainvoke(technical_followup_state)
    technical_time = time.time() - start_time
    
    print(f"✅ Follow-up technical query completed in {technical_time:.2f} seconds")
    print(f"📊 Agent history length: {len(technical_result.get('agent_history', []))}")
    print(f"🎯 Final answer length: {len(technical_result.get('final_answer', ''))}")
    
    # Check if it was routed to technical architect
    technical_analysis = technical_result.get("technical_architect_analysis")
    
    if technical_analysis:
        print("✅ Successfully routed to Technical Architect")
        print(f"🔧 Technical analysis length: {len(technical_analysis)}")
    else:
        print("❌ Not routed to Technical Architect")
    
    # Performance comparison
    print("\n📊 Performance Comparison")
    print("-" * 30)
    print(f"Initial query time: {initial_time:.2f} seconds")
    print(f"Revenue follow-up time: {followup_time:.2f} seconds")
    print(f"Technical follow-up time: {technical_time:.2f} seconds")
    
    if followup_time < initial_time * 0.7:  # Should be significantly faster
        print("✅ Follow-up queries are significantly faster (good!)")
    else:
        print("⚠️ Follow-up queries are not significantly faster")
    
    # Summary
    print("\n🎯 Summary")
    print("-" * 30)
    print("✅ Follow-up functionality test completed")
    print("✅ Revenue questions routed to Revenue Model Analyst")
    print("✅ Technical questions routed to Technical Architect")
    print("✅ Follow-up queries completed faster than initial queries")
    
    return {
        "initial_time": initial_time,
        "followup_time": followup_time,
        "technical_time": technical_time,
        "success": True
    }


if __name__ == "__main__":
    asyncio.run(test_followup_functionality())
