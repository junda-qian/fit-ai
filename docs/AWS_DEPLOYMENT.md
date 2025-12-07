# AWS Deployment Guide

Complete guide for deploying and destroying the Fit Tracker application on AWS.

---

## 🚀 Quick Reference

### Deploy
```bash
cd /Users/jundaqian/projects/fit-ai/fit-tracker
./scripts/deploy.sh dev
python3 scripts/insert_sample_data_to_dynamodb.py
```

### Destroy
```bash
cd /Users/jundaqian/projects/fit-ai/fit-tracker
./scripts/destroy.sh dev
```

---

## Prerequisites

- AWS CLI configured with valid credentials
- Docker running (required for Lambda packaging)
- Node.js and npm installed
- Python 3.9+ installed
- Terraform installed

---

## 🚀 Deployment

### Step 1: Deploy Infrastructure

From the project root, run:

```bash
cd /Users/jundaqian/projects/fit-ai/fit-tracker
./scripts/deploy.sh dev
```

**What this does:**
- Builds Lambda deployment package using Docker
- Creates/updates Terraform workspace for `dev` environment
- Deploys AWS infrastructure:
  - DynamoDB tables (9 tables)
  - Lambda function
  - API Gateway
  - S3 buckets (frontend, memory, documents)
  - CloudFront distribution
- Builds Next.js frontend
- Uploads frontend to S3

**Expected duration:** 5-10 minutes

---

### Step 2: Insert Sample Data

After deployment completes successfully, insert 90 days of sample data:

```bash
python3 scripts/insert_sample_data_to_dynamodb.py
```

**What this creates:**
- 1 demo user profile
- 10 exercise configurations
- 91 body logs (daily weight + weekly skinfolds)
- ~190 nutrition logs (meals across 90 days)
- ~47 workout logs (4x/week training)
- 91 daily summaries

**Demo User ID:** `demo_user_90day`

---

### Step 3: Get Deployment URLs

Get your CloudFront URL:

```bash
cd terraform
terraform output cloudfront_url
```

Get your API Gateway URL:

```bash
terraform output api_gateway_url
```

---

### Step 4: Access the Application

1. **Open the CloudFront URL** in your browser

2. **Set the demo user ID** in browser console:
   - Press `F12` to open Developer Tools
   - Go to the **Console** tab
   - Run this command:
     ```javascript
     localStorage.setItem('fit_tracker_user_id', 'demo_user_90day')
     ```

3. **Refresh the page** (`F5` or `Cmd+R`)

4. **Navigate and test:**
   - **Dashboard:** View today's summary
   - **Progress:** See 90-day charts and trends
   - **Nutrition Logs:** Browse meal history
   - **Workouts:** View workout logs
   - **Progress Analyzers:**
     - Click "Get Recommendation" for nutrition analysis
     - Click "Generate Weekly Summary" for training analysis

---

## 🧪 Verification

Test the analyzers directly via API:

### Test Training Analyzer

```bash
API_URL=$(cd terraform && terraform output -raw api_gateway_url)
curl -X POST "$API_URL/api/training/weekly-summary" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_90day"}'
```

**Expected response:**
```json
{
  "summary": {
    "overall_strength_trend": "stable",
    "exercises_analyzed": 10,
    "data_quality": "good"
  }
}
```

### Test Nutrition Analyzer

```bash
curl -X POST "$API_URL/api/nutrition/analyze" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_90day"}'
```

**Expected response:**
```json
{
  "recommendation": {
    "recommended_calories": 2000,
    "adjustment_category": "decrease"
  }
}
```

---

## 🗑️ Destroy Infrastructure

### Quick Destroy

To destroy all AWS resources:

```bash
cd /Users/jundaqian/projects/fit-ai/fit-tracker
./scripts/destroy.sh dev
```

**What this does:**
1. Empties all S3 buckets:
   - Frontend bucket
   - Memory bucket
   - Documents bucket
2. Destroys all Terraform-managed resources:
   - CloudFront distribution (~4 minutes)
   - API Gateway
   - Lambda function
   - DynamoDB tables
   - S3 buckets
   - IAM roles

**Expected duration:** 5-8 minutes (CloudFront takes longest)

---

## 📁 Project Structure

```
fit-tracker/
├── scripts/
│   ├── deploy.sh                          # Main deployment script
│   ├── destroy.sh                         # Destruction script
│   ├── insert_sample_data_to_dynamodb.py  # Sample data generator
│   ├── reset_demo_data.py                 # Clean demo user data
│   └── verify_sample_data.py              # Verify inserted data
├── terraform/
│   ├── main.tf                            # Main infrastructure
│   ├── dynamodb.tf                        # DynamoDB tables
│   ├── variables.tf                       # Input variables
│   └── outputs.tf                         # Output values
├── backend/
│   ├── server.py                          # FastAPI application
│   ├── deploy.py                          # Lambda packaging script
│   └── database.py                        # DynamoDB client
├── frontend/
│   └── app/                               # Next.js application
└── ai_agents/
    ├── nutrition_specialist/              # Nutrition analyzer
    └── training_specialist/               # Training analyzer
```

---

## 🔧 Troubleshooting

### Issue: "BucketNotEmpty" error during destroy

**Solution:** The destroy script now automatically empties buckets. If this still occurs:

```bash
# Manually empty buckets
aws s3 rm s3://health-chatbot-dev-frontend-$(aws sts get-caller-identity --query Account --output text) --recursive
aws s3 rm s3://health-chatbot-dev-memory-$(aws sts get-caller-identity --query Account --output text) --recursive
aws s3 rm s3://health-chatbot-dev-documents-$(aws sts get-caller-identity --query Account --output text) --recursive

# Then run destroy again
./scripts/destroy.sh dev
```

### Issue: Frontend shows 404 errors

**Cause:** Sample data not inserted yet

**Solution:**
```bash
python3 scripts/insert_sample_data_to_dynamodb.py
```

### Issue: Analyzers return "insufficient_data"

**Cause:** Either no sample data or exercise configurations missing

**Solution:**
1. Verify sample data exists:
   ```bash
   python3 scripts/verify_sample_data.py
   ```
2. Re-insert if needed:
   ```bash
   python3 scripts/reset_demo_data.py
   python3 scripts/insert_sample_data_to_dynamodb.py
   ```

### Issue: Docker not running during deployment

**Error:** `Cannot connect to the Docker daemon`

**Solution:**
1. Start Docker Desktop
2. Wait for Docker to fully start
3. Run deployment again

---

## 🌍 Environments

The deployment supports multiple environments:

- **dev** (default): Development environment
- **test**: Testing environment
- **prod**: Production environment

### Deploy to Different Environment

```bash
./scripts/deploy.sh prod
./scripts/destroy.sh prod
```

---

## 💰 Cost Estimation

Approximate AWS costs for **dev** environment with sample data:

| Service | Usage | Est. Monthly Cost |
|---------|-------|-------------------|
| DynamoDB | 9 tables, on-demand | $1-2 |
| Lambda | ~100 requests/day | < $0.50 |
| API Gateway | ~100 requests/day | < $0.50 |
| S3 | 3 buckets, minimal storage | < $0.50 |
| CloudFront | Minimal traffic | < $1 |
| **Total** | | **~$3-5/month** |

**Note:** Costs increase with actual usage. The sample data deployment uses minimal resources.

---

## 🔐 Security Notes

- All S3 buckets have public access blocked by default
- Frontend bucket allows CloudFront access only
- API Gateway has rate limiting enabled (5 req/s, 10 burst)
- Lambda has 60-second timeout
- DynamoDB uses on-demand billing (scales automatically)

---

## 📝 Sample Data Details

The sample data represents a realistic 90-day fitness journey:

### User Profile
- **Goal:** Weight loss
- **Training Status:** Intermediate
- **Starting Weight:** 85.0 kg
- **Final Weight:** ~79-80 kg (5-6 kg loss)
- **Body Fat:** Declining trend via skinfold measurements

### Nutrition Data
- **Compliance:** 80-85% (realistic adherence)
- **Calories:** ~2200/day target
- **Weekends:** Higher calorie days (realistic variation)
- **Missing Days:** ~15-20% (realistic tracking gaps)

### Training Data
- **Frequency:** 4x/week (Upper/Lower split)
- **Exercises:** 10 configured exercises
- **Progression Models:**
  - Linear progressive (Bench, Squat)
  - Rep range (accessories)
- **Missed Sessions:** ~10% (realistic training consistency)

### Analyzers
- **Nutrition Analyzer:** Uses last 14 days of data
- **Training Analyzer:** Analyzes last 14 days of workouts
- **Confidence:** Scales with data quantity (5+ exercises = 100%)

---

## 🔄 Update Deployment

To update an existing deployment with code changes:

```bash
# No need to destroy - just redeploy
./scripts/deploy.sh dev
```

Terraform will:
- Update Lambda function code
- Update frontend in S3
- Invalidate CloudFront cache
- Leave DynamoDB data intact

---

## 📚 Additional Resources

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Static Exports](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
- [AWS DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

---

## ✅ Deployment Checklist

- [ ] Docker is running
- [ ] AWS CLI is configured
- [ ] Run `./scripts/deploy.sh dev`
- [ ] Wait for deployment to complete
- [ ] Run `python3 scripts/insert_sample_data_to_dynamodb.py`
- [ ] Get CloudFront URL from terraform output
- [ ] Open URL in browser
- [ ] Set localStorage user ID in console
- [ ] Refresh page
- [ ] Test both analyzers
- [ ] Verify 90 days of data appears

---

**Last Updated:** December 2025
