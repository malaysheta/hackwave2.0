import os
import json
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage as fallback
_in_memory_conversations = {}
_in_memory_context = {}
_in_memory_langgraph_array = []

class LangGraphMemoryManager:
    """
    LangGraph Memory Manager that stores one big array in MongoDB.
    This array contains all conversation context and is used for follow-up questions.
    """
    
    def __init__(self, mongodb_url: str = "mongodb://localhost:27017/Hackwave"):
        """
        Initialize the LangGraph Memory Manager.
        
        Args:
            mongodb_url: MongoDB connection URL
        """
        self.mongodb_url = mongodb_url
        self.client = None
        self.db = None
        self.langgraph_memory = None
        self.array_id = "langgraph_memory_array"  # Single document ID for the array
        
        # Try to connect to MongoDB, fallback to simple memory if fails
        try:
            import pymongo
            from pymongo import MongoClient
            from pymongo.collection import Collection
            from pymongo.database import Database
            
            self._connect()
            self._setup_indexes()
            logger.info("LangGraph Memory Manager initialized successfully")
        except Exception as e:
            logger.warning(f"MongoDB connection failed, using simple memory: {e}")
            self.client = None
            self.db = None
            self.langgraph_memory = None
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.mongodb_url)
            self.db = self.client.get_database()
            self.langgraph_memory = self.db.langgraph_memory
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB for LangGraph Memory: {self.mongodb_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _setup_indexes(self):
        """Setup database indexes for performance."""
        try:
            # Index for the main array document
            self.langgraph_memory.create_index("array_id")
            self.langgraph_memory.create_index("timestamp")
            logger.info("LangGraph Memory indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to setup indexes: {e}")
            raise
    
    def add_to_memory_array(self, thread_id: str, user_query: str, response: str, 
                           context: Dict[str, Any] = None) -> bool:
        """
        Add a new entry to the memory array with deduplication.
        
        Args:
            thread_id: Unique thread identifier
            user_query: User's question/query
            response: Agent's response
            context: Additional context data
        """
        try:
            if self.langgraph_memory is None:
                # Fallback to in-memory storage
                global _in_memory_langgraph_array
                entry = {
                    "thread_id": thread_id,
                    "user_query": user_query,
                    "response": response,
                    "context": context or {},
                    "timestamp": datetime.utcnow().isoformat(),
                    "entry_id": f"{thread_id}_{int(time.time())}"
                }
                _in_memory_langgraph_array.append(entry)
                logger.info(f"Added entry to in-memory LangGraph array for thread {thread_id}")
                return True
            
            # Create the entry
            entry = {
                "thread_id": thread_id,
                "user_query": user_query,
                "response": response,
                "context": context or {},
                "timestamp": datetime.utcnow(),
                "entry_id": f"{thread_id}_{int(time.time())}"
            }
            
            # Get or create the main array document
            array_doc = self.langgraph_memory.find_one({"array_id": self.array_id})
            
            if array_doc:
                # Update existing array
                memory_array = array_doc.get("memory_array", [])
                
                # Check for duplicates (same user_query and similar response)
                is_duplicate = False
                for existing_entry in memory_array[-10:]:  # Check last 10 entries
                    if (existing_entry.get("user_query") == user_query and 
                        self._is_similar_response(existing_entry.get("response", ""), response)):
                        is_duplicate = True
                        logger.info(f"Duplicate entry detected for thread {thread_id}, skipping")
                        break
                
                if not is_duplicate:
                    memory_array.append(entry)
                    
                    # Keep only last 1000 entries to prevent array from getting too large
                    if len(memory_array) > 1000:
                        memory_array = memory_array[-1000:]
                    
                    self.langgraph_memory.update_one(
                        {"array_id": self.array_id},
                        {
                            "$set": {
                                "memory_array": memory_array,
                                "last_updated": datetime.utcnow(),
                                "total_entries": len(memory_array)
                            }
                        }
                    )
                    logger.info(f"Added entry to LangGraph memory array for thread {thread_id}")
                else:
                    logger.info(f"Skipped duplicate entry for thread {thread_id}")
                
            else:
                # Create new array document
                self.langgraph_memory.insert_one({
                    "array_id": self.array_id,
                    "memory_array": [entry],
                    "created_at": datetime.utcnow(),
                    "last_updated": datetime.utcnow(),
                    "total_entries": 1
                })
                logger.info(f"Created new LangGraph memory array with entry for thread {thread_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add entry to memory array: {e}")
            return False
    
    def _is_similar_response(self, response1: str, response2: str, similarity_threshold: float = 0.8) -> bool:
        """
        Check if two responses are similar to detect duplicates.
        
        Args:
            response1: First response
            response2: Second response
            similarity_threshold: Threshold for similarity (0.0 to 1.0)
            
        Returns:
            True if responses are similar enough to be considered duplicates
        """
        try:
            # Simple similarity check based on content overlap
            if not response1 or not response2:
                return False
            
            # Normalize responses
            r1_clean = response1.lower().strip()
            r2_clean = response2.lower().strip()
            
            # If responses are identical, they're duplicates
            if r1_clean == r2_clean:
                return True
            
            # Check for significant content overlap
            words1 = set(r1_clean.split())
            words2 = set(r2_clean.split())
            
            if not words1 or not words2:
                return False
            
            # Calculate Jaccard similarity
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            if union == 0:
                return False
            
            similarity = intersection / union
            
            # Also check if one response contains the other (for partial duplicates)
            if r1_clean in r2_clean or r2_clean in r1_clean:
                return True
            
            return similarity >= similarity_threshold
            
        except Exception as e:
            logger.error(f"Error checking response similarity: {e}")
            return False
    
    def get_memory_context(self, thread_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get memory context for follow-up questions.
        
        Args:
            thread_id: Optional thread ID to filter by
            limit: Maximum number of entries to return
            
        Returns:
            List of memory entries for context
        """
        try:
            if self.langgraph_memory is None:
                # Fallback to in-memory storage
                global _in_memory_langgraph_array
                if thread_id:
                    filtered_array = [entry for entry in _in_memory_langgraph_array 
                                    if entry.get("thread_id") == thread_id]
                else:
                    filtered_array = _in_memory_langgraph_array
                
                # Return recent entries
                return filtered_array[-limit:] if filtered_array else []
            
            # Get from MongoDB
            array_doc = self.langgraph_memory.find_one({"array_id": self.array_id})
            
            if not array_doc:
                logger.info("No LangGraph memory array found")
                return []
            
            memory_array = array_doc.get("memory_array", [])
            
            # Filter by thread_id if provided
            if thread_id:
                memory_array = [entry for entry in memory_array 
                              if entry.get("thread_id") == thread_id]
            
            # Return recent entries
            recent_entries = memory_array[-limit:] if memory_array else []
            
            logger.info(f"Retrieved {len(recent_entries)} memory context entries")
            return recent_entries
            
        except Exception as e:
            logger.error(f"Failed to get memory context: {e}")
            return []
    
    def get_conversation_context(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get conversation context for a specific thread.
        
        Args:
            thread_id: Thread identifier
            limit: Maximum number of entries to return
            
        Returns:
            List of conversation entries for the thread
        """
        try:
            if self.langgraph_memory is None:
                # Fallback to in-memory storage
                global _in_memory_langgraph_array
                thread_entries = [entry for entry in _in_memory_langgraph_array 
                                if entry.get("thread_id") == thread_id]
                return thread_entries[-limit:] if thread_entries else []
            
            # Get from MongoDB
            array_doc = self.langgraph_memory.find_one({"array_id": self.array_id})
            
            if not array_doc:
                return []
            
            memory_array = array_doc.get("memory_array", [])
            thread_entries = [entry for entry in memory_array 
                            if entry.get("thread_id") == thread_id]
            
            return thread_entries[-limit:] if thread_entries else []
            
        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []
    
    def search_memory(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search memory array for relevant entries.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant memory entries
        """
        try:
            if self.langgraph_memory is None:
                # Simple text search in in-memory array
                global _in_memory_langgraph_array
                query_lower = query.lower()
                relevant_entries = []
                
                for entry in _in_memory_langgraph_array:
                    user_query = entry.get("user_query", "").lower()
                    response = entry.get("response", "").lower()
                    
                    if query_lower in user_query or query_lower in response:
                        relevant_entries.append(entry)
                
                return relevant_entries[-limit:] if relevant_entries else []
            
            # MongoDB text search
            array_doc = self.langgraph_memory.find_one({"array_id": self.array_id})
            
            if not array_doc:
                return []
            
            memory_array = array_doc.get("memory_array", [])
            query_lower = query.lower()
            relevant_entries = []
            
            for entry in memory_array:
                user_query = entry.get("user_query", "").lower()
                response = entry.get("response", "").lower()
                
                if query_lower in user_query or query_lower in response:
                    relevant_entries.append(entry)
            
            return relevant_entries[-limit:] if relevant_entries else []
            
        except Exception as e:
            logger.error(f"Failed to search memory: {e}")
            return []
    
    def clear_memory(self, thread_id: str = None) -> bool:
        """
        Clear memory entries.
        
        Args:
            thread_id: Optional thread ID to clear specific thread, None to clear all
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.langgraph_memory is None:
                # Clear in-memory array
                global _in_memory_langgraph_array
                if thread_id:
                    _in_memory_langgraph_array = [entry for entry in _in_memory_langgraph_array 
                                                if entry.get("thread_id") != thread_id]
                else:
                    _in_memory_langgraph_array = []
                logger.info(f"Cleared in-memory LangGraph array")
                return True
            
            # Clear from MongoDB
            if thread_id:
                # Clear specific thread
                array_doc = self.langgraph_memory.find_one({"array_id": self.array_id})
                if array_doc:
                    memory_array = array_doc.get("memory_array", [])
                    filtered_array = [entry for entry in memory_array 
                                    if entry.get("thread_id") != thread_id]
                    
                    self.langgraph_memory.update_one(
                        {"array_id": self.array_id},
                        {
                            "$set": {
                                "memory_array": filtered_array,
                                "last_updated": datetime.utcnow(),
                                "total_entries": len(filtered_array)
                            }
                        }
                    )
                    logger.info(f"Cleared memory for thread {thread_id}")
            else:
                # Clear all memory
                self.langgraph_memory.delete_one({"array_id": self.array_id})
                logger.info("Cleared all LangGraph memory")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory array.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            if self.langgraph_memory is None:
                # Get stats from in-memory array
                global _in_memory_langgraph_array
                thread_count = len(set(entry.get("thread_id") for entry in _in_memory_langgraph_array))
                return {
                    "total_entries": len(_in_memory_langgraph_array),
                    "thread_count": thread_count,
                    "storage_type": "in_memory"
                }
            
            # Get stats from MongoDB
            array_doc = self.langgraph_memory.find_one({"array_id": self.array_id})
            
            if not array_doc:
                return {
                    "total_entries": 0,
                    "thread_count": 0,
                    "storage_type": "mongodb"
                }
            
            memory_array = array_doc.get("memory_array", [])
            thread_count = len(set(entry.get("thread_id") for entry in memory_array))
            
            return {
                "total_entries": len(memory_array),
                "thread_count": thread_count,
                "storage_type": "mongodb",
                "created_at": array_doc.get("created_at"),
                "last_updated": array_doc.get("last_updated")
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("LangGraph Memory Manager connection closed")


class SimpleMemoryManager:
    """
    Simple in-memory memory manager that works without MongoDB.
    This ensures context management works immediately.
    """
    
    def __init__(self):
        """Initialize the simple memory manager."""
        self.conversations = True  # Dummy to satisfy checks
        self.checkpoints = True
        self.memory_context = True
        logger.info("Simple memory manager initialized")
    
    def save_conversation_memory(self, thread_id: str, state: Dict[str, Any]) -> bool:
        """Save conversation memory for a specific thread."""
        try:
            # Prepare conversation data
            conversation_data = {
                "thread_id": thread_id,
                "timestamp": datetime.utcnow().isoformat(),
                "user_query": state.get("user_query", ""),
                "current_step": state.get("current_step", 1),
                "agent_history": state.get("agent_history", []),
                "active_agent": state.get("active_agent", None),
                "supervisor_decision": state.get("supervisor_decision", None),
                "supervisor_reasoning": state.get("supervisor_reasoning", None),
                "is_complete": state.get("is_complete", False),
                "processing_time": state.get("processing_time", 0.0),
                "final_answer": state.get("final_answer", ""),
                "state_snapshot": {
                    "domain_expert_analysis": state.get("domain_expert_analysis"),
                    "ux_ui_specialist_analysis": state.get("ux_ui_specialist_analysis"),
                    "technical_architect_analysis": state.get("technical_architect_analysis"),
                    "revenue_model_analyst_analysis": state.get("revenue_model_analyst_analysis"),
                    "moderator_aggregation": state.get("moderator_aggregation"),
                    "debate_resolution": state.get("debate_resolution"),
                    "final_answer": state.get("final_answer"),
                }
            }
            
            # Store in memory
            if thread_id not in _in_memory_conversations:
                _in_memory_conversations[thread_id] = []
            _in_memory_conversations[thread_id].append(conversation_data)
            
            logger.info(f"Saved conversation memory for thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation memory: {e}")
            return False
    
    def get_conversation_history(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a specific thread."""
        try:
            if thread_id not in _in_memory_conversations:
                return []
            
            history = _in_memory_conversations[thread_id][-limit:]  # Get last N entries
            logger.info(f"Retrieved {len(history)} conversation history entries for thread {thread_id}")
            return history
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []
    
    def get_all_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent conversation history from all threads."""
        try:
            all_history = []
            for thread_id, conversations in _in_memory_conversations.items():
                for conv in conversations[-5:]:  # Get last 5 from each thread
                    all_history.append({
                        "_id": f"{thread_id}_{conv.get('timestamp', '')}",
                        "thread_id": thread_id,
                        "user_query": conv.get("user_query", ""),
                        "final_answer": conv.get("final_answer", ""),
                        "processing_time": conv.get("processing_time", 0),
                        "query_type": "general",
                        "timestamp": conv.get("timestamp", ""),
                        "state_snapshot": conv.get("state_snapshot", {})
                    })
            
            # Sort by timestamp and limit
            all_history.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            all_history = all_history[:limit]
            
            logger.info(f"Retrieved {len(all_history)} conversation history entries from all threads")
            return all_history
            
        except Exception as e:
            logger.error(f"Failed to retrieve all conversation history: {e}")
            return []
    
    def save_memory_context(self, thread_id: str, context: Dict[str, Any]) -> bool:
        """Save memory context for a specific thread."""
        try:
            context_data = {
                "thread_id": thread_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context
            }
            
            _in_memory_context[thread_id] = context_data
            logger.info(f"Saved memory context for thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save memory context: {e}")
            return False
    
    def get_memory_context(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the latest memory context for a specific thread."""
        try:
            if thread_id in _in_memory_context:
                context = _in_memory_context[thread_id]
                logger.info(f"Retrieved memory context for thread {thread_id}")
                return context.get("context")
            else:
                logger.info(f"No memory context found for thread {thread_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve memory context: {e}")
            return None
    
    def get_thread_summary(self, thread_id: str) -> Dict[str, Any]:
        """Get a summary of a conversation thread."""
        try:
            conversation_count = len(_in_memory_conversations.get(thread_id, []))
            latest_conversation = None
            if thread_id in _in_memory_conversations and _in_memory_conversations[thread_id]:
                latest_conversation = _in_memory_conversations[thread_id][-1]
            
            memory_context = self.get_memory_context(thread_id)
            
            summary = {
                "thread_id": thread_id,
                "conversation_count": conversation_count,
                "latest_conversation": latest_conversation,
                "memory_context": memory_context,
                "last_updated": latest_conversation.get("timestamp") if latest_conversation else None
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get thread summary: {e}")
            return {"thread_id": thread_id, "error": str(e)}
    
    def clear_thread_memory(self, thread_id: str) -> bool:
        """Clear all memory for a specific thread."""
        try:
            if thread_id in _in_memory_conversations:
                del _in_memory_conversations[thread_id]
            if thread_id in _in_memory_context:
                del _in_memory_context[thread_id]
            
            logger.info(f"Cleared memory for thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear thread memory: {e}")
            return False
    
    def close(self):
        """Close the memory manager."""
        logger.info("Simple memory manager closed")


class MongoDBMemoryManager:
    """
    MongoDB-based memory manager for LangGraph applications.
    Handles conversation history, state persistence, and checkpoint management.
    """
    
    def __init__(self, mongodb_url: str = "mongodb://localhost:27017/Hackwave"):
        """
        Initialize the MongoDB memory manager.
        
        Args:
            mongodb_url: MongoDB connection URL
        """
        self.mongodb_url = mongodb_url
        self.client = None
        self.db = None
        self.conversations = None
        self.checkpoints = None
        self.memory_context = None
        
        # Try to connect to MongoDB, fallback to simple memory if fails
        try:
            import pymongo
            from pymongo import MongoClient
            from pymongo.collection import Collection
            from pymongo.database import Database
            
            self._connect()
            self._setup_indexes()
            logger.info("MongoDB memory manager initialized successfully")
        except Exception as e:
            logger.warning(f"MongoDB connection failed, using simple memory manager: {e}")
            # Create a simple memory manager as fallback
            self.simple_manager = SimpleMemoryManager()
            self.conversations = self.simple_manager.conversations
            self.checkpoints = self.simple_manager.checkpoints
            self.memory_context = self.simple_manager.memory_context
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.mongodb_url)
            self.db = self.client.get_database()
            self.conversations = self.db.conversations
            self.checkpoints = self.db.checkpoints
            self.memory_context = self.db.memory_context
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.mongodb_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _setup_indexes(self):
        """Setup database indexes for performance."""
        try:
            # Indexes for conversations collection
            self.conversations.create_index("thread_id")
            self.conversations.create_index("timestamp")
            self.conversations.create_index([("thread_id", 1), ("timestamp", -1)])
            
            # Indexes for checkpoints collection
            self.checkpoints.create_index("thread_id")
            self.checkpoints.create_index("checkpoint_id")
            self.checkpoints.create_index([("thread_id", 1), ("timestamp", -1)])
            
            # Indexes for memory context collection
            self.memory_context.create_index("thread_id")
            self.memory_context.create_index("timestamp")
            self.memory_context.create_index([("thread_id", 1), ("timestamp", -1)])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to setup indexes: {e}")
            raise
    
    def _serialize_enum(self, obj):
        """Convert enum objects to strings for MongoDB serialization."""
        if hasattr(obj, 'value'):
            return obj.value
        return obj
    
    def _serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize state for MongoDB storage."""
        serialized = {}
        for key, value in state.items():
            if isinstance(value, dict):
                serialized[key] = self._serialize_state(value)
            elif isinstance(value, list):
                serialized[key] = [self._serialize_enum(item) if hasattr(item, 'value') else item for item in value]
            else:
                serialized[key] = self._serialize_enum(value)
        return serialized
    
    def save_conversation_memory(self, thread_id: str, state: Dict[str, Any]) -> bool:
        """Save conversation memory for a specific thread."""
        # If MongoDB is not available, use simple manager
        if hasattr(self, 'simple_manager'):
            return self.simple_manager.save_conversation_memory(thread_id, state)
        
        try:
            # Serialize state for MongoDB storage
            serialized_state = self._serialize_state(state)
            
            # Prepare conversation data
            conversation_data = {
                "thread_id": thread_id,
                "timestamp": datetime.utcnow(),
                "user_query": serialized_state.get("user_query", ""),
                "current_step": serialized_state.get("current_step", 1),
                "agent_history": serialized_state.get("agent_history", []),
                "active_agent": serialized_state.get("active_agent", None),
                "supervisor_decision": serialized_state.get("supervisor_decision", None),
                "supervisor_reasoning": serialized_state.get("supervisor_reasoning", None),
                "is_complete": serialized_state.get("is_complete", False),
                "processing_time": serialized_state.get("processing_time", 0.0),
                "final_answer": serialized_state.get("final_answer", ""),
                "state_snapshot": {
                    "domain_expert_analysis": serialized_state.get("domain_expert_analysis"),
                    "ux_ui_specialist_analysis": serialized_state.get("ux_ui_specialist_analysis"),
                    "technical_architect_analysis": serialized_state.get("technical_architect_analysis"),
                    "revenue_model_analyst_analysis": serialized_state.get("revenue_model_analyst_analysis"),
                    "moderator_aggregation": serialized_state.get("moderator_aggregation"),
                    "debate_resolution": serialized_state.get("debate_resolution"),
                    "final_answer": serialized_state.get("final_answer"),
                }
            }
            
            # Insert into conversations collection
            result = self.conversations.insert_one(conversation_data)
            logger.info(f"Saved conversation memory for thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation memory: {e}")
            return False
    
    def get_conversation_history(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a specific thread."""
        # If MongoDB is not available, use simple manager
        if hasattr(self, 'simple_manager'):
            return self.simple_manager.get_conversation_history(thread_id, limit)
        
        try:
            if self.conversations is None:
                logger.error("Conversations collection not initialized")
                return []
                
            cursor = self.conversations.find(
                {"thread_id": thread_id},
                {"_id": 0}  # Exclude MongoDB _id field
            ).sort("timestamp", -1).limit(limit)
            
            history = list(cursor)
            logger.info(f"Retrieved {len(history)} conversation history entries for thread {thread_id}")
            return history
            
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []
    
    def get_all_conversation_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent conversation history from all threads."""
        # If MongoDB is not available, use simple manager
        if hasattr(self, 'simple_manager'):
            return self.simple_manager.get_all_conversation_history(limit)
        
        try:
            if self.conversations is None:
                logger.error("Conversations collection not initialized")
                return []
                
            cursor = self.conversations.find(
                {},
                {"_id": 1, "thread_id": 1, "user_query": 1, "final_answer": 1, 
                 "processing_time": 1, "query_type": 1, "timestamp": 1, 
                 "state_snapshot": 1}
            ).sort("timestamp", -1).limit(limit)
            
            history = list(cursor)
            logger.info(f"Retrieved {len(history)} conversation history entries from all threads")
            return history
            
        except Exception as e:
            logger.error(f"Failed to retrieve all conversation history: {e}")
            return []
    
    def save_memory_context(self, thread_id: str, context: Dict[str, Any]) -> bool:
        """Save memory context for a specific thread."""
        # If MongoDB is not available, use simple manager
        if hasattr(self, 'simple_manager'):
            return self.simple_manager.save_memory_context(thread_id, context)
        
        try:
            if self.memory_context is None:
                logger.error("Memory context collection not initialized")
                return False
                
            context_data = {
                "thread_id": thread_id,
                "timestamp": datetime.utcnow(),
                "context": context
            }
            
            result = self.memory_context.insert_one(context_data)
            logger.info(f"Saved memory context for thread {thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save memory context: {e}")
            return False
    
    def get_memory_context(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve the latest memory context for a specific thread."""
        # If MongoDB is not available, use simple manager
        if hasattr(self, 'simple_manager'):
            return self.simple_manager.get_memory_context(thread_id)
        
        try:
            if self.memory_context is None:
                logger.error("Memory context collection not initialized")
                return None
                
            context = self.memory_context.find_one(
                {"thread_id": thread_id},
                {"_id": 0, "context": 1}
            )
            
            if context:
                logger.info(f"Retrieved memory context for thread {thread_id}")
                return context.get("context")
            else:
                logger.info(f"No memory context found for thread {thread_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve memory context: {e}")
            return None
    
    def get_thread_summary(self, thread_id: str) -> Dict[str, Any]:
        """Get a summary of a conversation thread."""
        # If MongoDB is not available, use simple manager
        if hasattr(self, 'simple_manager'):
            return self.simple_manager.get_thread_summary(thread_id)
        
        try:
            if self.conversations is None:
                logger.error("Conversations collection not initialized")
                return {"thread_id": thread_id, "error": "Database not connected"}
            
            # Get conversation count
            conversation_count = self.conversations.count_documents({"thread_id": thread_id})
            
            # Get latest conversation
            latest_conversation = self.conversations.find_one(
                {"thread_id": thread_id},
                sort=[("timestamp", -1)]
            )
            
            # Get memory context
            memory_context = self.get_memory_context(thread_id)
            
            summary = {
                "thread_id": thread_id,
                "conversation_count": conversation_count,
                "latest_conversation": latest_conversation,
                "memory_context": memory_context,
                "last_updated": latest_conversation.get("timestamp") if latest_conversation else None
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get thread summary: {e}")
            return {"thread_id": thread_id, "error": str(e)}
    
    def clear_thread_memory(self, thread_id: str) -> bool:
        """Clear all memory for a specific thread."""
        # If MongoDB is not available, use simple manager
        if hasattr(self, 'simple_manager'):
            return self.simple_manager.clear_thread_memory(thread_id)
        
        try:
            if (self.conversations is None or self.checkpoints is None or self.memory_context is None):
                logger.error("Database collections not initialized")
                return False
                
            # Delete from all collections
            conversations_result = self.conversations.delete_many({"thread_id": thread_id})
            checkpoints_result = self.checkpoints.delete_many({"thread_id": thread_id})
            memory_result = self.memory_context.delete_many({"thread_id": thread_id})
            
            logger.info(f"Cleared memory for thread {thread_id}: "
                       f"{conversations_result.deleted_count} conversations, "
                       f"{checkpoints_result.deleted_count} checkpoints, "
                       f"{memory_result.deleted_count} memory contexts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear thread memory: {e}")
            return False
    
    def close(self):
        """Close the MongoDB connection."""
        if hasattr(self, 'simple_manager'):
            self.simple_manager.close()
        elif self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


class MongoDBCheckpointSaver:
    """
    MongoDB-based checkpoint saver for LangGraph.
    Extends the base checkpoint saver to use MongoDB for persistence.
    """
    
    def __init__(self, mongodb_url: str = "mongodb://localhost:27017/Hackwave"):
        """
        Initialize the MongoDB checkpoint saver.
        
        Args:
            mongodb_url: MongoDB connection URL
        """
        self.mongodb_url = mongodb_url
        self.client = None
        self.db = None
        self.checkpoints = None
        
        try:
            import pymongo
            from pymongo import MongoClient
            from pymongo.collection import Collection
            from pymongo.database import Database
            
            self._connect()
            self._setup_indexes()
        except Exception as e:
            logger.warning(f"MongoDB checkpoint connection failed: {e}")
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.mongodb_url)
            self.db = self.client.get_database()
            self.checkpoints = self.db.checkpoints
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB for checkpoints: {self.mongodb_url}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB for checkpoints: {e}")
            raise
    
    def _setup_indexes(self):
        """Setup database indexes for checkpoints."""
        try:
            self.checkpoints.create_index("thread_id")
            self.checkpoints.create_index("checkpoint_id")
            self.checkpoints.create_index([("thread_id", 1), ("timestamp", -1)])
            logger.info("Checkpoint indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to setup checkpoint indexes: {e}")
            raise
    
    def get(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get a checkpoint by thread_id."""
        try:
            if self.checkpoints is None:
                return None
                
            thread_id = config.get("configurable", {}).get("thread_id")
            if not thread_id:
                return None
            
            checkpoint = self.checkpoints.find_one(
                {"thread_id": thread_id},
                sort=[("timestamp", -1)]
            )
            
            if checkpoint:
                logger.info(f"Retrieved checkpoint for thread {thread_id}")
                return checkpoint.get("checkpoint_data")
            else:
                logger.info(f"No checkpoint found for thread {thread_id}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get checkpoint: {e}")
            return None
    
    def put(self, config: Dict[str, Any], checkpoint: Dict[str, Any]) -> None:
        """Save a checkpoint."""
        try:
            if self.checkpoints is None:
                return
                
            thread_id = config.get("configurable", {}).get("thread_id")
            if not thread_id:
                logger.warning("No thread_id provided for checkpoint")
                return
            
            checkpoint_data = {
                "thread_id": thread_id,
                "checkpoint_id": f"{thread_id}_{int(time.time())}",
                "timestamp": datetime.utcnow(),
                "checkpoint_data": checkpoint
            }
            
            result = self.checkpoints.insert_one(checkpoint_data)
            logger.info(f"Saved checkpoint for thread {thread_id}")
            
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB checkpoint connection closed")


def create_mongodb_checkpoint_saver(mongodb_url: str = "mongodb://localhost:27017/Hackwave"):
    """Factory function to create a MongoDB checkpoint saver."""
    return MongoDBCheckpointSaver(mongodb_url)


def create_memory_manager(mongodb_url: str = "mongodb://localhost:27017/Hackwave"):
    """Factory function to create a MongoDB memory manager."""
    return MongoDBMemoryManager(mongodb_url)


def create_langgraph_memory_manager(mongodb_url: str = "mongodb://localhost:27017/Hackwave"):
    """Factory function to create a LangGraph Memory Manager."""
    return LangGraphMemoryManager(mongodb_url)
