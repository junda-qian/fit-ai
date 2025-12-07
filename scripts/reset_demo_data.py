"""
Reset demo user data - delete everything and start fresh

This script:
1. Deletes all data for demo_user_90day
2. Ensures clean slate for re-insertion
"""

import boto3

# AWS Configuration
REGION = "us-east-1"
TABLE_PREFIX = "health-chatbot-dev"
TEST_USER_ID = "demo_user_90day"

def delete_all_items(table, key_name, key_value, sort_key_name=None):
    """Delete all items matching the key"""
    count = 0

    if sort_key_name:
        # Query with partition key
        response = table.query(
            IndexName='UserIdIndex' if key_name == 'user_id' and table.table_name.endswith('user_exercises') else 'UserIdDateIndex',
            KeyConditionExpression=f'{key_name} = :val',
            ExpressionAttributeValues={':val': key_value}
        )
    else:
        # Scan for partition key
        response = table.scan(
            FilterExpression=f'{key_name} = :val',
            ExpressionAttributeValues={':val': key_value}
        )

    items = response.get('Items', [])

    # Delete each item
    for item in items:
        # Get the primary key(s)
        key = {}

        # Determine the actual partition key from table description
        table_desc = table.meta.client.describe_table(TableName=table.table_name)
        key_schema = table_desc['Table']['KeySchema']

        for key_element in key_schema:
            key_attr_name = key_element['AttributeName']
            if key_attr_name in item:
                key[key_attr_name] = item[key_attr_name]

        table.delete_item(Key=key)
        count += 1

    return count

def main():
    print(f"🗑️  Deleting all data for user: {TEST_USER_ID}\n")

    dynamodb = boto3.resource('dynamodb', region_name=REGION)

    tables_to_clean = [
        'user_profiles',
        'user_exercises',
        'body_logs',
        'nutrition_logs',
        'workout_logs',
        'daily_summaries',
        'training_recommendations',
        'training_progress_summaries',
    ]

    total_deleted = 0

    for table_name in tables_to_clean:
        full_table_name = f"{TABLE_PREFIX}-{table_name}"
        print(f"Cleaning {table_name}...")

        try:
            table = dynamodb.Table(full_table_name)
            count = delete_all_items(table, 'user_id', TEST_USER_ID)
            print(f"  ✅ Deleted {count} items")
            total_deleted += count
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)}")

    print(f"\n✅ Cleanup complete!")
    print(f"Total items deleted: {total_deleted}\n")
    print(f"You can now run insert_sample_data_to_dynamodb.py to add fresh data.")

if __name__ == "__main__":
    main()
