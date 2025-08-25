# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
import time
import asyncio
import json
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import FastAPI, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from src.agent.graph import graph
from src.agent.state import OverallState, QueryType, DebateCategory, AgentType, SupervisorDecision
from src.agent.memory import create_langgraph_memory_manager


# Define request/response models
class ProductRequirementsRequest(BaseModel):
    query: str
    query_type: Optional[str] = None
    debate_content: Optional[str] = None
    thread_id: Optional[str] = None  # Add thread_id for context persistence


class ProductRequirementsResponse(BaseModel):
    answer: str
    processing_time: float
    query_type: str
    debate_category: Optional[str] = None
    domain_analysis: Optional[str] = None
    ux_analysis: Optional[str] = None
    technical_analysis: Optional[str] = None
    moderator_aggregation: Optional[str] = None
    debate_resolution: Optional[str] = None
    agent_history: Optional[list] = None
    supervisor_reasoning: Optional[str] = None
    is_followup: Optional[bool] = None


# Define the FastAPI app
app = FastAPI(
    title="Supervisor-Based Multi-Agent Product Requirements Refinement System",
    description="A sophisticated supervisor-based multi-agent AI system for refining product requirements with dynamic routing and debate handling capabilities",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_frontend_router(build_dir="../frontend/dist"):
    """Creates a router to serve the React frontend.

    Args:
        build_dir: Path to the React build directory relative to this file.

    Returns:
        A Starlette application serving the frontend.
    """
    build_path = pathlib.Path(__file__).parent.parent.parent / build_dir

    if not build_path.is_dir() or not (build_path / "index.html").is_file():
        print(
            f"WARN: Frontend build directory not found or incomplete at {build_path}. Serving frontend will likely fail."
        )
        # Return a dummy router if build isn't ready
        from starlette.routing import Route

        async def dummy_frontend(request):
            return Response(
                "Frontend not built. Run 'npm run build' in the frontend directory.",
                media_type="text/plain",
                status_code=503,
            )

        return Route("/{path:path}", endpoint=dummy_frontend)

    return StaticFiles(directory=build_path, html=True)


async def stream_graph_execution(initial_state: OverallState, thread_id: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Stream the graph execution with real-time updates for Supervisor-based architecture."""
    
    try:
        # Prepare configuration with thread_id for context
        config = {}
        if thread_id:
            config = {
                "configurable": {
                    "thread_id": thread_id,
                    "model": "gemini-2.0-flash",
                    "max_debate_resolution_time": 120,
                    "enable_parallel_processing": True
                }
            }
        
        # Run the graph and capture results
        result = await graph.ainvoke(initial_state, config)
        
        # Stream supervisor decisions and agent activities
        agent_history = result.get("agent_history", [])
        
        for entry in agent_history:
            await asyncio.sleep(0.3)  # Simulate processing time
            
            if entry.get("agent") == "supervisor":
                yield f"data: {json.dumps({'type': 'supervisor_decision', 'content': entry.get('reasoning', 'Supervisor analyzing...')})}\n\n"
            elif entry.get("agent") == "domain_expert":
                yield f"data: {json.dumps({'type': 'domain_expert', 'content': result.get('domain_expert_analysis', 'Domain analysis completed')})}\n\n"
            elif entry.get("agent") == "ux_ui_specialist":
                yield f"data: {json.dumps({'type': 'ux_ui_specialist', 'content': result.get('ux_ui_specialist_analysis', 'UX/UI analysis completed')})}\n\n"
            elif entry.get("agent") == "technical_architect":
                yield f"data: {json.dumps({'type': 'technical_architect', 'content': result.get('technical_architect_analysis', 'Technical analysis completed')})}\n\n"
            elif entry.get("agent") == "revenue_model_analyst":
                yield f"data: {json.dumps({'type': 'revenue_model_analyst', 'content': result.get('revenue_model_analyst_analysis', 'Revenue analysis completed')})}\n\n"
            elif entry.get("agent") == "moderator":
                yield f"data: {json.dumps({'type': 'moderator_aggregation', 'content': result.get('moderator_aggregation', 'Moderator aggregation completed')})}\n\n"
            elif entry.get("agent") == "debate_analyzer":
                yield f"data: {json.dumps({'type': 'debate_analysis', 'content': result.get('debate_resolution', 'Debate analysis completed')})}\n\n"
            elif entry.get("agent") == "finalizer":
                yield f"data: {json.dumps({'type': 'final_answer', 'content': result.get('final_answer', 'Final answer generated')})}\n\n"
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
        
    except Exception as e:
        print(f"Error in streaming: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"


# API Endpoints
@app.post("/api/refine-requirements", response_model=ProductRequirementsResponse)
async def refine_product_requirements(request: ProductRequirementsRequest):
    """
    Refine product requirements using the supervisor-based multi-agent system.
    
    This endpoint processes product requirement queries through a Supervisor that coordinates:
    - Domain Expert: Analyzes business logic and domain-specific requirements
    - UX/UI Specialist: Handles user experience and interface design requirements
    - Technical Architect: Manages technical architecture and implementation requirements
    - Revenue Model Analyst: Analyzes revenue models and monetization strategies
    - Moderator/Aggregator: Consolidates feedback and resolves conflicts
    
    The Supervisor dynamically routes queries and handles debate resolution efficiently.
    """
    try:
        start_time = time.time()
        
        # Prepare the initial state with Supervisor-related fields
        initial_state: OverallState = {
            "messages": [HumanMessage(content=request.query)],
            "user_query": request.query,
            "query_type": QueryType.GENERAL,  # Will be determined by classify_query node
            "debate_category": None,
            "domain_expert_analysis": None,
            "ux_ui_specialist_analysis": None,
            "technical_architect_analysis": None,
            "revenue_model_analyst_analysis": None,
            "moderator_aggregation": None,
            "debate_resolution": None,
            "final_answer": None,
            "processing_time": 0.0,
            # Supervisor-related fields
            "active_agent": None,
            "supervisor_decision": None,
            "supervisor_reasoning": None,
            "agent_history": [],
            "current_step": 1,
            "max_steps": 10,
            "is_complete": False
        }
        
        # If debate content is provided, add it to the state
        if request.debate_content:
            initial_state["debate_content"] = request.debate_content
            initial_state["debate_category"] = DebateCategory.MODERATOR
        
        # Prepare configuration with thread_id for context
        config = {}
        if request.thread_id:
            config = {
                "configurable": {
                    "thread_id": request.thread_id,
                    "model": "gemini-2.0-flash",
                    "max_debate_resolution_time": 120,
                    "enable_parallel_processing": True
                }
            }
        
        # Run the graph using async execution
        result = await graph.ainvoke(initial_state, config)
        
        # Calculate total processing time
        total_time = time.time() - start_time
        
        # Extract the final answer from messages
        final_answer = ""
        if result.get("messages"):
            for message in result["messages"]:
                if hasattr(message, 'content'):
                    final_answer = message.content
                    break
        
        # Check if this was a follow-up query
        agent_history = result.get("agent_history", [])
        is_followup = len(agent_history) > 0
        
        # Check if any agent history entry indicates it was a follow-up
        for entry in agent_history:
            if entry.get("is_followup"):
                is_followup = True
                break
        
        return ProductRequirementsResponse(
            answer=final_answer or result.get("final_answer", "No answer generated"),
            processing_time=total_time,
            query_type=result.get("query_type", QueryType.GENERAL).value,
            debate_category=result.get("debate_category", DebateCategory.MODERATOR).value if result.get("debate_category") else None,
            domain_analysis=result.get("domain_expert_analysis"),
            ux_analysis=result.get("ux_ui_specialist_analysis"),
            technical_analysis=result.get("technical_architect_analysis"),
            moderator_aggregation=result.get("moderator_aggregation"),
            debate_resolution=result.get("debate_resolution"),
            agent_history=result.get("agent_history"),
            supervisor_reasoning=result.get("supervisor_reasoning"),
            is_followup=is_followup
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/api/refine-requirements/stream")
async def refine_product_requirements_stream(request: ProductRequirementsRequest):
    """
    Stream product requirements refinement using Server-Sent Events.
    
    This endpoint provides real-time streaming of the supervisor-based multi-agent analysis process,
    allowing the frontend to display progress updates as the Supervisor coordinates each specialist.
    """
    try:
        # Prepare the initial state with Supervisor-related fields
        initial_state: OverallState = {
            "messages": [HumanMessage(content=request.query)],
            "user_query": request.query,
            "query_type": QueryType.GENERAL,  # Will be determined by classify_query node
            "debate_category": None,
            "domain_expert_analysis": None,
            "ux_ui_specialist_analysis": None,
            "technical_architect_analysis": None,
            "revenue_model_analyst_analysis": None,
            "moderator_aggregation": None,
            "debate_resolution": None,
            "final_answer": None,
            "processing_time": 0.0,
            # Supervisor-related fields
            "active_agent": None,
            "supervisor_decision": None,
            "supervisor_reasoning": None,
            "agent_history": [],
            "current_step": 1,
            "max_steps": 10,
            "is_complete": False
        }
        
        # If debate content is provided, add it to the state
        if request.debate_content:
            initial_state["debate_content"] = request.debate_content
            initial_state["debate_category"] = DebateCategory.MODERATOR
        
        # Pass thread_id to the streaming function for context
        return StreamingResponse(
            stream_graph_execution(initial_state, request.thread_id),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/api/health")
async def health_check():
    """Health check endpoint for the supervisor-based multi-agent system."""
    return {
        "status": "healthy",
        "system": "Supervisor-Based Multi-Agent Product Requirements Refinement System",
        "version": "2.0.0",
        "architecture": "Supervisor-based with dynamic routing",
        "agents": [
            "Supervisor (Orchestrator)",
            "Domain Expert",
            "UX/UI Specialist", 
            "Technical Architect",
            "Revenue Model Analyst",
            "Moderator/Aggregator",
            "Debate Handler"
        ]
    }


@app.get("/api/agents")
async def get_agents_info():
    """Get information about available specialist agents and the Supervisor."""
    return {
        "agents": {
            "supervisor": {
                "name": "Supervisor (Orchestrator)",
                "description": "Coordinates and directs the workflow by deciding which specialist agent should act next",
                "expertise": ["Workflow Orchestration", "Dynamic Routing", "Decision Making", "Agent Coordination", "State Management"]
            },
            "domain_expert": {
                "name": "Domain Expert",
                "description": "Analyzes business logic, industry standards, compliance requirements, and domain-specific knowledge",
                "expertise": ["Business Logic", "Industry Standards", "Compliance", "Market Analysis", "Domain Knowledge"]
            },
            "ux_ui_specialist": {
                "name": "UX/UI Specialist", 
                "description": "Analyzes user experience requirements, interface design, accessibility, and usability",
                "expertise": ["User Experience", "Interface Design", "Accessibility", "Usability", "User Research"]
            },
            "technical_architect": {
                "name": "Technical Architect",
                "description": "Analyzes technical architecture, system design, scalability, and implementation requirements",
                "expertise": ["System Architecture", "Technology Stack", "Scalability", "Performance", "Security"]
            },
            "revenue_model_analyst": {
                "name": "Revenue Model Analyst",
                "description": "Analyzes revenue models, monetization strategies, pricing, and financial sustainability",
                "expertise": ["Revenue Models", "Monetization", "Pricing Strategies", "Business Models", "Financial Analysis"]
            },
            "moderator": {
                "name": "Moderator/Aggregator",
                "description": "Aggregates feedback from specialists and resolves conflicts to create unified requirements",
                "expertise": ["Conflict Resolution", "Requirements Aggregation", "Priority Setting", "Stakeholder Coordination"]
            },
            "debate_handler": {
                "name": "Debate Handler",
                "description": "Analyzes and routes debates to appropriate specialists for efficient resolution (under 2 minutes)",
                "expertise": ["Debate Analysis", "Conflict Routing", "Efficiency Optimization", "Specialist Coordination"]
            }
        }
    }


@app.get("/api/conversation-history/{thread_id}")
async def get_conversation_history(thread_id: str, limit: int = 10):
    """Get conversation history for a specific thread."""
    try:
        from src.agent.memory import create_memory_manager
        
        memory_manager = create_memory_manager()
        
        # Check if memory manager is properly initialized
        if not memory_manager.conversations:
            memory_manager.close()
            return {
                "history": [],
                "memory_context": None,
                "thread_summary": {"thread_id": thread_id, "error": "Database not connected"},
                "error": "Database connection issue"
            }
        
        history = memory_manager.get_conversation_history(thread_id, limit=limit)
        memory_context = memory_manager.get_memory_context(thread_id)
        thread_summary = memory_manager.get_thread_summary(thread_id)
        memory_manager.close()
        
        return {
            "history": history,
            "memory_context": memory_context,
            "thread_summary": thread_summary
        }
    except Exception as e:
        return {
            "history": [],
            "memory_context": None,
            "thread_summary": {"thread_id": thread_id, "error": str(e)},
            "error": f"Error retrieving conversation history: {str(e)}"
        }


@app.get("/api/conversation-history/default")
async def get_default_conversation_history(limit: int = 20):
    """Get recent conversation history from any thread for display."""
    try:
        from src.agent.memory import create_memory_manager
        
        memory_manager = create_memory_manager()
        
        # Check if memory manager is properly initialized
        if not memory_manager.conversations:
            memory_manager.close()
            return []
        
        # Get recent conversations from all threads using the new method
        recent_conversations = memory_manager.get_all_conversation_history(limit=limit)
        
        memory_manager.close()
        
        return recent_conversations
    except Exception as e:
        print(f"Error retrieving default conversation history: {str(e)}")
        return []


@app.get("/api/thread-context/{thread_id}")
async def get_thread_context(thread_id: str):
    """Get comprehensive context for a specific thread including history, memory, and summary."""
    try:
        from src.agent.memory import create_memory_manager
        
        memory_manager = create_memory_manager()
        
        # Get all context data with error handling
        try:
            history = memory_manager.get_conversation_history(thread_id, limit=20)
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            history = []
            
        try:
            memory_context = memory_manager.get_memory_context(thread_id)
        except Exception as e:
            print(f"Error getting memory context: {e}")
            memory_context = None
            
        try:
            thread_summary = memory_manager.get_thread_summary(thread_id)
        except Exception as e:
            print(f"Error getting thread summary: {e}")
            thread_summary = {"thread_id": thread_id, "error": str(e)}
        
        memory_manager.close()
        
        # Check if we have any context
        has_context = len(history) > 0 or memory_context is not None
        
        return {
            "thread_id": thread_id,
            "history": history,
            "memory_context": memory_context,
            "thread_summary": thread_summary,
            "has_context": has_context,
            "conversation_count": len(history)
        }
    except Exception as e:
        print(f"Error in thread-context endpoint: {e}")
        return {
            "thread_id": thread_id,
            "history": [],
            "memory_context": None,
            "thread_summary": {"thread_id": thread_id, "error": str(e)},
            "has_context": False,
            "conversation_count": 0,
            "error": f"Error retrieving thread context: {str(e)}"
        }


@app.delete("/api/conversation-history/{thread_id}")
async def clear_conversation_history(thread_id: str):
    """Clear conversation history for a specific thread."""
    try:
        from src.agent.memory import create_memory_manager
        
        memory_manager = create_memory_manager()
        success = memory_manager.clear_thread_memory(thread_id)
        memory_manager.close()
        
        if success:
            return {"message": f"Conversation history cleared for thread {thread_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear conversation history")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversation history: {str(e)}")


@app.get("/api/context/{thread_id}")
async def get_context_for_thread(thread_id: str):
    """Get comprehensive context for a specific thread with enhanced conversation history."""
    try:
        from src.agent.memory import create_memory_manager
        
        memory_manager = create_memory_manager()
        
        # Check if memory manager is properly initialized
        if memory_manager.conversations is None:
            memory_manager.close()
            return {
                "thread_id": thread_id,
                "has_context": False,
                "conversation_count": 0,
                "history": [],
                "memory_context": None,
                "thread_summary": {"thread_id": thread_id, "error": "Database not connected"},
                "latest_conversation": None,
                "error": "Database connection issue"
            }
        
        # Get conversation history
        history = memory_manager.get_conversation_history(thread_id, limit=50)
        
        # Get memory context
        memory_context = memory_manager.get_memory_context(thread_id)
        
        # Get thread summary
        thread_summary = memory_manager.get_thread_summary(thread_id)
        
        memory_manager.close()
        
        # Process history to create a more structured context
        processed_history = []
        for entry in history:
            processed_entry = {
                "timestamp": entry.get("timestamp"),
                "user_query": entry.get("user_query"),
                "final_answer": entry.get("final_answer"),
                "processing_time": entry.get("processing_time"),
                "query_type": entry.get("query_type"),
                "active_agent": entry.get("active_agent"),
                "supervisor_decision": entry.get("supervisor_decision"),
                "supervisor_reasoning": entry.get("supervisor_reasoning"),
                "state_snapshot": entry.get("state_snapshot", {}),
                "is_followup": entry.get("is_followup", False)
            }
            processed_history.append(processed_entry)
        
        # Check if we have any context
        has_context = len(processed_history) > 0 or memory_context is not None
        
        return {
            "thread_id": thread_id,
            "has_context": has_context,
            "conversation_count": len(processed_history),
            "history": processed_history,
            "memory_context": memory_context,
            "thread_summary": thread_summary,
            "latest_conversation": processed_history[0] if processed_history else None
        }
    except Exception as e:
        # Return a safe response instead of raising an exception
        return {
            "thread_id": thread_id,
            "has_context": False,
            "conversation_count": 0,
            "history": [],
            "memory_context": None,
            "thread_summary": {"thread_id": thread_id, "error": str(e)},
            "latest_conversation": None,
            "error": f"Error retrieving context: {str(e)}"
        }


@app.post("/api/context/check")
async def check_context_availability(request: ProductRequirementsRequest):
    """Check if a thread has existing context before processing."""
    try:
        if not request.thread_id:
            return {"has_context": False, "thread_id": None}
        
        from src.agent.memory import create_memory_manager
        
        memory_manager = create_memory_manager()
        
        # Check if memory manager is properly initialized
        if not memory_manager.conversations:
            memory_manager.close()
            return {
                "has_context": False,
                "thread_id": request.thread_id,
                "conversation_count": 0,
                "has_memory_context": False,
                "error": "Database not connected"
            }
        
        # Check if thread has any history
        history = memory_manager.get_conversation_history(request.thread_id, limit=1)
        memory_context = memory_manager.get_memory_context(request.thread_id)
        
        memory_manager.close()
        
        has_context = len(history) > 0 or memory_context is not None
        
        return {
            "has_context": has_context,
            "thread_id": request.thread_id,
            "conversation_count": len(history),
            "has_memory_context": memory_context is not None
        }
    except Exception as e:
        return {
            "has_context": False,
            "thread_id": request.thread_id,
            "conversation_count": 0,
            "has_memory_context": False,
            "error": f"Error checking context: {str(e)}"
        }


@app.get("/api/langgraph-memory/{thread_id}")
async def get_langgraph_memory(thread_id: str, limit: int = 50):
    """Get LangGraph memory context for a specific thread."""
    try:
        langgraph_memory = create_langgraph_memory_manager()
        
        # Get memory context
        memory_entries = langgraph_memory.get_conversation_context(thread_id, limit=limit)
        
        # Get memory statistics
        memory_stats = langgraph_memory.get_memory_stats()
        
        langgraph_memory.close()
        
        return {
            "thread_id": thread_id,
            "memory_entries": memory_entries,
            "memory_stats": memory_stats,
            "entry_count": len(memory_entries)
        }
    except Exception as e:
        return {
            "thread_id": thread_id,
            "memory_entries": [],
            "memory_stats": {"error": str(e)},
            "entry_count": 0,
            "error": f"Error retrieving LangGraph memory: {str(e)}"
        }


@app.get("/api/langgraph-memory/search/{thread_id}")
async def search_langgraph_memory(thread_id: str, query: str, limit: int = 20):
    """Search LangGraph memory for relevant entries."""
    try:
        langgraph_memory = create_langgraph_memory_manager()
        
        # Search memory
        search_results = langgraph_memory.search_memory(query, limit=limit)
        
        langgraph_memory.close()
        
        return {
            "thread_id": thread_id,
            "search_query": query,
            "search_results": search_results,
            "result_count": len(search_results)
        }
    except Exception as e:
        return {
            "thread_id": thread_id,
            "search_query": query,
            "search_results": [],
            "result_count": 0,
            "error": f"Error searching LangGraph memory: {str(e)}"
        }


@app.delete("/api/langgraph-memory/{thread_id}")
async def clear_langgraph_memory(thread_id: str):
    """Clear LangGraph memory for a specific thread."""
    try:
        langgraph_memory = create_langgraph_memory_manager()
        
        # Clear memory
        success = langgraph_memory.clear_memory(thread_id)
        
        langgraph_memory.close()
        
        return {
            "thread_id": thread_id,
            "cleared": success,
            "message": "Memory cleared successfully" if success else "Failed to clear memory"
        }
    except Exception as e:
        return {
            "thread_id": thread_id,
            "cleared": False,
            "error": f"Error clearing LangGraph memory: {str(e)}"
        }


@app.get("/api/langgraph-memory/stats")
async def get_langgraph_memory_stats():
    """Get overall LangGraph memory statistics."""
    try:
        langgraph_memory = create_langgraph_memory_manager()
        
        # Get memory statistics
        memory_stats = langgraph_memory.get_memory_stats()
        
        langgraph_memory.close()
        
        return {
            "memory_stats": memory_stats
        }
    except Exception as e:
        return {
            "memory_stats": {"error": str(e)},
            "error": f"Error retrieving LangGraph memory stats: {str(e)}"
        }


# Mount the frontend under /app to not conflict with the LangGraph API routes
app.mount(
    "/app",
    create_frontend_router(),
    name="frontend",
)
