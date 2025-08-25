#!/usr/bin/env python3
"""
Test MongoDB connection for LangGraph Memory System
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from pymongo import MongoClient
    print("✅ PyMongo imported successfully")
    
    # Test MongoDB connection
    mongodb_url = "mongodb://localhost:27017/Hackwave"
    print(f"🔗 Testing connection to: {mongodb_url}")
    
    client = MongoClient(mongodb_url)
    
    # Test connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful!")
    
    # Test database access
    db = client.get_database()
    print(f"✅ Database access successful: {db.name}")
    
    # Test collection creation
    test_collection = db.test_collection
    print("✅ Collection access successful")
    
    # Test insert and find
    test_doc = {"test": "data", "timestamp": "2024-01-01"}
    result = test_collection.insert_one(test_doc)
    print(f"✅ Insert successful: {result.inserted_id}")
    
    # Find the document
    found_doc = test_collection.find_one({"test": "data"})
    print(f"✅ Find successful: {found_doc}")
    
    # Clean up
    test_collection.delete_one({"test": "data"})
    print("✅ Cleanup successful")
    
    client.close()
    print("✅ MongoDB connection closed")
    
except ImportError as e:
    print(f"❌ PyMongo import failed: {e}")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    print("💡 Make sure MongoDB is running on localhost:27017")
