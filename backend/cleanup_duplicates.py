#!/usr/bin/env python3
"""
Duplicate Cleanup Script for LangGraph Memory System

This script removes duplicate entries from the LangGraph memory array
to prevent repetitive content and improve system performance.
"""

import os
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.memory import create_langgraph_memory_manager

def cleanup_duplicates():
    """Remove duplicate entries from LangGraph memory."""
    
    print("🧹 Starting LangGraph Memory Duplicate Cleanup...")
    print("=" * 60)
    
    try:
        # Initialize memory manager
        memory_manager = create_langgraph_memory_manager()
        
        # Get all memory entries
        all_entries = memory_manager.get_memory_context(limit=1000)
        
        if not all_entries:
            print("✅ No memory entries found. Nothing to clean up.")
            return
        
        print(f"📊 Found {len(all_entries)} total memory entries")
        
        # Track duplicates
        duplicates_found = 0
        unique_entries = []
        seen_queries = set()
        seen_responses = set()
        
        for entry in all_entries:
            user_query = entry.get("user_query", "").lower().strip()
            response = entry.get("response", "").lower().strip()
            
            # Check for exact duplicates
            if user_query in seen_queries and response in seen_responses:
                duplicates_found += 1
                print(f"🗑️  Removing duplicate: {user_query[:50]}...")
                continue
            
            # Check for similar responses (80% similarity)
            is_similar = False
            for seen_response in seen_responses:
                similarity = calculate_similarity(response, seen_response)
                if similarity > 0.8:
                    is_similar = True
                    duplicates_found += 1
                    print(f"🗑️  Removing similar: {user_query[:50]}... (similarity: {similarity:.2f})")
                    break
            
            if not is_similar:
                unique_entries.append(entry)
                seen_queries.add(user_query)
                seen_responses.add(response)
        
        # Update memory array with unique entries only
        if duplicates_found > 0:
            print(f"\n🔄 Updating memory array with {len(unique_entries)} unique entries...")
            
            # Clear existing array
            memory_manager.clear_memory()
            
            # Re-add unique entries
            for entry in unique_entries:
                memory_manager.add_to_memory_array(
                    thread_id=entry.get("thread_id", "unknown"),
                    user_query=entry.get("user_query", ""),
                    response=entry.get("response", ""),
                    context=entry.get("context", {})
                )
            
            print(f"✅ Cleanup completed! Removed {duplicates_found} duplicate entries.")
            print(f"📊 Memory now contains {len(unique_entries)} unique entries.")
        else:
            print("✅ No duplicates found. Memory is already clean!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        return False
    
    return True

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate similarity between two texts."""
    try:
        # Clean texts
        text1_clean = text1.lower().strip()
        text2_clean = text2.lower().strip()
        
        # If identical, return 1.0
        if text1_clean == text2_clean:
            return 1.0
        
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

def show_memory_stats():
    """Show current memory statistics."""
    
    print("\n📈 Memory Statistics:")
    print("-" * 30)
    
    try:
        memory_manager = create_langgraph_memory_manager()
        stats = memory_manager.get_memory_stats()
        
        if stats:
            print(f"Total Entries: {stats.get('total_entries', 0)}")
            print(f"Thread Count: {stats.get('thread_count', 0)}")
            print(f"Storage Type: {stats.get('storage_type', 'Unknown')}")
            
            if stats.get('created_at'):
                print(f"Created: {stats['created_at']}")
            if stats.get('last_updated'):
                print(f"Last Updated: {stats['last_updated']}")
        else:
            print("No memory statistics available.")
            
    except Exception as e:
        print(f"Error getting stats: {e}")

if __name__ == "__main__":
    print("🧠 LangGraph Memory Duplicate Cleanup Tool")
    print("=" * 50)
    
    # Show current stats
    show_memory_stats()
    
    # Ask for confirmation
    response = input("\n🤔 Do you want to proceed with duplicate cleanup? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        success = cleanup_duplicates()
        
        if success:
            print("\n📊 Final Memory Statistics:")
            show_memory_stats()
        else:
            print("\n❌ Cleanup failed. Please check the error messages above.")
    else:
        print("❌ Cleanup cancelled by user.")
    
    print("\n👋 Cleanup tool finished.")
