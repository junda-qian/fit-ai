# Multi-Agent AI Fitness Coach - System Architecture

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                    USER LAYER                                    │
│                                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Web App    │  │  Mobile App  │  │  iOS/Android │  │   Wearables  │       │
│  │  (Next.js)   │  │ (React Native│  │    Native    │  │  Integration │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │                  │                │
│         └──────────────────┴──────────────────┴──────────────────┘                │
│                                    │                                               │
└────────────────────────────────────┼───────────────────────────────────────────────┘
                                     │
                                     │ HTTPS
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  CDN LAYER                                       │
│                                                                                   │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                        AWS CloudFront (CDN)                                │  │
│  │  • Global edge locations    • Cache static assets    • SSL/TLS           │  │
│  └─────────────────────────┬─────────────────────────────────────────────────┘  │
│                            │                                                      │
└────────────────────────────┼──────────────────────────────────────────────────────┘
                             │
                 ┌───────────┴───────────┐
                 │                       │
                 ▼                       ▼
┌─────────────────────────────┐  ┌─────────────────────────────────────────────────┐
│     STATIC CONTENT          │  │              API LAYER                          │
│                             │  │                                                 │
│  ┌──────────────────────┐  │  │  ┌────────────────────────────────────────┐   │
│  │   Amazon S3          │  │  │  │     AWS API Gateway (HTTP API)         │   │
│  │  • HTML/CSS/JS       │  │  │  │  • Rate limiting  • Auth  • CORS       │   │
│  │  • Images            │  │  │  └─────────────────┬──────────────────────┘   │
│  │  • Static assets     │  │  │                    │                           │
│  └──────────────────────┘  │  │                    ▼                           │
│                             │  │  ┌────────────────────────────────────────┐   │
└─────────────────────────────┘  │  │       AWS Lambda (FastAPI)             │   │
                                 │  │  • Python 3.12    • Request routing    │   │
                                 │  │  • Business logic  • Error handling    │   │
                                 │  └─────────────────┬──────────────────────┘   │
                                 │                    │                           │
                                 └────────────────────┼───────────────────────────┘
                                                      │
                    ┌─────────────────────────────────┼───────────────────────────┐
                    │                                 │                           │
                    ▼                                 ▼                           ▼
┌──────────────────────────────┐  ┌──────────────────────────────┐  ┌─────────────────────────┐
│      DATA LAYER              │  │     AI ORCHESTRATION         │  │   KNOWLEDGE BASE        │
│                              │  │                              │  │                         │
│  ┌────────────────────────┐ │  │  ┌────────────────────────┐ │  │  ┌───────────────────┐ │
│  │  Amazon DynamoDB       │ │  │  │  Agent Orchestrator    │ │  │  │  OpenSearch       │ │
│  │  ┌──────────────────┐  │ │  │  │  (LangGraph/Custom)    │ │  │  │  Serverless       │ │
│  │  │ Users            │  │ │  │  │                        │ │  │  │                   │ │
│  │  ├──────────────────┤  │ │  │  │  ┌──────────────────┐ │ │  │  │  • Exercise DB    │ │
│  │  │ Goals            │  │ │  │  │  │ Shared Context   │ │ │  │  │  • Nutrition info │ │
│  │  ├──────────────────┤  │ │  │  │  │  • User state    │ │ │  │  │  • Workout plans  │ │
│  │  │ Nutrition Logs   │  │ │  │  │  │  • Agent memory  │ │ │  │  │  • RAG docs       │ │
│  │  ├──────────────────┤  │ │  │  │  │  • Decisions log │ │ │  │  │                   │ │
│  │  │ Workout Logs     │  │ │  │  │  └──────────────────┘ │ │  │  └─────────┬─────────┘ │
│  │  ├──────────────────┤  │ │  │  │                        │ │  │            │           │
│  │  │ Body Metrics     │  │ │  │  │  ┌──────────────────┐ │ │  │  ┌─────────▼─────────┐ │
│  │  ├──────────────────┤  │ │  │  │  │ Conflict         │ │ │  │  │ Vector Embeddings │ │
│  │  │ Daily Summaries  │  │ │  │  │  │ Resolver         │ │ │  │  │ (Bedrock Titan)   │ │
│  │  └──────────────────┘  │ │  │  │  └──────────────────┘ │ │  │  └───────────────────┘ │
│  │                        │ │  │  │                        │ │  │                         │
│  │  • Auto-scaling        │ │  │  └───────────┬────────────┘ │  │  • Vector search        │
│  │  • Pay per request     │ │  │              │              │  │  • Semantic matching    │
│  │  • Global tables       │ │  │              │              │  │  • Document retrieval   │
│  └────────────────────────┘ │  └──────────────┼──────────────┘  └─────────────────────────┘
│                              │                 │                                            │
└──────────────────────────────┘                 │                                            │
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    AI AGENT LAYER                                           │
│                              (AWS Bedrock - Claude 3.5 Sonnet)                              │
│                                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐            │
│  │  Analytics Agent     │  │  Nutrition Coach     │  │  Training Coach      │            │
│  │  ┌────────────────┐  │  │  ┌────────────────┐  │  │  ┌────────────────┐  │            │
│  │  │ Data Analysis  │  │  │  │ Meal Planning  │  │  │  │ Workout Design │  │            │
│  │  ├────────────────┤  │  │  ├────────────────┤  │  │  ├────────────────┤  │            │
│  │  │ Trend Detection│  │  │  │ Calorie Adjust │  │  │  │ Volume/Load    │  │            │
│  │  ├────────────────┤  │  │  ├────────────────┤  │  │  ├────────────────┤  │            │
│  │  │ Plateau ID     │  │  │  │ Macro Balance  │  │  │  │ Exercise Select│  │            │
│  │  ├────────────────┤  │  │  ├────────────────┤  │  │  ├────────────────┤  │            │
│  │  │ Goal Progress  │  │  │  │ USDA Search    │  │  │  │ Progressive    │  │            │
│  │  │                │  │  │  │                │  │  │  │ Overload       │  │            │
│  │  └────────────────┘  │  │  └────────────────┘  │  │  └────────────────┘  │            │
│  │                      │  │                      │  │                      │            │
│  │  Tools:              │  │  Tools:              │  │  Tools:              │            │
│  │  • Statistical calc  │  │  • TDEE calculator   │  │  • Volume calc       │            │
│  │  • Query DynamoDB    │  │  • Food database     │  │  • 1RM estimator     │            │
│  │  • Generate insights │  │  • Recipe generation │  │  • Exercise library  │            │
│  └──────────────────────┘  └──────────────────────┘  └──────────────────────┘            │
│                                                                                              │
│  ┌──────────────────────┐  ┌──────────────────────────────────────────────────────────┐  │
│  │  Motivation Agent    │  │              RAG Chatbot Agent                           │  │
│  │  ┌────────────────┐  │  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │ Encouragement  │  │  │  │ • Query OpenSearch for relevant knowledge        │ │  │
│  │  ├────────────────┤  │  │  │ • Answer fitness/nutrition questions             │ │  │
│  │  │ Achievements   │  │  │  │ • Provide educational content                    │ │  │
│  │  ├────────────────┤  │  │  │ • Reference scientific research                  │ │  │
│  │  │ Habit tracking │  │  │  │ • Context-aware responses                        │ │  │
│  │  ├────────────────┤  │  │  └────────────────────────────────────────────────────┘ │  │
│  │  │ Streak mgmt    │  │  │                                                          │  │
│  │  └────────────────┘  │  │  Tools:                                                  │  │
│  │                      │  │  • Vector search      • Document retrieval              │  │
│  │  Tools:              │  │  • Citation generation • Source tracking                │  │
│  │  • Badge system      │  │                                                          │  │
│  │  • Notification gen  │  │                                                          │  │
│  └──────────────────────┘  └──────────────────────────────────────────────────────────┘  │
│                                                                                              │
│  Agent Communication Flow:                                                                  │
│  Analytics → Nutrition/Training (provides data)                                            │
│  Nutrition ↔ Training (coordinate on conflicts)                                            │
│  Motivation → All agents (provides encouragement context)                                  │
│  RAG Chatbot → All agents (provides knowledge)                                             │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL INTEGRATIONS                                          │
│                                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  USDA FoodData   │  │  Stripe Payment  │  │  Email/SMS       │  │  Wearable APIs   │  │
│  │  Central API     │  │  Processing      │  │  (AWS SES/SNS)   │  │  (Fitbit, Apple) │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              MONITORING & OPERATIONS                                        │
│                                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  CloudWatch      │  │  X-Ray Tracing   │  │  Cost Explorer   │  │  AWS Secrets     │  │
│  │  Logs & Metrics  │  │  Distributed     │  │  Budget Alerts   │  │  Manager         │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                                              │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Example: Plateau Detection & Resolution

```
1. User logs weight for 14 days
        ↓
2. Frontend → API Gateway → Lambda → DynamoDB (store weight log)
        ↓
3. User clicks "Get AI Advice" on Progress page
        ↓
4. Frontend → API Gateway → Lambda → Agent Orchestrator
        ↓
5. Orchestrator activates Analytics Agent
        ↓
6. Analytics Agent:
   - Queries DynamoDB (last 4 weeks of data)
   - Calculates trends (weight, calories, workouts)
   - Detects: "Weight plateau: 175lbs for 14 days, eating 1800 cal/day"
        ↓
7. Orchestrator: "Plateau detected, consulting coaches..."
        ↓
8. Nutrition Coach Agent:
   - Reads analytics summary
   - Calculates TDEE
   - Recommends: "Reduce to 1600 cal/day"
   - Generates meal plan using USDA API
        ↓
9. Training Coach Agent (parallel):
   - Reads analytics summary
   - Checks workout volume
   - Recommends: "Add 2 sets to leg day"
        ↓
10. Orchestrator detects conflict:
    - Nutrition wants to CUT calories
    - Training wants to ADD volume (needs more calories)
        ↓
11. Orchestrator queries user goal: "Lose weight" (priority 1)
        ↓
12. Orchestrator resolves:
    - Accept nutrition recommendation (calorie cut)
    - Defer training volume increase
    - Suggest: "Focus on weight loss for 2 weeks, then reassess"
        ↓
13. Motivation Agent generates encouragement:
    - "Plateaus are normal! Let's adjust and keep going."
        ↓
14. Combined response → Lambda → API Gateway → Frontend
        ↓
15. User sees:
    - Explanation of plateau
    - Why calories need adjustment
    - New meal plan
    - Expected timeline to goal
    - Motivational message
        ↓
16. User accepts recommendation
        ↓
17. DynamoDB updated:
    - New calorie target: 1600
    - Decision log: AI recommendation + user acceptance
    - Agent memory: "User prioritizes weight loss over strength gains"
```

---

## Technology Stack Summary

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State**: React Context API
- **Build**: Static export for S3

### Backend
- **API**: FastAPI (Python 3.12)
- **Runtime**: AWS Lambda (serverless)
- **Gateway**: AWS API Gateway (HTTP API)
- **Package**: Mangum (ASGI adapter for Lambda)

### Data Storage
- **Primary DB**: Amazon DynamoDB
  - 6 tables (Users, Goals, Nutrition, Workouts, Body Metrics, Summaries)
  - Global Secondary Indexes for efficient queries
  - On-demand billing
- **Vector Store**: OpenSearch Serverless
  - Stores embeddings for RAG
  - Semantic search for knowledge retrieval
- **Static Assets**: Amazon S3

### AI & ML
- **LLM**: AWS Bedrock (Claude 3.5 Sonnet)
- **Embeddings**: Bedrock Titan Embeddings
- **Orchestration**: Custom (LangGraph optional)
- **Agents**: 5 specialized AI agents

### Infrastructure
- **IaC**: Terraform
- **CDN**: CloudFront
- **Monitoring**: CloudWatch, X-Ray
- **Secrets**: AWS Secrets Manager
- **CI/CD**: Custom deploy scripts

### External APIs
- **Food Data**: USDA FoodData Central API
- **Payments**: Stripe (future)
- **Notifications**: AWS SES/SNS (future)

---

## Cost Estimate (Monthly)

### Development/Testing:
- **DynamoDB**: $5-10 (on-demand, low traffic)
- **Lambda**: $2-5 (mostly free tier)
- **API Gateway**: $1-3
- **S3 + CloudFront**: $1-2
- **OpenSearch Serverless**: $20-30 (minimum OCU)
- **Bedrock API calls**: $10-30 (testing AI agents)
- **Total**: ~$40-80/month

### Production (1000 users):
- **DynamoDB**: $50-100 (increased reads/writes)
- **Lambda**: $10-20 (more invocations)
- **API Gateway**: $5-10
- **S3 + CloudFront**: $5-10 (more traffic)
- **OpenSearch Serverless**: $50-80 (more OCU)
- **Bedrock API calls**: $200-400 (user AI interactions)
- **Total**: ~$320-620/month
- **Per user**: $0.32-0.62/month
- **Revenue target**: $15/user/month = 95%+ margin

---

## Scalability & Performance

### Current Capacity:
- **Concurrent users**: 100-500 (Lambda auto-scales)
- **API requests/sec**: 10-50 (throttled via API Gateway)
- **Database**: Auto-scales with demand
- **AI agents**: Rate limited per user to control costs

### Scale to 10K users:
- **No architecture changes needed**
- **Cost increases linearly** (serverless advantage)
- **Potential optimizations**:
  - Cache frequent AI responses
  - Batch AI operations
  - Use cheaper models for simple tasks (Nova Lite vs Sonnet)

### Performance Targets:
- **Page load**: < 3 seconds
- **API response**: < 500ms (non-AI)
- **AI agent response**: 3-8 seconds (acceptable for value)
- **Uptime**: 99.9% (AWS SLA)

---

## Security & Compliance

### Security Measures:
- **HTTPS only** (CloudFront + API Gateway)
- **API rate limiting** (prevent abuse)
- **Input validation** (prevent injection attacks)
- **CORS policies** (restrict origins)
- **Secrets management** (AWS Secrets Manager)
- **IAM least privilege** (minimal permissions)

### Compliance Considerations:
- **HIPAA**: Not compliant yet (would require BAA with AWS)
- **GDPR**: Ready (user data deletion, export capabilities)
- **Disclaimers**: Medical advice disclaimers required
- **Data retention**: Configurable per user preference

### Privacy:
- **Data encryption**: At rest (DynamoDB) and in transit (TLS)
- **User consent**: Required for data processing
- **Data ownership**: Users own their data
- **Export capability**: Users can download all data

---

## Deployment Environments

### Development (`dev`)
- **Terraform workspace**: dev
- **Purpose**: Active development and testing
- **Data**: Test data only
- **Cost controls**: Strict billing alerts

### Production (`prod`)
- **Terraform workspace**: prod
- **Purpose**: Live user traffic
- **Data**: Real user data
- **Monitoring**: 24/7 alerting
- **Backups**: Automated daily snapshots
- **Custom domain**: health-coach.app (example)

---

## Future Enhancements

### Phase 2 (Post-presentation):
- Mobile apps (React Native)
- Wearable integrations (Fitbit, Apple Watch)
- Social features (friend connections, challenges)
- Payment processing (Stripe)
- Advanced analytics (predictive modeling)

### Phase 3 (Scale):
- White-label for gyms/trainers
- API for third-party integrations
- Machine learning models (custom trained)
- Multi-language support
- Regional compliance (HIPAA, etc.)

---

This architecture is:
- ✅ **Serverless**: Auto-scales, pay-per-use
- ✅ **Cost-effective**: <$100/month during development
- ✅ **Production-ready**: Can handle 1000s of users
- ✅ **Modern**: AI-first, cloud-native
- ✅ **Maintainable**: Infrastructure as Code (Terraform)
- ✅ **Impressive**: Shows technical sophistication for presentations
