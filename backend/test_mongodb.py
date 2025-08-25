#!/usr/bin/env python3
"""
Simple MongoDB connection test script.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from agent.memory import create_memory_manager
    print("✅ Memory manager imported successfully")
    
    # Test memory manager creation
    mm = create_memory_manager()
    print("✅ Memory manager created successfully")
    
    # Test collections
    print(f"✅ Conversations collection: {mm.conversations is not None}")
    print(f"✅ Checkpoints collection: {mm.checkpoints is not None}")
    print(f"✅ Memory context collection: {mm.memory_context is not None}")
    
    # Test a simple query
    try:
        history = mm.get_conversation_history("test_thread", limit=1)
        print(f"✅ Query test successful: {len(history)} results")
    except Exception as e:
        print(f"❌ Query test failed: {e}")
    
    # Close connection
    mm.close()
    print("✅ Memory manager closed successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
