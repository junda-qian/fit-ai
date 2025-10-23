# OpenSearch Serverless Collection for vector database
resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "${local.name_prefix}-encrypt"
  type = "encryption"

  policy = jsonencode({
    Rules = [
      {
        Resource = [
          "collection/${local.name_prefix}-health-docs"
        ]
        ResourceType = "collection"
      }
    ]
    AWSOwnedKey = true
  })
}

resource "aws_opensearchserverless_security_policy" "network" {
  name = "${local.name_prefix}-network"
  type = "network"

  policy = jsonencode([
    {
      Rules = [
        {
          Resource = [
            "collection/${local.name_prefix}-health-docs"
          ]
          ResourceType = "collection"
        }
      ]
      AllowFromPublic = true
    }
  ])
}

resource "aws_opensearchserverless_access_policy" "data_access" {
  name = "${local.name_prefix}-data"
  type = "data"

  policy = jsonencode([
    {
      Rules = [
        {
          Resource = [
            "collection/${local.name_prefix}-health-docs"
          ]
          Permission = [
            "aoss:CreateCollectionItems",
            "aoss:DeleteCollectionItems",
            "aoss:UpdateCollectionItems",
            "aoss:DescribeCollectionItems"
          ]
          ResourceType = "collection"
        },
        {
          Resource = [
            "index/${local.name_prefix}-health-docs/*"
          ]
          Permission = [
            "aoss:CreateIndex",
            "aoss:DeleteIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument"
          ]
          ResourceType = "index"
        }
      ]
      Principal = [
        aws_iam_role.lambda_role.arn,
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:user/aiengineer"
      ]
    }
  ])
}

resource "aws_opensearchserverless_collection" "health_docs" {
  name = "${local.name_prefix}-health-docs"
  type = "VECTORSEARCH"

  tags = local.common_tags

  timeouts {
    create = "40m"
  }

  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network
  ]
}
