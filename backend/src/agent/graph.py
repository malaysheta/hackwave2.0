import os
import time
import asyncio
import re
import logging
from typing import List, Dict, Any

# Configure logging
logger = logging.getLogger(__name__)

from src.agent.tools_and_schemas import (
    QueryClassification,
    DomainExpertAnalysis,
    UXUISpecialistAnalysis,
    TechnicalArchitectAnalysis,
    RevenueModelAnalystAnalysis,
    ModeratorAggregation,
    DebateAnalysis,
    SupervisorAnalysis,
    QueryType,
    DebateCategory,
)
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from google.genai import Client

from src.agent.state import (
    OverallState,
    DomainExpertState,
    UXUISpecialistState,
    TechnicalArchitectState,
    RevenueModelAnalystState,
    ModeratorState,
    DebateAnalysisState,
    SupervisorState,
    AgentType,
    SupervisorDecision,
)
from src.agent.configuration import Configuration
from src.agent.prompts import (
    get_current_date,
    supervisor_instructions,
    query_classification_instructions,
    domain_expert_instructions,
    ux_ui_specialist_instructions,
    technical_architect_instructions,
    revenue_model_analyst_instructions,
    moderator_aggregation_instructions,
    debate_analysis_instructions,
    final_answer_instructions,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agent.memory import create_memory_manager, create_mongodb_checkpoint_saver, create_langgraph_memory_manager

load_dotenv()

# Lazy initialization of genai_client to avoid blocking operations
_genai_client = None

def get_genai_client():
    """Get or create the genai client instance."""
    global _genai_client
    if _genai_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY is not set")
        _genai_client = Client(api_key=api_key)
    return _genai_client


# Supervisor Node - The main orchestrator
async def supervisor_node(state: OverallState, config: RunnableConfig) -> OverallState:
    """Supervisor node that decides which agent should act next.
    
    This is the main orchestrator that analyzes the current state and determines
    the next action in the workflow.
    
    Args:
        state: Current graph state
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update including supervisor decision and next agent
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Get thread_id from config
    thread_id = configurable.thread_id if hasattr(configurable, 'thread_id') else None
    
    # Initialize memory managers
    memory_manager = create_memory_manager()
    langgraph_memory = create_langgraph_memory_manager()
    
    # Retrieve conversation history and LangGraph memory context if thread_id is available
    conversation_context = ""
    langgraph_context = ""
    if thread_id:
        try:
            # Get regular conversation history
            history = memory_manager.get_conversation_history(thread_id, limit=5)
            if history:
                conversation_context = "\n\nPrevious Conversation Context:\n"
                for entry in reversed(history):  # Show most recent first
                    conversation_context += f"- Step {entry.get('current_step', 'N/A')}: "
                    conversation_context += f"{entry.get('user_query', 'No query')} "
                    conversation_context += f"(Agent: {entry.get('active_agent', 'N/A')})\n"
                    if entry.get('final_answer'):
                        conversation_context += f"  Response: {entry.get('final_answer', '')[:200]}...\n"
            
            # Get LangGraph memory context for follow-up questions
            langgraph_entries = langgraph_memory.get_conversation_context(thread_id, limit=10)
            if langgraph_entries:
                langgraph_context = "\n\nLangGraph Memory Context (for follow-up questions):\n"
                for entry in reversed(langgraph_entries[-5:]):  # Show last 5 entries
                    langgraph_context += f"- User: {entry.get('user_query', 'No query')}\n"
                    langgraph_context += f"  Response: {entry.get('response', '')[:150]}...\n"
                    if entry.get('context'):
                        context_summary = str(entry.get('context'))[:100]
                        langgraph_context += f"  Context: {context_summary}...\n"
        except Exception as e:
            print(f"Warning: Could not retrieve memory context: {e}")
    
    # Initialize Gemini 2.0 Flash for supervisor analysis
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.3,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(SupervisorAnalysis)
    
    # Format the prompt with current state, conversation history, and LangGraph memory context
    current_date = get_current_date()
    formatted_prompt = supervisor_instructions.format(
        user_query=state["user_query"],
        current_step=state.get("current_step", 1),
        max_steps=state.get("max_steps", 10),
        agent_history=state.get("agent_history", []),
        domain_expert_analysis=state.get("domain_expert_analysis", "Not completed"),
        ux_ui_specialist_analysis=state.get("ux_ui_specialist_analysis", "Not completed"),
        technical_architect_analysis=state.get("technical_architect_analysis", "Not completed"),
        revenue_model_analyst_analysis=state.get("revenue_model_analyst_analysis", "Not completed"),
        moderator_aggregation=state.get("moderator_aggregation", "Not completed"),
        debate_resolution=state.get("debate_resolution", "Not applicable"),
        current_date=current_date,
        conversation_context=conversation_context + langgraph_context,
    )
    
    # Get supervisor decision using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history = state.get("agent_history", [])
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "supervisor",
        "decision": result.decision.value,
        "next_agent": result.next_agent.value,
        "reasoning": result.reasoning,
        "timestamp": time.time(),
        "is_followup": len(agent_history) > 0  # Mark as follow-up if there's previous history
    })
    
    # Save conversation memory if thread_id is available
    if thread_id:
        try:
            # Merge current state with updates
            current_state = {**state, **{
                "active_agent": result.next_agent,
                "supervisor_decision": result.decision,
                "supervisor_reasoning": result.reasoning,
                "agent_history": agent_history,
                "current_step": state.get("current_step", 1) + 1,
                "processing_time": time.time() - start_time
            }}
            memory_manager.save_conversation_memory(thread_id, current_state)
        except Exception as e:
            print(f"Warning: Could not save conversation memory: {e}")
    
    return {
        "active_agent": result.next_agent,
        "supervisor_decision": result.decision,
        "supervisor_reasoning": result.reasoning,
        "agent_history": agent_history,
        "current_step": state.get("current_step", 1) + 1,
        "processing_time": time.time() - start_time
    }


# Query Classification Node (now called by Supervisor)
async def classify_query(state: OverallState, config: RunnableConfig) -> OverallState:
    """Classify user queries to determine initial routing.
    
    Args:
        state: Current graph state containing the user query
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update, including query_type and debate_category
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Initialize Gemini 2.0 Flash for query classification
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.3,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(QueryClassification)
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_classification_instructions.format(
        user_query=state["user_query"],
        current_date=current_date,
    )
    
    # Classify the query using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Check if this is a debate (contains debate keywords)
    debate_keywords = ["debate", "conflict", "disagreement", "argument", "dispute", "controversy"]
    is_debate = any(keyword in state["user_query"].lower() for keyword in debate_keywords)
    
    if is_debate:
        return {
            "query_type": QueryType.GENERAL,
            "debate_category": DebateCategory.MODERATOR,
            "processing_time": time.time() - start_time
        }
    
    return {
        "query_type": result.query_type,
        "debate_category": None,
        "processing_time": time.time() - start_time
    }


# Specialist Agent Nodes (now callable by Supervisor)
async def domain_expert_analysis(state: OverallState, config: RunnableConfig) -> OverallState:
    """Domain Expert analysis node.
    
    Args:
        state: Current graph state containing the user query
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update containing domain expert analysis
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Get thread_id from config
    thread_id = configurable.thread_id if hasattr(configurable, 'thread_id') else None
    
    # Initialize memory manager
    memory_manager = create_memory_manager()
    
    # Get LangGraph memory context for deduplication
    langgraph_memory = create_langgraph_memory_manager()
    langgraph_context = langgraph_memory.get_conversation_context(thread_id) if thread_id else []
    
    # Check for duplicate analysis in recent context
    if langgraph_context:
        recent_analyses = [entry.get("response", "") for entry in langgraph_context[-5:]]
        current_query = state["user_query"].lower().strip()
        
        # Check if similar analysis already exists
        for analysis in recent_analyses:
            if (current_query in analysis.lower() or 
                analysis.lower() in current_query or
                self._calculate_similarity(current_query, analysis.lower()) > 0.7):
                logger.info(f"Duplicate analysis detected for query: {state['user_query']}")
                # Return existing analysis instead of generating new one
                return {
                    "domain_expert_analysis": analysis,
                    "agent_history": state.get("agent_history", []),
                    "processing_time": time.time() - start_time
                }
    
    # Initialize Gemini 2.0 Flash for domain expert analysis
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.7,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(DomainExpertAnalysis)
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = domain_expert_instructions.format(
        user_query=state["user_query"],
        current_date=current_date,
    )
    
    # Generate domain expert analysis using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history = state.get("agent_history", [])
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "domain_expert",
        "analysis_completed": True,
        "timestamp": time.time()
    })
    
    # Prepare updated state
    analysis_result = f"""
Domain Analysis: {result.domain_analysis}

Domain Requirements:
{chr(10).join(f"- {req}" for req in result.domain_requirements)}

Domain Concerns:
{chr(10).join(f"- {concern}" for concern in result.domain_concerns)}

Priority Level: {result.priority_level}
        """.strip()
    
    updated_state = {
        "domain_expert_analysis": analysis_result,
        "agent_history": agent_history,
        "processing_time": time.time() - start_time
    }
    
    # Save conversation memory if thread_id is available
    if thread_id:
        try:
            # Merge current state with updates
            current_state = {**state, **updated_state}
            memory_manager.save_conversation_memory(thread_id, current_state)
        except Exception as e:
            print(f"Warning: Could not save conversation memory: {e}")
    
    return updated_state


def _calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using simple word overlap.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    try:
        # Clean and normalize texts
        text1_clean = re.sub(r'[^\w\s]', '', text1.lower())
        text2_clean = re.sub(r'[^\w\s]', '', text2.lower())
        
        # Split into words
        words1 = set(text1_clean.split())
        words2 = set(text2_clean.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
        
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0


async def ux_ui_specialist_analysis(state: OverallState, config: RunnableConfig) -> OverallState:
    """UX/UI Specialist analysis node.
    
    Args:
        state: Current graph state containing the user query
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update containing UX/UI specialist analysis
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Initialize Gemini 2.0 Flash for UX/UI specialist analysis
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.7,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(UXUISpecialistAnalysis)
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = ux_ui_specialist_instructions.format(
        user_query=state["user_query"],
        current_date=current_date,
    )
    
    # Generate UX/UI specialist analysis using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history = state.get("agent_history", [])
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "ux_ui_specialist",
        "analysis_completed": True,
        "timestamp": time.time()
    })
    
    return {
        "ux_ui_specialist_analysis": f"""
UX Analysis: {result.ux_analysis}

UI Requirements:
{chr(10).join(f"- {req}" for req in result.ui_requirements)}

User Experience Concerns:
{chr(10).join(f"- {concern}" for concern in result.user_experience_concerns)}

Accessibility Requirements:
{chr(10).join(f"- {req}" for req in result.accessibility_requirements)}
        """.strip(),
        "agent_history": agent_history,
        "processing_time": time.time() - start_time
    }


async def technical_architect_analysis(state: OverallState, config: RunnableConfig) -> OverallState:
    """Technical Architect analysis node.
    
    Args:
        state: Current graph state containing the user query
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update containing technical architect analysis
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Initialize Gemini 2.0 Flash for technical architect analysis
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.7,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(TechnicalArchitectAnalysis)
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = technical_architect_instructions.format(
        user_query=state["user_query"],
        current_date=current_date,
    )
    
    # Generate technical architect analysis using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history = state.get("agent_history", [])
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "technical_architect",
        "analysis_completed": True,
        "timestamp": time.time()
    })
    
    return {
        "technical_architect_analysis": f"""
Technical Analysis: {result.technical_analysis}

Technical Requirements:
{chr(10).join(f"- {req}" for req in result.technical_requirements)}

Technical Concerns:
{chr(10).join(f"- {concern}" for concern in result.technical_concerns)}

Scalability Considerations:
{chr(10).join(f"- {consideration}" for consideration in result.scalability_considerations)}
        """.strip(),
        "agent_history": agent_history,
        "processing_time": time.time() - start_time
    }


async def revenue_model_analyst_analysis(state: OverallState, config: RunnableConfig) -> OverallState:
    """Revenue Model Analyst analysis node.
    
    Args:
        state: Current graph state containing the user query
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update containing revenue model analyst analysis
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Initialize Gemini 2.0 Flash for revenue model analyst analysis
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.7,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(RevenueModelAnalystAnalysis)
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = revenue_model_analyst_instructions.format(
        user_query=state["user_query"],
        current_date=current_date,
    )
    
    # Generate revenue model analyst analysis using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history = state.get("agent_history", [])
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "revenue_model_analyst",
        "analysis_completed": True,
        "timestamp": time.time()
    })
    
    return {
        "revenue_model_analyst_analysis": f"""
Revenue Analysis: {result.revenue_analysis}

Revenue Requirements:
{chr(10).join(f"- {req}" for req in result.revenue_requirements)}

Revenue Concerns:
{chr(10).join(f"- {concern}" for concern in result.revenue_concerns)}

Monetization Strategies:
{chr(10).join(f"- {strategy}" for strategy in result.monetization_strategies)}

Pricing Considerations:
{chr(10).join(f"- {consideration}" for consideration in result.pricing_considerations)}
        """.strip(),
        "agent_history": agent_history,
        "processing_time": time.time() - start_time
    }


async def analyze_debate(state: OverallState, config: RunnableConfig) -> OverallState:
    """Debate analysis and routing node.
    
    Args:
        state: Current graph state containing the debate content
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update containing debate analysis and routing decision
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Initialize Gemini 2.0 Flash for debate analysis
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.5,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(DebateAnalysis)
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = debate_analysis_instructions.format(
        debate_content=state.get("debate_content", state["user_query"]),
        user_query=state["user_query"],
        current_date=current_date,
    )
    
    # Generate debate analysis using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history = state.get("agent_history", [])
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "debate_analyzer",
        "debate_category": result.debate_category.value,
        "timestamp": time.time()
    })
    
    return {
        "debate_category": result.debate_category,
        "debate_resolution": f"""
Debate Analysis:
- Category: {result.debate_category.value}
- Routing Decision: {result.routing_decision}
- Urgency Level: {result.urgency_level}
- Estimated Resolution Time: {result.estimated_resolution_time}
        """.strip(),
        "agent_history": agent_history,
        "processing_time": time.time() - start_time
    }


async def moderator_aggregation(state: OverallState, config: RunnableConfig) -> OverallState:
    """Moderator/Aggregator analysis node.
    
    Args:
        state: Current graph state containing specialist analyses
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update containing moderator aggregation
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Initialize Gemini 2.0 Flash for moderator aggregation
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.5,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(ModeratorAggregation)
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = moderator_aggregation_instructions.format(
        domain_analysis=state.get("domain_expert_analysis", "No domain analysis provided"),
        ux_analysis=state.get("ux_ui_specialist_analysis", "No UX/UI analysis provided"),
        technical_analysis=state.get("technical_architect_analysis", "No technical analysis provided"),
        revenue_analysis=state.get("revenue_model_analyst_analysis", "No revenue analysis provided"),
        user_query=state["user_query"],
        current_date=current_date,
    )
    
    # Generate moderator aggregation using async execution
    result = await structured_llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history = state.get("agent_history", [])
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "moderator",
        "aggregation_completed": True,
        "timestamp": time.time()
    })
    
    return {
        "moderator_aggregation": f"""
Aggregated Requirements:
{chr(10).join(f"- {req}" for req in result.aggregated_requirements)}

Conflict Resolution:
{result.conflict_resolution if result.conflict_resolution else "No conflicts identified"}

Final Recommendations:
{chr(10).join(f"- {rec}" for rec in result.final_recommendations)}

Implementation Priority:
{chr(10).join(f"- {priority}" for priority in result.implementation_priority)}
        """.strip(),
        "agent_history": agent_history,
        "processing_time": time.time() - start_time
    }


async def finalize_answer(state: OverallState, config: RunnableConfig) -> OverallState:
    """Final answer generation node.
    
    Args:
        state: Current graph state containing all analyses
        config: Configuration for the runnable
        
    Returns:
        Dictionary with state update containing the final answer
    """
    configurable = Configuration.from_runnable_config(config)
    start_time = time.time()
    
    # Check if this is a follow-up question (has agent history)
    agent_history = state.get("agent_history", [])
    is_followup = len(agent_history) > 0
    
    # For follow-up questions, use the direct agent analysis as final answer
    if is_followup:
        # Get the most recent agent analysis
        domain_analysis = state.get("domain_expert_analysis", "")
        ux_analysis = state.get("ux_ui_specialist_analysis", "")
        technical_analysis = state.get("technical_architect_analysis", "")
        revenue_analysis = state.get("revenue_model_analyst_analysis", "")
        moderator_analysis = state.get("moderator_aggregation", "")
        
        # Use the analysis that exists (should be only one for follow-ups)
        final_content = domain_analysis or ux_analysis or technical_analysis or revenue_analysis or moderator_analysis
        
        if final_content:
            # Clean up the content to make it more readable
            final_content = final_content.strip()
            
                # Update agent history
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "finalizer",
        "final_answer_generated": True,
        "is_followup": True,
        "timestamp": time.time()
    })
    
    # Save to LangGraph memory array
    configurable = Configuration.from_runnable_config(config)
    thread_id = configurable.thread_id if hasattr(configurable, 'thread_id') else None
    if thread_id:
        try:
            langgraph_memory = create_langgraph_memory_manager()
            context = {
                "agent_history": agent_history,
                "is_followup": True,
                "processing_time": time.time() - start_time
            }
            langgraph_memory.add_to_memory_array(
                thread_id=thread_id,
                user_query=state["user_query"],
                response=final_content,
                context=context
            )
        except Exception as e:
            print(f"Warning: Could not save to LangGraph memory: {e}")
    
    return {
        "messages": [AIMessage(content=final_content)],
        "final_answer": final_content,
        "agent_history": agent_history,
        "is_complete": True,
        "processing_time": time.time() - start_time
    }
    
    # For new queries, use the normal aggregation process
    # Initialize Gemini 2.0 Flash for final answer generation
    llm = ChatGoogleGenerativeAI(
        model=configurable.model,
        temperature=0.3,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    
    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = final_answer_instructions.format(
        user_query=state["user_query"],
        moderator_aggregation=state.get("moderator_aggregation", "No aggregation available"),
        current_date=current_date,
    )
    
    # Generate final answer using async execution
    result = await llm.ainvoke(formatted_prompt)
    
    # Update agent history
    agent_history.append({
        "step": state.get("current_step", 1),
        "agent": "finalizer",
        "final_answer_generated": True,
        "is_followup": False,
        "timestamp": time.time()
    })
    
    # Save to LangGraph memory array
    configurable = Configuration.from_runnable_config(config)
    thread_id = configurable.thread_id if hasattr(configurable, 'thread_id') else None
    if thread_id:
        try:
            langgraph_memory = create_langgraph_memory_manager()
            context = {
                "agent_history": agent_history,
                "is_followup": False,
                "processing_time": time.time() - start_time,
                "moderator_aggregation": state.get("moderator_aggregation", ""),
                "domain_expert_analysis": state.get("domain_expert_analysis", ""),
                "ux_ui_specialist_analysis": state.get("ux_ui_specialist_analysis", ""),
                "technical_architect_analysis": state.get("technical_architect_analysis", ""),
                "revenue_model_analyst_analysis": state.get("revenue_model_analyst_analysis", "")
            }
            langgraph_memory.add_to_memory_array(
                thread_id=thread_id,
                user_query=state["user_query"],
                response=result.content,
                context=context
            )
        except Exception as e:
            print(f"Warning: Could not save to LangGraph memory: {e}")
    
    return {
        "messages": [AIMessage(content=result.content)],
        "final_answer": result.content,
        "agent_history": agent_history,
        "is_complete": True,
        "processing_time": time.time() - start_time
    }


# Router function for Supervisor-based routing
def supervisor_router(state: OverallState) -> str:
    """Router function that determines the next node based on Supervisor decision.
    
    Args:
        state: Current graph state
        
    Returns:
        String indicating the next node to execute
    """
    # If we have a final answer, we're done
    if state.get("is_complete", False):
        return "finalize_answer"
    
    # If we've exceeded max steps, end
    if state.get("current_step", 1) > state.get("max_steps", 10):
        return "finalize_answer"
    
    # Get the supervisor's decision
    supervisor_decision = state.get("supervisor_decision")
    active_agent = state.get("active_agent")
    
    if not supervisor_decision or not active_agent:
        # Initial state, start with supervisor
        return "supervisor"
    
    # Route based on supervisor decision
    if supervisor_decision == SupervisorDecision.END:
        return "finalize_answer"
    elif supervisor_decision == SupervisorDecision.DEBATE:
        return "analyze_debate"
    elif supervisor_decision == SupervisorDecision.CONTINUE:
        # Route to the specific agent the supervisor chose
        if active_agent == AgentType.DOMAIN_EXPERT:
            return "domain_expert"
        elif active_agent == AgentType.UX_UI_SPECIALIST:
            return "ux_ui_specialist"
        elif active_agent == AgentType.TECHNICAL_ARCHITECT:
            return "technical_architect"
        elif active_agent == AgentType.REVENUE_MODEL_ANALYST:
            return "revenue_model_analyst"
        elif active_agent == AgentType.MODERATOR:
            return "moderator_aggregation"
        else:
            # Default to supervisor for unknown agent
            return "supervisor"
    
    # Default fallback
    return "supervisor"


# New function to detect follow-up queries and route efficiently
def detect_followup_and_route(state: OverallState) -> str:
    """Detect if this is a follow-up query and route directly to the most relevant agent.
    
    Args:
        state: Current graph state
        
    Returns:
        String indicating the next node to execute
    """
    user_query = state.get("user_query", "").lower()
    agent_history = state.get("agent_history", [])
    
    # Check if this is a follow-up (has conversation history)
    is_followup = len(agent_history) > 0
    
    if is_followup:
        # Route directly based on query content for efficiency
        if any(keyword in user_query for keyword in ["revenue", "money", "income", "pricing", "monetization", "profit", "earnings"]):
            return "revenue_model_analyst"
        elif any(keyword in user_query for keyword in ["ui", "ux", "design", "user experience", "interface", "usability", "accessibility"]):
            return "ux_ui_specialist"
        elif any(keyword in user_query for keyword in ["technical", "architecture", "code", "database", "api", "infrastructure", "scalability"]):
            return "technical_architect"
        elif any(keyword in user_query for keyword in ["business", "domain", "market", "industry", "compliance", "regulation"]):
            return "domain_expert"
        else:
            # For complex follow-ups, use moderator
            return "moderator_aggregation"
    
    # For new queries, use the normal supervisor flow
    return "supervisor"


# Create the Supervisor-based Multi-Agent Graph
builder = StateGraph(OverallState, context_schema=Configuration)

# Define all nodes
builder.add_node("supervisor", supervisor_node)
builder.add_node("classify_query", classify_query)
builder.add_node("domain_expert", domain_expert_analysis)
builder.add_node("ux_ui_specialist", ux_ui_specialist_analysis)
builder.add_node("technical_architect", technical_architect_analysis)
builder.add_node("revenue_model_analyst", revenue_model_analyst_analysis)
builder.add_node("analyze_debate", analyze_debate)
builder.add_node("moderator_aggregation", moderator_aggregation)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint
builder.add_edge(START, "classify_query")

# Add conditional edges for follow-up detection and routing
builder.add_conditional_edges(
    "classify_query",
    detect_followup_and_route,  # Use follow-up detection for efficient routing
    ["supervisor", "domain_expert", "ux_ui_specialist", "technical_architect", 
     "revenue_model_analyst", "moderator_aggregation"]
)

# Add conditional edges from supervisor to all possible agents
builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    ["domain_expert", "ux_ui_specialist", "technical_architect", "revenue_model_analyst", 
     "moderator_aggregation", "analyze_debate", "finalize_answer"]
)

# All specialist agents return to supervisor for next decision
builder.add_edge("domain_expert", "supervisor")
builder.add_edge("ux_ui_specialist", "supervisor")
builder.add_edge("technical_architect", "supervisor")
builder.add_edge("revenue_model_analyst", "supervisor")
builder.add_edge("moderator_aggregation", "supervisor")
builder.add_edge("analyze_debate", "supervisor")

# Finalize answer leads to end
builder.add_edge("finalize_answer", END)

# Compile the graph without custom checkpointer (LangGraph API handles persistence)
graph = builder.compile(
    name="supervisor-based-multi-agent-product-requirements"
)
