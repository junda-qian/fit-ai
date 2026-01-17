# Terraform Explained - For Beginners

## What is Terraform?

Imagine you're building a house. Instead of manually hammering every nail, wiring every socket, and painting every wall yourself, you could hand a detailed blueprint to a construction crew and say "build this." Terraform is like that blueprint system, but for cloud infrastructure.

**Terraform** is an "Infrastructure as Code" (IaC) tool that lets you:
- **Write code** to describe what cloud resources you want (servers, databases, storage, etc.)
- **Automatically create** all those resources in the cloud (like AWS, Azure, Google Cloud)
- **Track changes** to your infrastructure over time
- **Replicate environments** easily (create identical dev, test, and production setups)
- **Destroy everything** with a single command when you're done

Think of it as a recipe book for cloud infrastructure. You write down what you want, and Terraform makes it happen.

## Why Use Terraform?

### Without Terraform:
You'd have to:
1. Log into the AWS Console (a web interface)
2. Click through dozens of screens to create a database
3. Manually configure security settings
4. Repeat the same clicks for every environment
5. Hope you didn't forget any steps or make mistakes

### With Terraform:
1. Write code once describing your infrastructure
2. Run `terraform apply`
3. Everything gets created automatically, consistently, every time

## How FitTracker AI Uses Terraform

This fitness app uses Terraform to create **all** its cloud infrastructure on AWS. Here's what gets created:

### Cloud Resources Created:
- **3 Storage Buckets** (like digital file cabinets)
- **1 Serverless Computer** (Lambda function - runs your code without managing servers)
- **9 Databases** (DynamoDB tables - stores user data, workouts, nutrition logs)
- **1 Vector Database** (OpenSearch - for AI-powered health Q&A)
- **1 Content Delivery Network** (CloudFront - makes your website fast globally)
- **1 API Gateway** (the "front door" for your backend)
- **Security Policies** (who can access what)

All of this gets created with a single command: `terraform apply`

---

## Terraform File Structure in This Project

```
terraform/
├── main.tf              ← Core infrastructure (storage, compute, CDN)
├── dynamodb.tf          ← Database tables (9 tables for user data)
├── opensearch.tf        ← Vector database for AI chatbot
├── variables.tf         ← Configuration inputs (like form fields)
├── outputs.tf           ← Important info to display after deployment
├── versions.tf          ← Which version of Terraform to use
└── terraform.tfvars     ← Actual values for your variables
```

---

## File-by-File Breakdown

### 1. `versions.tf` - The Foundation
**What it does:** Defines which version of Terraform and cloud providers to use.

**Analogy:** Like specifying "I need a Phillips screwdriver, not a flathead" before starting a project.

**What's in it:**
- Requires Terraform version 1.0 or higher
- Uses AWS as the cloud provider (version 6.x)
- Sets up two AWS regions:
  - Default region (from your AWS CLI configuration)
  - Tokyo region (ap-northeast-1) for SSL certificates

**Why it matters:** Ensures everyone on your team uses compatible tools.

---

### 2. `variables.tf` - The Configuration Template
**What it does:** Defines all the settings you can customize (like a settings menu).

**Analogy:** Like a form with blank fields that you'll fill out later.

**Variables defined:**
- `project_name` - Name prefix for all resources (must be lowercase, numbers, hyphens only)
- `environment` - Which environment: dev, test, or prod
- `bedrock_model_id` - Which AI model to use (default: amazon.nova-micro-v1:0)
- `lambda_timeout` - How long your server code can run (default: 60 seconds)
- `api_throttle_burst_limit` - Max API requests in a burst (default: 10)
- `api_throttle_rate_limit` - Steady-state API requests per second (default: 5)
- `use_custom_domain` - Whether to use a custom domain like "myapp.com" (default: false)
- `root_domain` - Your custom domain name (if using one)
- `usda_api_key` - API key for food database searches (marked as sensitive)

**Why it matters:** You can deploy the same infrastructure with different settings (e.g., small for dev, large for production).

---

### 3. `terraform.tfvars` - The Actual Values
**What it does:** Fills in the blank fields from `variables.tf` with real values.

**Analogy:** Like filling out a form with your actual information.

**Current values:**
```
project_name             = "health-chatbot"
environment              = "dev"
bedrock_model_id         = "amazon.nova-lite-v1:0"
lambda_timeout           = 120 seconds
api_throttle_burst_limit = 10 requests
api_throttle_rate_limit  = 5 requests/second
use_custom_domain        = false
usda_api_key             = "mrACeMiM6cd1HrbGemjTE9GuBqszVAMKpYqv1UYN"
```

**Why it matters:** Separates configuration from code, so you can have different `.tfvars` files for dev/prod.

---

### 4. `main.tf` - The Core Infrastructure
**What it does:** Creates the main cloud resources for the fitness app.

**Analogy:** The main blueprint showing the foundation, walls, and roof of your house.

**Resources created:**

#### Storage (S3 Buckets - like cloud file cabinets)
1. **Memory Bucket** - Stores conversation history with the AI chatbot
2. **Documents Bucket** - Stores health PDFs for the AI + the Lambda deployment package
3. **Frontend Bucket** - Hosts the website (Next.js app)

#### Compute (Lambda - serverless computer)
- **Lambda Function** - Runs your Python FastAPI backend (247MB)
  - Timeout: 120 seconds
  - Runtime: Python 3.12
  - Connected to all databases and AI services
  - Environment variables configured (API keys, database names, etc.)

#### API Gateway (The "Front Door")
- **HTTP API** - Routes web requests to your Lambda function
- **30+ API routes** defined:
  - `/health` - Health check
  - `/chat` - Chatbot endpoint
  - `/api/nutrition/logs` - Nutrition tracking
  - `/api/workout/logs` - Workout tracking
  - `/api/user-profile` - User profiles
  - etc.

#### Content Delivery Network (CloudFront)
- **CloudFront Distribution** - Makes your website load fast worldwide
  - Caches static files (HTML, CSS, JS)
  - Serves from nearest location to users
  - Redirects HTTP to HTTPS for security
  - Handles 404 errors by serving index.html (for single-page apps)

#### Security (IAM Roles - permission system)
- **Lambda Execution Role** - Gives Lambda permission to:
  - Write logs to CloudWatch
  - Access Amazon Bedrock (AI service)
  - Read/write S3 buckets
  - Read/write DynamoDB tables

#### Optional: Custom Domain (disabled by default)
- If enabled, creates SSL certificate and DNS records
- Lets you use "myapp.com" instead of CloudFront's random URL

**Key Features:**
- All resources are tagged with: Project, Environment, ManagedBy
- Public access blocked on memory/documents buckets (secure)
- Frontend bucket publicly accessible (for website hosting)
- Throttling enabled on API (prevents abuse)

---

### 5. `dynamodb.tf` - The Database Tables
**What it does:** Creates 9 NoSQL database tables to store all app data.

**Analogy:** Like creating 9 different filing cabinets, each for a specific type of document.

**Tables created:**

1. **user_profiles**
   - Stores: User account info, fitness goals, body stats
   - Key: `user_id`

2. **workout_plans**
   - Stores: AI-generated workout plans
   - Key: `id`
   - Index: Search by `user_id` to find all plans for a user

3. **nutrition_logs**
   - Stores: Daily food intake (calories, protein, carbs, fats)
   - Key: `id`
   - Index: Search by `user_id` and `date` to get nutrition for specific days

4. **workout_logs**
   - Stores: Exercise performance (sets, reps, weight)
   - Key: `id`
   - Index: Search by `user_id` and `date`

5. **body_logs**
   - Stores: Body measurements (weight, body fat %, muscle mass)
   - Key: `id`
   - Index: Search by `user_id` and `date`

6. **daily_summaries**
   - Stores: Aggregated daily stats
   - Key: `id`
   - Index: Search by `user_id` and `date`

7. **user_exercises**
   - Stores: User's custom exercises and progression models
   - Key: `id`
   - Index: Search by `user_id`

8. **training_recommendations**
   - Stores: AI-generated training advice (when to deload, increase weight, etc.)
   - Key: `id`
   - Index: Search by `user_id` and `created_at`

9. **training_progress_summaries**
   - Stores: Weekly training progress summaries
   - Key: `id`
   - Index: Search by `user_id` and `week`

**Key Features:**
- **Billing Mode:** PAY_PER_REQUEST (only pay when you use it, no idle costs)
- **Encryption:** All tables encrypted at rest
- **Backups:** Point-in-time recovery enabled (can restore to any moment)
- **Indexes (GSI):** Allow fast searches by user_id + date/week

**Why DynamoDB?**
- No servers to manage
- Scales automatically
- Pay only for what you use
- Fast read/write performance

---

### 6. `opensearch.tf` - The Vector Database for AI
**What it does:** Creates a specialized database for AI-powered health Q&A using RAG (Retrieval-Augmented Generation).

**Analogy:** Like a super-smart librarian that can find relevant health information from 4,484 medical documents using AI similarity search.

**What's created:**

1. **Encryption Policy** - Encrypts data at rest using AWS-managed keys

2. **Network Policy** - Allows public access (so Lambda can connect)

3. **Access Policy** - Defines who can read/write:
   - Lambda function (for the chatbot)
   - IAM user "aiengineer" (for manual data management)

4. **OpenSearch Collection** - The actual vector database
   - Type: VECTORSEARCH (optimized for AI embeddings)
   - Stores: 4,484 medical document embeddings (1536 dimensions each)
   - Used by: Coach Orchestrator chatbot for evidence-based health answers

**How it works:**
1. User asks: "What's the best diet for muscle gain?"
2. Lambda converts question to a 1536-dimension vector (using Bedrock Titan)
3. OpenSearch finds 5 most similar medical document chunks
4. GPT-4 uses those chunks to generate an evidence-based answer

**Cost Warning:**
The file includes this comment:
```
# NOTE: OpenSearch costs ~$700+/month even when empty
```
This is why the app sometimes disables OpenSearch to save costs and uses FAISS (a free alternative) instead.

---

### 7. `outputs.tf` - The Results Display
**What it does:** After Terraform creates everything, it displays important information you'll need.

**Analogy:** Like a construction crew handing you the keys and the address after building your house.

**Information displayed:**

1. **api_gateway_url**
   - Example: `https://qj0nsm3f9a.execute-api.us-east-1.amazonaws.com`
   - Use this to call your backend API

2. **cloudfront_url**
   - Example: `https://d1gigxpg1cktct.cloudfront.net`
   - Use this to access your website

3. **s3_frontend_bucket**
   - Example: `health-chatbot-dev-frontend-123456789`
   - Where your Next.js website files are stored

4. **s3_memory_bucket**
   - Example: `health-chatbot-dev-memory-123456789`
   - Where chatbot conversations are saved

5. **s3_documents_bucket**
   - Example: `health-chatbot-dev-documents-123456789`
   - Where health PDFs and Lambda code are stored

6. **lambda_function_name**
   - Example: `health-chatbot-dev-api`
   - Name of your backend function

7. **custom_domain_url** (if enabled)
   - Example: `https://myfitnessapp.com`
   - Your custom domain (if configured)

**Why it matters:** You need these URLs to:
- Configure your frontend to talk to the backend
- Access your deployed website
- Debug issues
- Integrate with other services

---

## How Everything Works Together

### The Deployment Flow:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. YOU RUN: terraform apply                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TERRAFORM READS:                                         │
│    • variables.tf (what can be configured)                  │
│    • terraform.tfvars (actual values)                       │
│    • versions.tf (which providers to use)                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TERRAFORM CREATES (in order):                            │
│    ① S3 Buckets (storage first)                             │
│    ② DynamoDB Tables (databases)                            │
│    ③ OpenSearch Collection (vector DB) - 40min!             │
│    ④ IAM Role (permissions)                                 │
│    ⑤ Lambda Function (backend code)                         │
│    ⑥ API Gateway (routes)                                   │
│    ⑦ CloudFront Distribution (CDN)                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. TERRAFORM DISPLAYS:                                      │
│    • CloudFront URL (your website)                          │
│    • API Gateway URL (your backend)                         │
│    • Bucket names                                           │
└─────────────────────────────────────────────────────────────┘
```

### The App Request Flow:

```
User visits website
    ↓
CloudFront (CDN) serves Next.js frontend
    ↓
User clicks "Ask Coach a question"
    ↓
Frontend sends POST to API Gateway
    ↓
API Gateway routes to Lambda function
    ↓
Lambda runs FastAPI code
    ├→ Reads from DynamoDB (user data)
    ├→ Searches OpenSearch (health knowledge)
    ├→ Calls Bedrock AI (GPT-4 for answer)
    └→ Saves conversation to S3
    ↓
Response sent back to user
```

---

## Common Terraform Commands

### View planned changes (dry run)
```bash
terraform plan
```
Shows what will be created/changed/destroyed WITHOUT actually doing it.

### Create/update infrastructure
```bash
terraform apply
```
Creates or updates resources to match your code. Asks for confirmation first.

### Destroy everything
```bash
terraform destroy
```
Deletes ALL resources created by Terraform. Irreversible!

### Check current state
```bash
terraform show
```
Displays the current state of your infrastructure.

### List all resources
```bash
terraform state list
```
Shows all resources Terraform is managing.

### Initialize Terraform (first time)
```bash
terraform init
```
Downloads provider plugins (AWS, etc.) and sets up Terraform.

---

## Key Terraform Concepts

### Resources
A "resource" is a single cloud component (e.g., a database, a storage bucket, a server).

Example:
```hcl
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-unique-bucket-name"
}
```

### Data Sources
Read-only information about existing resources (e.g., "What's my AWS account ID?").

Example:
```hcl
data "aws_caller_identity" "current" {}
# Now you can use: data.aws_caller_identity.current.account_id
```

### Variables
Inputs you can customize (like function parameters).

Example:
```hcl
variable "environment" {
  type    = string
  default = "dev"
}
```

### Outputs
Values to display after deployment (like function return values).

Example:
```hcl
output "website_url" {
  value = aws_cloudfront_distribution.main.domain_name
}
```

### Locals
Calculated values used within your Terraform code.

Example:
```hcl
locals {
  name_prefix = "${var.project_name}-${var.environment}"
  # Result: "health-chatbot-dev"
}
```

### Depends On
Explicitly define dependencies between resources.

Example:
```hcl
resource "aws_lambda_function" "api" {
  # ... config ...
  depends_on = [aws_cloudfront_distribution.main]
}
```
This ensures CloudFront is created before Lambda.

---

## Cost Breakdown

This infrastructure uses a **serverless, pay-per-use model**:

### Free/Cheap Resources:
- **S3 Storage:** ~$0.023/GB/month (minimal for small app)
- **DynamoDB:** Pay-per-request (free tier: 25GB storage, 25 WCU, 25 RCU)
- **Lambda:** Free tier: 1M requests/month + 400,000 GB-seconds compute
- **CloudFront:** Free tier: 1TB outbound data/month
- **API Gateway:** $1 per million requests

### Expensive Resource:
- **OpenSearch Serverless:** ~$700+/month (even when empty!)
  - This is why the code has logic to disable it and use FAISS locally instead

### Estimated Monthly Cost:
- **With OpenSearch:** ~$720/month
- **Without OpenSearch:** ~$5-20/month (depending on usage)

---

## Security Features Built-In

1. **Encryption:**
   - All DynamoDB tables encrypted at rest
   - OpenSearch encrypted
   - S3 buckets can be encrypted

2. **Least Privilege Access:**
   - Lambda only gets permissions it needs
   - S3 buckets block public access (except frontend)

3. **HTTPS Everywhere:**
   - CloudFront forces HTTPS
   - API Gateway supports HTTPS

4. **Backup & Recovery:**
   - DynamoDB point-in-time recovery enabled
   - Can restore to any moment in the past 35 days

5. **API Throttling:**
   - Rate limiting prevents abuse
   - Burst limit: 10 requests
   - Steady rate: 5 requests/second

---

## Environments (Dev vs Prod)

This project supports multiple environments using **Terraform Workspaces**.

### How it works:
```bash
# Create/switch to dev environment
terraform workspace select dev

# Create/switch to prod environment
terraform workspace select prod
```

Each workspace has:
- Separate infrastructure (different databases, different Lambda functions)
- Same code, different values in `terraform.tfvars`
- Isolated for safety (changes in dev don't affect prod)

### Naming Convention:
All resources are prefixed with: `${project_name}-${environment}`

Examples:
- Dev: `health-chatbot-dev-api`
- Prod: `health-chatbot-prod-api`

---

## Troubleshooting Common Issues

### "Error: Bucket already exists"
**Problem:** S3 bucket names must be globally unique across ALL AWS accounts.

**Solution:** Change `project_name` in `terraform.tfvars` to something more unique.

---

### "Error: OpenSearch creation timeout"
**Problem:** OpenSearch takes 30-40 minutes to create.

**Solution:** Increase timeout or disable OpenSearch if not needed.

---

### "Error: Lambda function too large"
**Problem:** Lambda deployment package is >250MB (current: 247MB).

**Solution:** Optimize dependencies or use Lambda layers.

---

### "Error: Permission denied"
**Problem:** IAM role doesn't have required permissions.

**Solution:** Check `aws_iam_role_policy` resources in `main.tf`.

---

## Best Practices

1. **Always run `terraform plan` before `apply`**
   - Review changes before executing

2. **Use version control (Git)**
   - Track changes to your Terraform code
   - Never commit `terraform.tfstate` (contains secrets!)

3. **Store state remotely (not done in this project)**
   - Use S3 + DynamoDB for state locking
   - Prevents conflicts when working in teams

4. **Use variables for everything that might change**
   - Don't hardcode values in resources

5. **Tag all resources**
   - Makes cost tracking and organization easier

6. **Test in dev before applying to prod**
   - Use workspaces to separate environments

7. **Keep sensitive values in `.tfvars`**
   - Never commit API keys to Git
   - Use `.gitignore` for `terraform.tfvars`

---

## Summary

**Terraform** is a powerful tool that lets you define cloud infrastructure in code. For the FitTracker AI app, it:

1. Creates 3 S3 buckets for storage
2. Creates 9 DynamoDB tables for data
3. Creates a vector database for AI (OpenSearch)
4. Creates a Lambda function to run your backend
5. Creates an API Gateway to route requests
6. Creates a CloudFront CDN for fast website delivery
7. Sets up all security policies and permissions

All with a single command: `terraform apply`

When you're done, `terraform destroy` deletes everything.

This approach is:
- **Reproducible** - Same code always creates same infrastructure
- **Version-controlled** - Track changes over time
- **Collaborative** - Teams can work together
- **Efficient** - No manual clicking in AWS Console

Think of Terraform as "programmable cloud infrastructure" - you write code, and the cloud gets built automatically!
