#!/usr/bin/env python3
"""
MongoDB utilities for the Dataset Visualizer app
Provides functions to query GeoJSON data from MongoDB
"""

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import List, Dict, Any, Optional
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Connection Details
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")


class MongoDBClient:
    """MongoDB client for GeoJSON data access"""
    
    def __init__(self, uri=MONGO_URI, db_name=MONGO_DB, collection_name=MONGO_COLLECTION):
        """Initialize MongoDB client"""
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            print("✓ Connected to MongoDB")
            return True
        except PyMongoError as e:
            print(f"✗ Failed to connect to MongoDB: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            print("✓ Disconnected from MongoDB")
    
    def get_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get GeoJSON by filename"""
        try:
            return self.collection.find_one({"_filename": filename})
        except PyMongoError as e:
            print(f"Error querying by filename: {str(e)}")
            return None
    
    def search_by_name(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for features by filename (partial match)"""
        try:
            query = {"_filename": {"$regex": search_term, "$options": "i"}}
            return list(self.collection.find(query).limit(limit))
        except PyMongoError as e:
            print(f"Error searching: {str(e)}")
            return []
    
    def get_all_features(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all features with optional limit"""
        try:
            return list(self.collection.find({}).limit(limit))
        except PyMongoError as e:
            print(f"Error retrieving features: {str(e)}")
            return []
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature filenames"""
        try:
            filenames = self.collection.distinct("_filename")
            return sorted(filenames)
        except PyMongoError as e:
            print(f"Error retrieving filenames: {str(e)}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            stats = {
                "document_count": self.collection.count_documents({}),
                "indexes": list(self.collection.list_indexes()),
            }
            return stats
        except PyMongoError as e:
            print(f"Error getting stats: {str(e)}")
            return {}
    
    def bulk_insert_features(self, features: List[Dict[str, Any]]) -> bool:
        """Bulk insert multiple features"""
        try:
            if features:
                result = self.collection.insert_many(features)
                print(f"✓ Inserted {len(result.inserted_ids)} features")
                return True
            return False
        except PyMongoError as e:
            print(f"Error bulk inserting: {str(e)}")
            return False


# Convenience functions for use in Flask app

def get_mongodb_client():
    """Get a configured MongoDB client"""
    client = MongoDBClient()
    if client.connect():
        return client
    return None


def get_geojson_by_name(name: str) -> Optional[Dict[str, Any]]:
    """Get GeoJSON feature by name"""
    client = get_mongodb_client()
    if client:
        try:
            feature = client.get_by_filename(name)
            return feature
        finally:
            client.disconnect()
    return None
