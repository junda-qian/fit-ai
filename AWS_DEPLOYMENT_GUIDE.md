# AWS Deployment Guide - Tracking System

## Overview

This guide provides step-by-step instructions to deploy the complete tracking system to AWS infrastructure. After following this guide, your tracking system (nutrition logging, workout logging, body weight tracking, progress charts) will be fully operational in AWS.

**Prerequisites:**
- ✅ Local testing completed and passed
- ✅ Feature branch: `feature/tracking-system`
- ✅ AWS account with appropriate permissions
- ✅ Terraform installed locally
- ✅ AWS CLI configured with credentials

**Estimated Time:** 2-3 hours

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Phase 1: Update Terraform Infrastructure](#phase-1-update-terraform-infrastructure)
3. [Phase 2: Update Backend Code](#phase-2-update-backend-code)
4. [Phase 3: Deploy Infrastructure](#phase-3-deploy-infrastructure)
5. [Phase 4: Deploy Lambda Function](#phase-4-deploy-lambda-function)
6. [Phase 5: Deploy Frontend](#phase-5-deploy-frontend)
7. [Phase 6: Test in AWS](#phase-6-test-in-aws)
8. [Phase 7: Verify & Monitor](#phase-7-verify--monitor)
9. [Rollback Procedure](#rollback-procedure)
10. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before starting, verify these items:

### Local Environment
- [ ] Local testing completed successfully
- [ ] All tests passing
- [ ] Git status clean (no uncommitted changes except test data)
- [ ] Current branch: `feature/tracking-system`
- [ ] Latest changes pushed to remote

### AWS Prerequisites
- [ ] AWS CLI installed: `aws --version`
- [ ] AWS credentials configured: `aws sts get-caller-identity`
- [ ] Terraform installed: `terraform --version` (should be >= 1.0)
- [ ] Access to AWS account ID: 767398103642
- [ ] USDA API key ready: `mrACeMiM6cd1HrbGemjTE9GuBqszVAMKpYqv1UYN`

### Current Infrastructure Status
Check what's already deployed:
```bash
cd terraform
terraform show
```

Expected existing resources:
- [ ] Lambda function (API)
- [ ] API Gateway
- [ ] S3 buckets (frontend, documents, memory)
- [ ] CloudFront distribution
- [ ] OpenSearch Serverless collection
- [ ] IAM roles and policies

---

## Phase 1: Update Terraform Infrastructure

**Estimated Time:** 30 minutes

### Step 1.1: Create DynamoDB Tables Configuration

**File:** `terraform/dynamodb.tf` (NEW FILE)

Create this new file with 6 DynamoDB tables:

```hcl
# DynamoDB Tables for Tracking System

locals {
  dynamodb_tables = {
    user_profiles = {
      hash_key = "user_id"
      attributes = [
        { name = "user_id", type = "S" },
      ]
      gsi = []
    }
    workout_plans = {
      hash_key = "id"
      attributes = [
        { name = "id", type = "S" },
        { name = "user_id", type = "S" },
      ]
      gsi = [
        {
          name            = "UserIdIndex"
          hash_key        = "user_id"
          projection_type = "ALL"
        }
      ]
    }
    nutrition_logs = {
      hash_key = "id"
      attributes = [
        { name = "id", type = "S" },
        { name = "user_id", type = "S" },
        { name = "date", type = "S" },
      ]
      gsi = [
        {
          name            = "UserIdDateIndex"
          hash_key        = "user_id"
          range_key       = "date"
          projection_type = "ALL"
        }
      ]
    }
    workout_logs = {
      hash_key = "id"
      attributes = [
        { name = "id", type = "S" },
        { name = "user_id", type = "S" },
        { name = "date", type = "S" },
      ]
      gsi = [
        {
          name            = "UserIdDateIndex"
          hash_key        = "user_id"
          range_key       = "date"
          projection_type = "ALL"
        }
      ]
    }
    body_logs = {
      hash_key = "id"
      attributes = [
        { name = "id", type = "S" },
        { name = "user_id", type = "S" },
        { name = "date", type = "S" },
      ]
      gsi = [
        {
          name            = "UserIdDateIndex"
          hash_key        = "user_id"
          range_key       = "date"
          projection_type = "ALL"
        }
      ]
    }
    daily_summaries = {
      hash_key = "id"
      attributes = [
        { name = "id", type = "S" },
        { name = "user_id", type = "S" },
        { name = "date", type = "S" },
      ]
      gsi = [
        {
          name            = "UserIdDateIndex"
          hash_key        = "user_id"
          range_key       = "date"
          projection_type = "ALL"
        }
      ]
    }
  }
}

# Create DynamoDB tables
resource "aws_dynamodb_table" "tracking_tables" {
  for_each = local.dynamodb_tables

  name           = "${local.name_prefix}-${each.key}"
  billing_mode   = "PAY_PER_REQUEST"  # On-demand pricing
  hash_key       = each.value.hash_key
  range_key      = lookup(each.value, "range_key", null)

  # Define attributes
  dynamic "attribute" {
    for_each = each.value.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  # Add range_key attribute if it exists
  dynamic "attribute" {
    for_each = lookup(each.value, "range_key", null) != null ? [1] : []
    content {
      name = each.value.range_key
      type = "S"
    }
  }

  # Global Secondary Indexes
  dynamic "global_secondary_index" {
    for_each = each.value.gsi
    content {
      name            = global_secondary_index.value.name
      hash_key        = global_secondary_index.value.hash_key
      range_key       = lookup(global_secondary_index.value, "range_key", null)
      projection_type = global_secondary_index.value.projection_type
    }
  }

  # Enable point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = merge(
    local.common_tags,
    {
      Purpose = "Tracking System"
    }
  )
}

# Output table names for reference
output "dynamodb_table_names" {
  value = {
    for k, v in aws_dynamodb_table.tracking_tables : k => v.name
  }
  description = "Names of all DynamoDB tracking tables"
}

output "dynamodb_table_arns" {
  value = {
    for k, v in aws_dynamodb_table.tracking_tables : k => v.arn
  }
  description = "ARNs of all DynamoDB tracking tables"
}
```

**Why these tables:**
- **user_profiles**: Stores calculator results (targets, BMR, TDEE)
- **workout_plans**: Stores generated workout plans
- **nutrition_logs**: Meal/food entries
- **workout_logs**: Workout session logs
- **body_logs**: Weight & body measurements
- **daily_summaries**: Pre-computed daily aggregations

**Why GSI (Global Secondary Index):**
- Enables efficient queries by `user_id` and `date`
- Example: "Get all nutrition logs for user X between date Y and Z"

---

### Step 1.2: Update Lambda IAM Permissions

**File:** `terraform/main.tf`

Add DynamoDB permissions to Lambda role:

**Find this section (around line 149):**
```hcl
resource "aws_iam_role_policy" "lambda_opensearch" {
  name = "${local.name_prefix}-lambda-opensearch-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "aoss:APIAccessAll"
        ]
        Resource = "*"
      }
    ]
  })
}
```

**Add AFTER it:**
```hcl
# DynamoDB access for Lambda
resource "aws_iam_role_policy" "lambda_dynamodb" {
  name = "${local.name_prefix}-lambda-dynamodb-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchGetItem",
          "dynamodb:BatchWriteItem"
        ]
        Resource = [
          for table in aws_dynamodb_table.tracking_tables : table.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query"
        ]
        Resource = [
          for table in aws_dynamodb_table.tracking_tables : "${table.arn}/index/*"
        ]
      }
    ]
  })
}
```

---

### Step 1.3: Add USDA API Key to Lambda Environment

**File:** `terraform/main.tf`

**Find the Lambda function resource (around line 176):**
```hcl
resource "aws_lambda_function" "api" {
  ...
  environment {
    variables = {
      CORS_ORIGINS        = var.use_custom_domain ? "https://${var.root_domain},https://www.${var.root_domain}" : "https://${aws_cloudfront_distribution.main.domain_name}"
      S3_BUCKET           = aws_s3_bucket.memory.id
      USE_S3              = "true"
      BEDROCK_MODEL_ID    = var.bedrock_model_id
      USE_OPENSEARCH      = "true"
      OPENSEARCH_ENDPOINT = aws_opensearchserverless_collection.health_docs.collection_endpoint
      DEFAULT_AWS_REGION  = data.aws_region.current.name
    }
  }
  ...
}
```

**Replace the `environment` block with:**
```hcl
  environment {
    variables = {
      CORS_ORIGINS        = var.use_custom_domain ? "https://${var.root_domain},https://www.${var.root_domain}" : "https://${aws_cloudfront_distribution.main.domain_name}"
      S3_BUCKET           = aws_s3_bucket.memory.id
      USE_S3              = "true"
      BEDROCK_MODEL_ID    = var.bedrock_model_id
      USE_OPENSEARCH      = "true"
      OPENSEARCH_ENDPOINT = aws_opensearchserverless_collection.health_docs.collection_endpoint
      DEFAULT_AWS_REGION  = data.aws_region.current.name

      # Tracking System Environment Variables
      USE_DYNAMODB        = "true"
      USDA_API_KEY        = var.usda_api_key

      # DynamoDB Table Names
      DYNAMODB_USER_PROFILES     = aws_dynamodb_table.tracking_tables["user_profiles"].name
      DYNAMODB_WORKOUT_PLANS     = aws_dynamodb_table.tracking_tables["workout_plans"].name
      DYNAMODB_NUTRITION_LOGS    = aws_dynamodb_table.tracking_tables["nutrition_logs"].name
      DYNAMODB_WORKOUT_LOGS      = aws_dynamodb_table.tracking_tables["workout_logs"].name
      DYNAMODB_BODY_LOGS         = aws_dynamodb_table.tracking_tables["body_logs"].name
      DYNAMODB_DAILY_SUMMARIES   = aws_dynamodb_table.tracking_tables["daily_summaries"].name
    }
  }
```

---

### Step 1.4: Add USDA API Key Variable

**File:** `terraform/variables.tf`

**Add to the end of the file:**
```hcl
variable "usda_api_key" {
  description = "USDA FoodData Central API Key for food database searches"
  type        = string
  sensitive   = true
}
```

---

### Step 1.5: Add New API Gateway Routes

**File:** `terraform/main.tf`

**Find the existing API Gateway routes section (around line 238-272):**

**Add AFTER the existing routes:**
```hcl
# ==================== Tracking System API Routes ====================

# User Profile Routes
resource "aws_apigatewayv2_route" "post_user_profile" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /api/user-profile"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_user_profile" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/user-profile/{user_id}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Workout Plan Routes
resource "aws_apigatewayv2_route" "post_workout_plan" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /api/workout-plan"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_active_workout_plan" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/workout-plan/{user_id}/active"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_all_workout_plans" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/workout-plan/{user_id}/all"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Nutrition Logging Routes
resource "aws_apigatewayv2_route" "post_nutrition_log" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /api/nutrition/logs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_nutrition_logs" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/nutrition/logs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Workout Logging Routes
resource "aws_apigatewayv2_route" "post_workout_log" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /api/workout/logs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_workout_logs" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/workout/logs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Body Logging Routes
resource "aws_apigatewayv2_route" "post_body_log" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /api/body/logs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_body_logs" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/body/logs"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Summary Routes
resource "aws_apigatewayv2_route" "get_daily_summary" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/summary/daily"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_route" "get_weekly_summary" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/summary/weekly"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

# Food Search Route
resource "aws_apigatewayv2_route" "get_food_search" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "GET /api/food/search"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}
```

**Total new routes: 14**

---

### Step 1.6: Create Terraform Variables File

**File:** `terraform/terraform.tfvars`

**Add this line:**
```hcl
usda_api_key = "mrACeMiM6cd1HrbGemjTE9GuBqszVAMKpYqv1UYN"
```

**Note:** Since you already have `!terraform.tfvars` in `.gitignore`, this file will be committed. The API key is not highly sensitive (it's rate-limited and free), but if you prefer, you can use environment variables instead.

---

## Phase 2: Update Backend Code

**Estimated Time:** 45 minutes

### Step 2.1: Create DynamoDB Database Adapter

**File:** `backend/dynamodb_adapter.py` (NEW FILE)

This adapter will replace the JSON file database with DynamoDB:

```python
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
                response = table.query(
                    IndexName="UserIdIndex" if collection == "workout_plans" else "UserIdDateIndex",
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
```

---

### Step 2.2: Update database.py to Support Both JSON and DynamoDB

**File:** `backend/database.py`

**Replace the bottom of the file (after the JSONDatabase class):**

```python
# ... existing JSONDatabase class remains unchanged ...

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
```

This ensures:
- **Local development**: Uses JSON files (when `USE_DYNAMODB=false`)
- **AWS Lambda**: Uses DynamoDB (when `USE_DYNAMODB=true`)

---

### Step 2.3: Update requirements.txt

**File:** `backend/requirements.txt`

Make sure boto3 is included (it should already be there):

```txt
fastapi
uvicorn
python-dotenv
python-multipart
boto3  # ← Should already exist
pypdf
mangum
langchain
langchain-aws
langchain-community
faiss-cpu
opensearch-py
requests-aws4auth
requests  # Add if missing (for USDA API)
```

---

## Phase 3: Deploy Infrastructure

**Estimated Time:** 15-20 minutes

### Step 3.1: Validate Terraform Changes

```bash
cd terraform

# Format Terraform files
terraform fmt

# Validate configuration
terraform validate

# Expected output: "Success! The configuration is valid."
```

---

### Step 3.2: Review Terraform Plan

```bash
# See what will be created/changed
terraform plan

# Expected output should show:
# + 6 DynamoDB tables
# + 1 IAM policy (DynamoDB access)
# + 14 API Gateway routes
# ~ 1 Lambda function (updated environment variables)
```

**Review the plan carefully:**
- [ ] 6 new DynamoDB tables
- [ ] DynamoDB IAM policy
- [ ] 14 new API routes
- [ ] Lambda environment variables updated
- [ ] No unexpected deletions

---

### Step 3.3: Apply Terraform Changes

```bash
# Apply the changes
terraform apply

# Review the plan again when prompted
# Type "yes" to confirm

# Expected time: 5-10 minutes
```

**What happens:**
1. Creates 6 DynamoDB tables with GSIs
2. Adds DynamoDB permissions to Lambda IAM role
3. Adds 14 new API Gateway routes
4. Updates Lambda environment variables

**Verify success:**
```bash
# Check DynamoDB tables
aws dynamodb list-tables | grep fitness-chatbot

# Should see:
# - fitness-chatbot-dev-user_profiles
# - fitness-chatbot-dev-workout_plans
# - fitness-chatbot-dev-nutrition_logs
# - fitness-chatbot-dev-workout_logs
# - fitness-chatbot-dev-body_logs
# - fitness-chatbot-dev-daily_summaries
```

---

## Phase 4: Deploy Lambda Function

**Estimated Time:** 10 minutes

### Step 4.1: Build Lambda Deployment Package

```bash
cd backend

# Create deployment package
./build_lambda.sh

# Or manually:
mkdir -p lambda-package
pip install -r requirements.txt -t lambda-package/
cp *.py lambda-package/
cd lambda-package && zip -r ../lambda-deployment.zip . && cd ..
```

**Verify package includes:**
- [ ] `server.py`
- [ ] `database.py`
- [ ] `dynamodb_adapter.py` (NEW)
- [ ] `models.py`
- [ ] `food_database.py`
- [ ] All dependencies (boto3, fastapi, etc.)

---

### Step 4.2: Upload Lambda Package

```bash
# Upload to S3 (Terraform will pick it up)
aws s3 cp lambda-deployment.zip s3://fitness-chatbot-dev-documents-767398103642/

# Update Lambda function
cd ../terraform
terraform apply -target=aws_lambda_function.api

# Or let Terraform detect the change:
terraform apply
```

---

### Step 4.3: Verify Lambda Deployment

```bash
# Check Lambda function
aws lambda get-function --function-name fitness-chatbot-dev-api

# Check environment variables
aws lambda get-function-configuration --function-name fitness-chatbot-dev-api --query 'Environment.Variables'

# Should include:
# - USE_DYNAMODB: "true"
# - USDA_API_KEY: "mrACe..."
# - DYNAMODB_USER_PROFILES: "fitness-chatbot-dev-user_profiles"
# - ... (all other DynamoDB table names)
```

---

## Phase 5: Deploy Frontend

**Estimated Time:** 10 minutes

### Step 5.1: Update Frontend API URL

**File:** `frontend/.env.production` (create if doesn't exist)

```bash
NEXT_PUBLIC_API_URL=https://YOUR_API_GATEWAY_URL
```

**Get API Gateway URL:**
```bash
cd terraform
terraform output

# Or:
aws apigatewayv2 get-apis --query 'Items[?Name==`fitness-chatbot-dev-api-gateway`].ApiEndpoint' --output text
```

---

### Step 5.2: Build Frontend

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build

# Expected output: .next folder with optimized build
```

---

### Step 5.3: Deploy to S3

```bash
# Upload to S3
aws s3 sync out/ s3://fitness-chatbot-dev-frontend-767398103642/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"

# Get distribution ID:
# terraform output | grep cloudfront_distribution_id
```

---

## Phase 6: Test in AWS

**Estimated Time:** 30 minutes

### Step 6.1: Get Frontend URL

```bash
cd terraform
terraform output cloudfront_domain_name

# Or visit CloudFront console to get URL
```

---

### Step 6.2: Test Complete User Journey

**Visit:** `https://YOUR_CLOUDFRONT_URL`

1. **Energy Calculator**
   - Navigate to `/calculator`
   - Fill in test data
   - Click "Calculate"
   - Click "Save & Continue"
   - **Verify:** Redirects to planner

2. **Workout Planner**
   - Fill in test data
   - Click "Generate Workout Plan"
   - Click "Start This Plan"
   - **Verify:** Redirects to dashboard

3. **Dashboard**
   - **Verify:** Shows your targets
   - **Verify:** Shows your plan name
   - **Verify:** Progress at 0%

4. **USDA Food Search**
   - Navigate to `/tracking/nutrition`
   - Search "banana"
   - **Verify:** Returns results

5. **Log Nutrition**
   - Add 2-3 meals
   - **Verify:** Meals appear in list

6. **Log Workout**
   - Navigate to `/tracking/workouts`
   - Log a workout
   - **Verify:** Workout saved

7. **Log Weight**
   - Navigate to dashboard
   - Log weight
   - **Verify:** Weight displayed

8. **Check Dashboard Updates**
   - Refresh dashboard
   - **Verify:** Progress bars updated
   - **Verify:** Workout shows "Completed"

---

### Step 6.3: Verify DynamoDB Data

```bash
# Check user profiles
aws dynamodb scan --table-name fitness-chatbot-dev-user_profiles

# Check nutrition logs
aws dynamodb scan --table-name fitness-chatbot-dev-nutrition_logs

# Check daily summaries
aws dynamodb scan --table-name fitness-chatbot-dev-daily_summaries
```

**Expected:** Should see entries corresponding to your test data

---

## Phase 7: Verify & Monitor

**Estimated Time:** 15 minutes

### Step 7.1: Check CloudWatch Logs

```bash
# View Lambda logs
aws logs tail /aws/lambda/fitness-chatbot-dev-api --follow

# Look for:
# - "✅ Using DynamoDB for tracking data"
# - No errors in tracking endpoints
```

---

### Step 7.2: Check API Gateway Metrics

**AWS Console:** API Gateway → fitness-chatbot-dev-api-gateway → Metrics

**Verify:**
- [ ] New routes receiving requests
- [ ] No 5xx errors
- [ ] Response times < 1 second

---

### Step 7.3: Check DynamoDB Metrics

**AWS Console:** DynamoDB → Tables

**For each table, check:**
- [ ] Item count > 0 (after testing)
- [ ] Read/write capacity showing activity
- [ ] No throttling errors

---

### Step 7.4: Performance Testing

Test with realistic load:
- [ ] Log 10+ meals
- [ ] Log 5+ workouts
- [ ] Query historical data (7-14 days)
- [ ] Dashboard loads in < 2 seconds
- [ ] Food search returns in < 1 second

---

## Rollback Procedure

**If something goes wrong:**

### Option 1: Rollback Terraform Changes

```bash
cd terraform

# Destroy new resources
terraform destroy -target=aws_dynamodb_table.tracking_tables
terraform destroy -target=aws_iam_role_policy.lambda_dynamodb

# Restore previous Lambda
# (Upload previous lambda-deployment.zip)
```

---

### Option 2: Rollback to Previous Git Commit

```bash
# Find previous commit
git log --oneline

# Revert to previous state
git revert HEAD

# Or reset (destructive):
git reset --hard PREVIOUS_COMMIT_HASH
```

---

### Option 3: Switch Back to JSON Storage

```bash
# Update Lambda environment variable
aws lambda update-function-configuration \
  --function-name fitness-chatbot-dev-api \
  --environment Variables="{USE_DYNAMODB=false}"
```

---

## Troubleshooting

### Issue 1: DynamoDB Permission Denied

**Error:** `AccessDeniedException: User is not authorized to perform: dynamodb:PutItem`

**Solution:**
```bash
# Verify IAM policy attached
aws iam list-attached-role-policies --role-name fitness-chatbot-dev-lambda-role

# Check inline policies
aws iam list-role-policies --role-name fitness-chatbot-dev-lambda-role
aws iam get-role-policy --role-name fitness-chatbot-dev-lambda-role --policy-name fitness-chatbot-dev-lambda-dynamodb-policy
```

---

### Issue 2: USDA API Not Working

**Error:** `Food search returns no results` or `401 Unauthorized`

**Solution:**
```bash
# Verify environment variable
aws lambda get-function-configuration \
  --function-name fitness-chatbot-dev-api \
  --query 'Environment.Variables.USDA_API_KEY'

# Test API key directly
curl "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=YOUR_KEY&query=banana"
```

---

### Issue 3: API Gateway Route Not Found

**Error:** `404 Not Found` for tracking endpoints

**Solution:**
```bash
# List all routes
aws apigatewayv2 get-routes --api-id YOUR_API_ID

# Verify routes deployed
terraform state list | grep aws_apigatewayv2_route
```

---

### Issue 4: Lambda Timeout

**Error:** `Task timed out after 3.00 seconds`

**Solution:**
```bash
# Increase timeout in terraform/main.tf
# timeout = 30  (or higher)

terraform apply
```

---

### Issue 5: Frontend Not Updating

**Error:** Old version of frontend still showing

**Solution:**
```bash
# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id YOUR_DIST_ID \
  --paths "/*"

# Wait 2-5 minutes for propagation
```

---

## Post-Deployment Checklist

After successful deployment:

- [ ] All tracking features working in AWS
- [ ] DynamoDB tables populated with test data
- [ ] No errors in CloudWatch logs
- [ ] API response times acceptable
- [ ] Frontend accessible via CloudFront
- [ ] USDA food search working
- [ ] Dashboard displaying correct data
- [ ] Progress charts rendering

**If all checks pass:**
```bash
# Merge to main
git checkout main
git merge feature/tracking-system
git push origin main

# Tag release
git tag -a v1.0-tracking-system -m "Release: Complete tracking system with DynamoDB"
git push origin v1.0-tracking-system
```

---

## Cost Estimates

**Expected AWS costs (monthly):**

- **DynamoDB:** $1-5 (on-demand, low traffic)
- **Lambda:** $0-1 (first 1M requests free)
- **API Gateway:** $0-1 (first 1M requests free)
- **CloudFront:** $0-1 (low traffic)
- **S3:** $0.50 (storage + requests)

**Total:** ~$2-10/month for prototype

---

## Next Steps

After successful deployment:

1. **User Testing:** Get real users to test the system
2. **Monitor Metrics:** Watch CloudWatch for performance/errors
3. **Optimize Queries:** Add more GSIs if needed for performance
4. **Add Authentication:** Implement user auth (Cognito)
5. **AI Agents:** Begin Phase 3 - Multi-agent coaching system

---

**Document Created:** 2025-10-19
**Purpose:** Step-by-step guide for deploying tracking system to AWS
**Author:** Claude Code Assistant
