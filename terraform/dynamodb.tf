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

  name         = "${local.name_prefix}-${each.key}"
  billing_mode = "PAY_PER_REQUEST" # On-demand pricing
  hash_key     = each.value.hash_key

  # Define attributes
  dynamic "attribute" {
    for_each = each.value.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
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
