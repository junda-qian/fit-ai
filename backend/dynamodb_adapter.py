"""
DynamoDB adapter for tracking system
Provides the same interface as JSONDatabase but uses DynamoDB
"""
import os
import boto3
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import json


class DecimalEncoder(json.JSONEncoder):
    """Helper to convert Decimal to float for JSON serialization"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


class DynamoDBAdapter:
    """DynamoDB adapter with same interface as JSONDatabase"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=os.getenv('DEFAULT_AWS_REGION', 'us-east-1'))

        # Table name mapping
        self.table_mapping = {
            "user_profiles": os.getenv('DYNAMODB_USER_PROFILES'),
            "workout_plans": os.getenv('DYNAMODB_WORKOUT_PLANS'),
            "nutrition_logs": os.getenv('DYNAMODB_NUTRITION_LOGS'),
            "workout_logs": os.getenv('DYNAMODB_WORKOUT_LOGS'),
            "body_logs": os.getenv('DYNAMODB_BODY_LOGS'),
            "daily_summaries": os.getenv('DYNAMODB_DAILY_SUMMARIES'),
        }

    def _get_table(self, collection: str):
        """Get DynamoDB table for collection"""
        table_name = self.table_mapping.get(collection)
        if not table_name:
            raise ValueError(f"Unknown collection: {collection}")
        return self.dynamodb.Table(table_name)

    def _convert_to_dynamodb(self, data: Dict) -> Dict:
        """Convert Python types to DynamoDB types"""
        return json.loads(json.dumps(data, default=str), parse_float=Decimal)

    def _convert_from_dynamodb(self, data: Dict) -> Dict:
        """Convert DynamoDB types to Python types"""
        return json.loads(json.dumps(data, cls=DecimalEncoder))

    def insert(self, collection: str, document: Dict) -> Dict:
        """Insert a document"""
        table = self._get_table(collection)
        item = self._convert_to_dynamodb(document)
        table.put_item(Item=item)
        return document

    def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        """Find single document"""
        table = self._get_table(collection)

        # If querying by primary key
        if collection == "user_profiles" and "user_id" in query:
            try:
                response = table.get_item(Key={"user_id": query["user_id"]})
                if 'Item' in response:
                    return self._convert_from_dynamodb(response['Item'])
            except Exception as e:
                print(f"DynamoDB get_item error: {e}")
                return None

        # If querying by id (hash key for other tables)
        if "id" in query:
            try:
                response = table.get_item(Key={"id": query["id"]})
                if 'Item' in response:
                    item = self._convert_from_dynamodb(response['Item'])
                    # Check other query conditions
                    if all(item.get(k) == v for k, v in query.items()):
                        return item
            except Exception as e:
                print(f"DynamoDB get_item error: {e}")
                return None

        # Otherwise, use query with GSI if user_id is provided
        if "user_id" in query and collection != "user_profiles":
            try:
                if collection == "workout_plans":
                    # Simple user_id query
                    response = table.query(
                        IndexName="UserIdIndex",
                        KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(query['user_id'])
                    )
                else:
                    # user_id + date range query
                    if "date" in query:
                        response = table.query(
                            IndexName="UserIdDateIndex",
                            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(query['user_id']) &
                                                 boto3.dynamodb.conditions.Key('date').eq(query['date'])
                        )
                    else:
                        response = table.query(
                            IndexName="UserIdDateIndex",
                            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(query['user_id'])
                        )

                items = [self._convert_from_dynamodb(item) for item in response.get('Items', [])]

                # Filter by additional conditions
                for item in items:
                    if all(item.get(k) == v for k, v in query.items()):
                        return item
            except Exception as e:
                print(f"DynamoDB query error: {e}")
                return None

        return None

    def find(self, collection: str, query: Dict) -> List[Dict]:
        """Find multiple documents"""
        table = self._get_table(collection)

        # Use GSI if querying by user_id
        if "user_id" in query and collection != "user_profiles":
            try:
                if collection == "workout_plans":
                    # Simple user_id query
                    response = table.query(
                        IndexName="UserIdIndex",
                        KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(query['user_id'])
                    )
                else:
                    # user_id + date range query
                    if "date" in query:
                        response = table.query(
                            IndexName="UserIdDateIndex",
                            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(query['user_id']) &
                                                 boto3.dynamodb.conditions.Key('date').eq(query['date'])
                        )
                    else:
                        response = table.query(
                            IndexName="UserIdDateIndex",
                            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(query['user_id'])
                        )

                items = [self._convert_from_dynamodb(item) for item in response.get('Items', [])]

                # Filter by additional conditions
                results = []
                for item in items:
                    if all(item.get(k) == v for k, v in query.items()):
                        results.append(item)
                return results
            except Exception as e:
                print(f"DynamoDB query error: {e}")
                return []

        # Fallback to scan (inefficient, but works for small datasets)
        try:
            response = table.scan()
            items = [self._convert_from_dynamodb(item) for item in response.get('Items', [])]

            results = []
            for item in items:
                if all(item.get(k) == v for k, v in query.items()):
                    results.append(item)
            return results
        except Exception as e:
            print(f"DynamoDB scan error: {e}")
            return []

    def update(self, collection: str, query: Dict, update: Dict) -> bool:
        """Update documents"""
        # Find items to update
        items = self.find(collection, query)

        if not items:
            return False

        table = self._get_table(collection)
        updated = False

        for item in items:
            # Get primary key
            if collection == "user_profiles":
                key = {"user_id": item["user_id"]}
            else:
                key = {"id": item["id"]}

            # Merge update into item
            updated_item = {**item, **update}
            updated_item['updated_at'] = datetime.now().isoformat()

            # Put updated item
            table.put_item(Item=self._convert_to_dynamodb(updated_item))
            updated = True

        return updated

    def delete(self, collection: str, query: Dict) -> int:
        """Delete documents"""
        items = self.find(collection, query)

        if not items:
            return 0

        table = self._get_table(collection)
        count = 0

        for item in items:
            # Get primary key
            if collection == "user_profiles":
                key = {"user_id": item["user_id"]}
            else:
                key = {"id": item["id"]}

            table.delete_item(Key=key)
            count += 1

        return count
