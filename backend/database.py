"""
Simple JSON file-based database for MVP

Why JSON files instead of a real database?
- ✅ No setup required (no PostgreSQL/MongoDB installation)
- ✅ Easy to debug (just open the JSON file)
- ✅ Perfect for MVP/testing
- ✅ Easy to migrate later (we'll move to DynamoDB/PostgreSQL in production)

How it works:
- Each "collection" (like a database table) is a JSON file
- Each file contains an array of objects
- We read the file, modify it in memory, then write it back

Example file structure:
user_profiles.json:
[
  {
    "id": "uuid-1",
    "user_id": "user_123",
    "target_calories": 2640,
    "target_protein": 180,
    ...
  },
  {
    "id": "uuid-2",
    "user_id": "user_456",
    ...
  }
]
"""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pathlib import Path


class JSONDatabase:
    """Simple file-based database using JSON"""

    def __init__(self, data_dir: str = "data/tracking"):
        """
        Initialize the database

        Args:
            data_dir: Directory where JSON files will be stored
        """
        self.data_dir = Path(data_dir)
        # Create directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Define our "collections" (like database tables)
        # Each collection is stored in a separate JSON file
        self.collections = {
            "user_profiles": self.data_dir / "user_profiles.json",
            "workout_plans": self.data_dir / "workout_plans.json",
            "nutrition_logs": self.data_dir / "nutrition_logs.json",
            "workout_logs": self.data_dir / "workout_logs.json",
            "body_logs": self.data_dir / "body_logs.json",
            "daily_summaries": self.data_dir / "daily_summaries.json",
        }

        # Initialize empty collections if they don't exist
        for collection_file in self.collections.values():
            if not collection_file.exists():
                self._write_file(collection_file, [])

    def _read_file(self, file_path: Path) -> List[Dict]:
        """
        Read JSON file and return list of documents

        Example:
        [
          {"id": "1", "name": "John"},
          {"id": "2", "name": "Jane"}
        ]
        """
        with open(file_path, 'r') as f:
            return json.load(f)

    def _write_file(self, file_path: Path, data: List[Dict]):
        """
        Write list of documents to JSON file

        Args:
            file_path: Path to JSON file
            data: List of dictionaries to write

        Note: We use default=str to handle datetime objects
        """
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def insert(self, collection: str, document: Dict) -> Dict:
        """
        Insert a new document into collection

        Example:
        db.insert("user_profiles", {
            "user_id": "user_123",
            "target_calories": 2640,
            ...
        })

        Args:
            collection: Collection name (e.g., "user_profiles")
            document: Dictionary to insert

        Returns:
            The inserted document
        """
        file_path = self.collections[collection]
        data = self._read_file(file_path)
        data.append(document)
        self._write_file(file_path, data)
        return document

    def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        """
        Find single document matching query

        Example:
        db.find_one("user_profiles", {"user_id": "user_123"})

        Returns the FIRST document where all query fields match
        Returns None if no match found

        Args:
            collection: Collection name
            query: Dictionary of field: value pairs to match

        Returns:
            First matching document or None
        """
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        for doc in data:
            # Check if all query fields match this document
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    def find(self, collection: str, query: Dict) -> List[Dict]:
        """
        Find ALL documents matching query

        Example:
        db.find("nutrition_logs", {"user_id": "user_123"})

        Returns ALL documents where all query fields match

        Args:
            collection: Collection name
            query: Dictionary of field: value pairs to match

        Returns:
            List of matching documents (empty list if none found)
        """
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        results = []
        for doc in data:
            # Check if all query fields match this document
            if all(doc.get(k) == v for k, v in query.items()):
                results.append(doc)
        return results

    def update(self, collection: str, query: Dict, update: Dict) -> bool:
        """
        Update documents matching query

        Example:
        db.update(
            "user_profiles",
            {"user_id": "user_123"},
            {"target_calories": 2800, "updated_at": "2025-10-18"}
        )

        Updates ALL documents that match the query

        Args:
            collection: Collection name
            query: Dictionary to find documents to update
            update: Dictionary of fields to update

        Returns:
            True if any documents were updated, False otherwise
        """
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        updated = False
        for doc in data:
            # Check if this document matches the query
            if all(doc.get(k) == v for k, v in query.items()):
                # Update the document
                doc.update(update)
                doc['updated_at'] = datetime.now().isoformat()
                updated = True

        if updated:
            self._write_file(file_path, data)
        return updated

    def delete(self, collection: str, query: Dict) -> int:
        """
        Delete documents matching query

        Example:
        db.delete("nutrition_logs", {"id": "log_123"})

        Deletes ALL documents that match the query

        Args:
            collection: Collection name
            query: Dictionary to find documents to delete

        Returns:
            Number of documents deleted
        """
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        original_length = len(data)

        # Keep only documents that DON'T match the query
        data = [
            doc for doc in data
            if not all(doc.get(k) == v for k, v in query.items())
        ]

        self._write_file(file_path, data)
        return original_length - len(data)


# Global database instance
# This allows us to import and use: from database import db

# Determine which database to use based on environment
import os

USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'false').lower() == 'true'

if USE_DYNAMODB:
    from dynamodb_adapter import DynamoDBAdapter
    db = DynamoDBAdapter()
    print("✅ Using DynamoDB for tracking data")
else:
    db = JSONDatabase()
    print("✅ Using JSON files for tracking data (local development)")
