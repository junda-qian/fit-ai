# Building AI Agents with Coding Assistants: A Practical Journey

## 📋 Step 1: DESIGN

### How to Do It

**1. Define Agent Responsibilities**
- Identify distinct domains (Coach, Nutrition, Training)
- Map user needs to agent capabilities
- Design agent interaction patterns

**2. Choose the Right LLMs**
- Evaluate models for each use case
- Consider cost vs. quality tradeoffs
- Plan for model provider diversity

**3. Design Data Architecture**
- Map user journeys to data requirements
- Design database schema with access patterns
- Plan for conversation memory and context

**4. Sketch Infrastructure**
- Choose deployment platform (serverless vs. containers)
- Plan for scalability and cost optimization
- Design API architecture

### What to Be Careful About (Lessons Learned)

**❌ Mistake 1: Assuming Everything Needs AI**
- **Problem**: Initially designed Energy Calculator to use LLM for "intelligent" calculations
- **Reality**: TDEE calculation uses well-established formulas (Cunningham BMR)
- **Solution**: Used deterministic Python code instead - faster, cheaper, more reliable
- **Lesson**: Ask "Does this ACTUALLY need AI?" before committing to LLM usage

```python
# ❌ Wrong: Using expensive LLM for deterministic math
bedrock.converse("Calculate my TDEE based on 70kg, 175cm...")

# ✅ Right: Use formulas directly
def calculate_cunningham_bmr(fat_free_mass_kg: float) -> float:
    return 370 + (21.6 * fat_free_mass_kg)
```

**❌ Mistake 2: Using AI When Deterministic Algorithms Suffice**
- **Problem**: Initially planned to use Bedrock Nova for Nutrition/Training analysis
- **Cost Issue**: Would be $30-50/month for automated weekly analyses
- **Reality Check**: Nutrition/training progression follows well-established rules
- **Solution**: Hybrid strategy
  - **OpenAI GPT-4**: Coach Agent (conversational quality matters)
  - **Bedrock Nova**: Workout Planner only (creative planning benefits from AI)
  - **Deterministic Algorithms**: Nutrition/Training Specialists (100% reliable, $0 cost)
- **Lesson**: Question if each component ACTUALLY needs AI - often deterministic code is better

**❌ Mistake 3: Incomplete Agent Trigger Design**
- **Problem**: Training Agent initially designed as "event-driven only"
- **Gap**: Missed weekly trend analysis for users who don't work out
- **Solution**: Dual-trigger pattern
  1. **Post-workout trigger**: Immediate session feedback
  2. **Weekly scheduled**: Monday 5:55 AM UTC for trend analysis
- **Lesson**: Consider both reactive AND proactive agent behaviors

**❌ Mistake 4: Poor Data Access Pattern Planning**
- **Problem**: Querying DynamoDB without GSI (Global Secondary Index)
- **Result**: Expensive table scans, slow queries
- **Solution**: Designed 4 GSI patterns upfront:
  - `UserIdDateIndex` (nutrition_logs, workout_logs, body_logs)
  - `UserIdIndex` (workout_plans, user_exercises)
  - `UserIdWeekIndex` (training_progress_summaries)
  - `UserIdCreatedAtIndex` (training_recommendations)
- **Lesson**: DynamoDB query patterns MUST be designed before building

**🔧 Tool Usage with Claude Code:**
- **Ask Claude to**: "Analyze my agent requirements and suggest LLM choices"
- **Ask Claude to**: "Design DynamoDB schema with access patterns for [use case]"
- **Ask Claude to**: "Review this design - what needs AI vs. deterministic code?"

---

## 🛠️ Step 2: BUILDING

### How to Do It

**1. Set Up Development Environment**
- Local backend (FastAPI + FAISS)
- Local frontend (Next.js dev server)
- Environment variable management

**2. Implement AI Agents**
- Create agent classes with clear interfaces
- Implement tool/function calling
- Build RAG pipeline (embeddings + vector search)

**3. Build API Layer**
- FastAPI endpoints for each feature
- Request/response validation
- Error handling and retries

**4. Develop Frontend**
- Component-based UI (React)
- API integration
- State management

### What to Be Careful About (Lessons Learned)

**❌ Mistake 1: Lambda Package Size Explosion**
- **Problem**: Initial Lambda package = 1.2GB (way over 250MB limit)
- **Cause**: Installing all dependencies including development tools
- **Solution**: Created separate `requirements-lambda.txt`
  - Excluded: `pytest`, `black`, `mypy`, dev tools
  - Used Docker with official Lambda Python 3.12 image
  - Platform-specific builds: `--platform manylinux2014_x86_64`
- **Final Size**: 247MB (within limits!)
- **Lesson**: Lambda has strict size limits - optimize dependencies early

```python
# backend/deploy.py
subprocess.run([
    "docker", "run", "--rm",
    "-v", f"{os.getcwd()}:/var/task",
    "--platform", "linux/amd64",  # ✅ Critical for Lambda compatibility
    "public.ecr.aws/lambda/python:3.12",
    "/bin/sh", "-c",
    "pip install --target /var/task/lambda-package -r /var/task/requirements-lambda.txt --platform manylinux2014_x86_64 --only-binary=:all:"
], check=True)
```

**❌ Mistake 2: Hardcoding LLM API Calls**
- **Problem**: Tightly coupled code with OpenAI SDK in early prototypes
- **Issue**: Switching providers or using deterministic code required rewrites
- **Solution**: Clear separation between AI and non-AI components

```python
# ❌ Wrong: Hardcoded LLM when algorithm suffices
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    messages=[{"role": "user", "content": "Calculate optimal deficit..."}]
)

# ✅ Right: Deterministic algorithm for nutrition analysis
class NutritionSpecialist:
    def analyze(self, user_profile, weight_trend, nutrition_summary):
        # Pure Python - no LLM needed!
        maintenance = estimate_maintenance_calories(
            nutrition_summary.avg_calories,
            weight_trend.weekly_rate_pct
        )
        optimal_deficit = calculate_optimal_deficit(
            user_profile.body_fat_pct,
            user_profile.sex
        )
        # Returns structured recommendation (100% reliable)
```

**❌ Mistake 3: Insufficient RAG Context Quality**
- **Problem**: RAG returned irrelevant medical documents
- **Debugging**:
  1. Checked embedding model (was using wrong dimensions)
  2. Verified chunk size (1000 chars too large for some content)
  3. Added source tracking for debugging
- **Solution**:
  - Used Bedrock Titan V1 (1536 dimensions)
  - Reduced chunk size to 1000 chars with 200 overlap
  - Added metadata: `{source, page, chunk_id}`
- **Lesson**: RAG quality depends on embeddings + chunking + retrieval tuning

**❌ Mistake 4: Missing Error Handling in Async Agents**
- **Problem**: Nutrition Agent silently failed on Mondays
- **Cause**: Missing user data (new users with <14 days of logs)
- **Solution**: Added graceful degradation

```python
# ✅ Proper error handling
try:
    nutrition_data = fetch_last_14_days(user_id)
    if len(nutrition_data) < 7:
        return {
            "status": "insufficient_data",
            "message": "Need at least 7 days of logs for analysis"
        }
    analysis = agent.analyze(nutrition_data)
except Exception as e:
    logger.error(f"Nutrition agent failed: {e}")
    return {"status": "error", "message": str(e)}
```

**❌ Mistake 5: Workout Planner Hallucinations**
- **Problem**: AI generated invalid exercise names
- **Issue**: No validation of LLM output
- **Solution**: Retry with validation loop (max 5 attempts)

```python
# ai_agents/workout_planner.py
for attempt in range(max_retries):
    plan = self.call_bedrock_for_workout(prompt)

    # ✅ Validate against known exercise database
    validation = self.validate_workout_plan(plan, exercise_config)

    if validation["is_valid"]:
        return plan
    else:
        # Retry with validation errors in prompt
        prompt += f"\nPrevious attempt failed: {validation['errors']}"
```

**🔧 Tool Usage with Claude Code:**
- **Ask Claude to**: "Help me debug why RAG is returning irrelevant results"
- **Ask Claude to**: "Refactor this to support multiple LLM providers"
- **Ask Claude to**: "Add retry logic with exponential backoff for this API call"

---

## 🚀 Step 3: DEPLOY

### How to Do It

**1. Containerize for Lambda**
- Use official AWS Lambda base images
- Build platform-specific dependencies
- Create deployment package

**2. Infrastructure as Code (Terraform)**
- Define all AWS resources
- Manage environments (dev/prod)
- Version control infrastructure

**3. Automate Deployment**
- Build scripts for repeatable deployments
- Environment configuration management
- Frontend static export to S3

**4. Set Up Monitoring**
- CloudWatch logs
- Error tracking
- Performance metrics

### What to Be Careful About (Lessons Learned)

**❌ Mistake 1: Next.js Routing Breaks on S3/CloudFront**
- **Problem**: `/calculator` → 404 error on CloudFront
- **Cause**: Next.js exports `calculator.html`, but S3 expects `calculator/index.html`
- **CloudFront behavior**: Tries to serve `calculator` as directory
- **Solution**: Post-build script to fix directory structure

```bash
# scripts/deploy.sh - Frontend deployment fix
cd out
for page in calculator chatbot workout-planner; do
  if [ -f "$page.html" ]; then
    mkdir -p "$page"
    cp "$page.html" "$page/index.html"  # ✅ S3 routing fix
  fi
done
```

**Before fix:**
```
out/
├── calculator.html     ❌ CloudFront can't route
├── chatbot.html
└── index.html
```

**After fix:**
```
out/
├── calculator/
│   └── index.html      ✅ /calculator → calculator/index.html
├── chatbot/
│   └── index.html      ✅ /chatbot → chatbot/index.html
└── index.html
```

**❌ Mistake 2: Terraform Destroy Fails on Non-Empty S3 Buckets**
- **Problem**: `terraform destroy` errors because S3 buckets contain objects
- **AWS Policy**: Cannot delete non-empty buckets
- **Solution**: Pre-destroy bucket emptying script

```bash
# scripts/destroy.sh
echo "📦 Emptying S3 buckets..."
for bucket in frontend memory documents; do
    aws s3 rm "s3://${BUCKET_NAME}/" --recursive
    echo "✓ $bucket bucket emptied"
done

terraform destroy -auto-approve
```

**❌ Mistake 3: Environment Variable Confusion**
- **Problem**: Production frontend calling localhost API
- **Cause**: Forgot to set `NEXT_PUBLIC_API_URL` for production build
- **Impact**: Users see blank pages (CORS errors)
- **Solution**: Automated environment injection in deploy script

```bash
# scripts/deploy.sh
API_URL=$(terraform output -raw api_gateway_url)

# ✅ Create production env file BEFORE build
echo "NEXT_PUBLIC_API_URL=$API_URL" > frontend/.env.production

cd frontend
npm run build  # Now uses correct API URL
```

**❌ Mistake 4: Lambda Cold Start Timeout**
- **Problem**: First request after 5+ minutes → 30s timeout
- **Cause**: Large Lambda package (247MB) takes ~10s to cold start
- **Initial timeout**: 30 seconds (not enough)
- **Solution**: Increased to 120 seconds

```hcl
# terraform/main.tf
resource "aws_lambda_function" "api" {
  timeout = 120  # ✅ Increased from 30s
  memory_size = 1024  # Also increased memory for faster init
}
```

**❌ Mistake 5: Missing Terraform Workspace Management**
- **Problem**: `terraform apply` overwrites dev environment during prod deploy
- **Solution**: Proper workspace isolation

```bash
# scripts/deploy.sh
ENVIRONMENT=${1:-dev}

if ! terraform workspace list | grep -q "$ENVIRONMENT"; then
  terraform workspace new "$ENVIRONMENT"  # ✅ Create if missing
else
  terraform workspace select "$ENVIRONMENT"  # ✅ Switch to correct env
fi

terraform apply -var="environment=$ENVIRONMENT"
```

**❌ Mistake 6: Lambda Deployment Package Not Updating**
- **Problem**: Deployed new code but Lambda still runs old version
- **Cause**: Terraform didn't detect S3 object change (same filename)
- **Solution**: Added MD5 hash to trigger updates

```hcl
# terraform/main.tf
resource "aws_lambda_function" "api" {
  s3_bucket = aws_s3_bucket.documents.id
  s3_key    = aws_s3_object.lambda_zip.key

  source_code_hash = filebase64sha256("${path.module}/../backend/lambda-deployment.zip")  # ✅ Force update on change
}
```

**🔧 Tool Usage with Claude Code:**
- **Ask Claude to**: "Debug why my CloudFront routes return 404"
- **Ask Claude to**: "Create a deployment script that handles dev/prod environments"
- **Ask Claude to**: "Why is my Lambda timing out on first request?"

---

## 🔄 Step 4: MAINTENANCE & OPERATION

### How to Do It

**1. Monitor Application Health**
- CloudWatch logs analysis
- Error tracking and alerting
- Performance metrics review

**2. Manage Demo/Test Data**
- Keep demo data fresh and realistic
- Automate data generation
- Regular data resets

**3. Cost Optimization**
- Review AWS billing
- Optimize resource usage
- Shut down unused resources

**4. Documentation & Knowledge Sharing**
- Maintain architecture docs
- Create onboarding materials
- Document lessons learned

### What to Be Careful About (Lessons Learned)

**❌ Mistake 1: Stale Demo Data**
- **Problem**: Demo user showed data from 12/11, but date was 12/14
- **Impact**: Presentation looks unprofessional with outdated data
- **Cause**: Manual data insertion weeks ago
- **Solution**: Regular data refresh workflow

```bash
# ✅ Automated demo data refresh
python3 scripts/reset_demo_data.py    # Clear old data
sleep 5                                 # Wait for DynamoDB
python3 scripts/insert_sample_data_to_dynamodb.py  # Insert fresh data
```

**Lesson**: Demo data needs lifecycle management - automate it!

**❌ Mistake 2: Concurrent Data Operations Causing Duplicates**
- **Problem**: Ran reset and insert scripts at same time → duplicate data
- **Symptom**: "Two weeks worth of data in one week"
- **Solution**: Sequential execution with proper waits

```bash
# ❌ Wrong: Parallel execution
python3 reset_demo_data.py &
python3 insert_sample_data.py &

# ✅ Right: Sequential with wait
python3 reset_demo_data.py && sleep 5 && python3 insert_sample_data.py
```

**❌ Mistake 3: Forgetting What Each Service Does**
- **Problem**: After 2 months, hard to remember architecture for presentation
- **Solution**: Created three documentation files
  1. `ARCHITECTURE_SLIDE.md` - Visual diagrams + AWS resources
  2. `REQUEST_FLOW.md` - Step-by-step request tracing
  3. `REPOSITORY_WALKTHROUGH.md` - Complete codebase guide

**Lesson**: Document while building, not after - future you will thank you!

**❌ Mistake 4: Unclear Cost Attribution**
- **Problem**: AWS bill shows $15 - but what's expensive?
- **Initial guess**: Lambda invocations
- **Reality**: OpenSearch Serverless ($7/month idle cost)
- **Solution**:
  - Reviewed each service cost in billing console
  - Disabled OpenSearch for dev environment
  - Used FAISS locally during development

**Cost breakdown:**
```
OpenSearch Serverless: $7.20/month (idle!)
Lambda: $2.50/month (pay per request)
DynamoDB: $0.80/month (pay per request)
S3: $0.30/month
CloudFront: $0.00 (free tier)
```

**Optimization:**
```bash
# ✅ Use OpenSearch only in production
USE_OPENSEARCH=false  # Local dev with FAISS
USE_OPENSEARCH=true   # Production only
```

**❌ Mistake 5: No Deployment History Tracking**
- **Problem**: "Which version is deployed?" → No idea
- **Impact**: Can't rollback easily
- **Solution**: Git tagging + commit hashes in deployment

```bash
# scripts/deploy.sh
COMMIT_HASH=$(git rev-parse --short HEAD)
echo "🚀 Deploying commit: $COMMIT_HASH"

# Tag successful deployments
git tag "deploy-prod-$(date +%Y%m%d-%H%M%S)-$COMMIT_HASH"
git push origin --tags
```

**❌ Mistake 6: Lost Tribal Knowledge**
- **Problem**: Teammate asks "Why dual-trigger for Training Agent?"
- **Original design**: Only in my head
- **Solution**: Updated specification docs with rationale

```markdown
# docs/agents/TRAINING_AGENT_SPEC.md

## Trigger Pattern: Dual-Trigger

**Why not just event-driven?**
- Users who skip workouts get no feedback

**Why not just scheduled?**
- Active users want immediate post-workout insights

**Solution: Both!**
1. Event trigger: Immediate session feedback
2. Scheduled trigger: Weekly trends (Mon 5:55 AM UTC)
```

**❌ Mistake 7: Demo Deployment Not Matching Local**
- **Problem**: Feature works locally, breaks on AWS
- **Debugging process**:
  1. Check CloudWatch logs
  2. Verify environment variables
  3. Test Lambda function directly
  4. Check IAM permissions
- **Common causes**:
  - Missing environment variable in Terraform
  - Wrong Lambda timeout setting
  - IAM role missing Bedrock permissions

**🔧 Tool Usage with Claude Code:**
- **Ask Claude to**: "Analyze AWS billing and suggest cost optimizations"
- **Ask Claude to**: "Create documentation for this architecture"
- **Ask Claude to**: "Debug why demo data shows duplicates"
- **Ask Claude to**: "Generate presentation materials from codebase"

---

## 🎯 Key Takeaways: Building AI Agents with Coding Assistants

### What Claude Code Excels At:
1. **Architecture Design**: "Design a multi-agent system for fitness coaching"
2. **Code Generation**: Implementing agents, APIs, infrastructure
3. **Debugging**: "Why is my Lambda timing out?" → Systematic investigation
4. **Documentation**: Auto-generating architecture diagrams from codebase
5. **Refactoring**: "Make this work with multiple LLM providers"

### What Still Requires Human Judgment:
1. **Business Logic**: "Should Energy Calculator use AI?" → NO
2. **Cost Tradeoffs**: "Use GPT-4 everywhere?" → Hybrid strategy
3. **User Experience**: Agent trigger patterns, data freshness
4. **Architectural Decisions**: Monolithic Lambda vs microservices

### Workflow That Works:
```
1. Human: Define business requirements
2. Claude Code: Propose technical design
3. Human: Review, refine, approve
4. Claude Code: Implement + test
5. Human: Deploy with Claude's automation scripts
6. Both: Monitor, iterate based on real usage
```

### Final Lesson:
**AI coding assistants amplify your productivity, but you remain the architect.**
- Use Claude Code for speed (10x faster implementation)
- Keep human oversight for decisions (cost, UX, business logic)
- Document everything (Claude can help generate docs from code)
- Iterate based on real-world feedback (Claude helps debug production issues)

---

This presentation structure tells a **story of real development**, showing both successes and failures, with concrete examples from your FitTracker AI journey. The "mistakes → solutions" format is highly engaging and provides actionable lessons for the audience.
