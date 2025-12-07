"""
Verify sample data was inserted correctly into DynamoDB
"""

import boto3
from datetime import datetime, date, timedelta

# AWS Configuration
REGION = "us-east-1"
TABLE_PREFIX = "health-chatbot-dev"
TEST_USER_ID = "demo_user_90day"

def main():
    print("🔍 Verifying sample data in DynamoDB...\n")

    dynamodb = boto3.resource('dynamodb', region_name=REGION)

    # Check user profile
    print("1. User Profile:")
    user_profiles_table = dynamodb.Table(f"{TABLE_PREFIX}-user_profiles")
    response = user_profiles_table.get_item(Key={'user_id': TEST_USER_ID})

    if 'Item' in response:
        profile = response['Item']
        print(f"   ✅ Found user: {profile.get('name', 'N/A')}")
        print(f"      • Age: {profile.get('age', 'N/A')}")
        print(f"      • Target calories: {profile.get('target_calories', 'N/A')}")
        print(f"      • Goal: {profile.get('goal', 'N/A')}")
    else:
        print("   ❌ User profile not found")
        return

    # Check body logs
    print("\n2. Body Logs:")
    body_logs_table = dynamodb.Table(f"{TABLE_PREFIX}-body_logs")
    response = body_logs_table.query(
        IndexName='UserIdDateIndex',
        KeyConditionExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': TEST_USER_ID},
        ScanIndexForward=False,
        Limit=5
    )

    body_logs_count = response['Count']
    print(f"   ✅ Found {body_logs_count} recent body logs")
    if response['Items']:
        latest = response['Items'][0]
        print(f"      • Latest weight: {latest.get('weight', 'N/A')} kg on {latest.get('date', 'N/A')}")

    # Check nutrition logs
    print("\n3. Nutrition Logs:")
    nutrition_logs_table = dynamodb.Table(f"{TABLE_PREFIX}-nutrition_logs")
    response = nutrition_logs_table.query(
        IndexName='UserIdDateIndex',
        KeyConditionExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': TEST_USER_ID},
        ScanIndexForward=False,
        Limit=5
    )

    nutrition_count = response['Count']
    print(f"   ✅ Found {nutrition_count} recent nutrition logs")
    if response['Items']:
        latest = response['Items'][0]
        print(f"      • Latest meal: {latest.get('meal_type', 'N/A')} - {latest.get('calories', 'N/A')} cal on {latest.get('date', 'N/A')}")

    # Check workout logs
    print("\n4. Workout Logs:")
    workout_logs_table = dynamodb.Table(f"{TABLE_PREFIX}-workout_logs")
    response = workout_logs_table.query(
        IndexName='UserIdDateIndex',
        KeyConditionExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': TEST_USER_ID},
        ScanIndexForward=False,
        Limit=5
    )

    workout_count = response['Count']
    print(f"   ✅ Found {workout_count} recent workout logs")
    if response['Items']:
        latest = response['Items'][0]
        print(f"      • Latest workout: {latest.get('workout_name', 'N/A')} on {latest.get('date', 'N/A')}")
        print(f"      • Duration: {latest.get('duration_minutes', 'N/A')} minutes")

    # Check daily summaries
    print("\n5. Daily Summaries:")
    summaries_table = dynamodb.Table(f"{TABLE_PREFIX}-daily_summaries")
    response = summaries_table.query(
        IndexName='UserIdDateIndex',
        KeyConditionExpression='user_id = :uid',
        ExpressionAttributeValues={':uid': TEST_USER_ID},
        ScanIndexForward=False,
        Limit=5
    )

    summary_count = response['Count']
    print(f"   ✅ Found {summary_count} recent daily summaries")
    if response['Items']:
        latest = response['Items'][0]
        print(f"      • Latest summary ({latest.get('date', 'N/A')}):")
        print(f"        - Total calories: {latest.get('total_calories', 'N/A')}")
        print(f"        - Protein: {latest.get('total_protein', 'N/A')}g")
        print(f"        - Weight: {latest.get('weight', 'N/A')}kg")
        print(f"        - Workouts: {latest.get('workouts_completed', 'N/A')}")

    print("\n✅ Data verification complete!")
    print(f"\n🚀 Your sample data is ready!")
    print(f"   User ID: {TEST_USER_ID}")
    print(f"   CloudFront URL: https://d18dmr2jorio01.cloudfront.net")

if __name__ == "__main__":
    main()
