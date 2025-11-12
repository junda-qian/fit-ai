# Fitness AI Agent Architecture
## Multi-Agent System with Tools

Inspired by ALEX Financial Planner's multi-agent architecture, adapted for fitness coaching.

---

## Executive Summary

This document outlines a multi-agent AI fitness coaching system that:
- **Proactively monitors** user progress with weekly automated analysis
- Uses **specialized agents** for nutrition and training optimization
- **Automatically adjusts** meal and training plans based on detected trends
- Integrates **function tools** for calculations and data access
- Follows **OpenAI Agents SDK patterns** from the ALEX project
- Deploys as **AWS Lambda functions** with EventBridge scheduling
- Provides **intelligent coordination** between potentially conflicting advice
- Uses **14-day trend analysis** to filter out daily noise (water retention, sleep variance)

### Key Paradigm Shift: Proactive vs Reactive

**Traditional AI Coach (Reactive):**
- User notices plateau → asks "what should I do?"
- Requires user to diagnose their own problems
- Reactive intervention only

**This AI Coach (Proactive):**
- AI monitors progress automatically every week
- AI detects plateaus, anomalies, overtraining signals
- AI adjusts plans automatically with transparent reasoning
- User just logs data and follows updated plan
- Like having a real coach checking in weekly

**User Experience:**
1. User logs workouts, nutrition, weight, and body composition consistently
2. Every Monday: AI analyzes last 14 days of data (weight, body fat %, workouts, nutrition)
3. AI detects issues (plateau, body recomposition, too fast/slow progress, overtraining)
4. AI updates meal/training plan if needed using personalized deficit/surplus calculations
5. User views analysis in dashboard with changes + reasoning (e.g., "Body fat decreased despite weight plateau - keep current calories!")
6. User follows updated plan (no diagnosis required)

---

## Key Learnings from ALEX Backend

### 1. Orchestrator Pattern
- **Planner agent** coordinates specialist agents via function tools
- Each specialist has a single responsibility
- Orchestrator decides which agents to invoke based on context

### 2. Structured Output with Pydantic
- Use `output_type` parameter for validated responses
- Pydantic models ensure data quality
- Field validators enforce business rules (e.g., macros sum to 100%)

### 3. Pre-processing Before AI
- Handle deterministic logic outside agents (e.g., `handle_missing_instruments`)
- Only use AI for decisions requiring reasoning
- Reduces costs and improves reliability

### 4. Context Wrapper Pattern
- `RunContextWrapper[ContextClass]` provides clean context access to tools
- Tools are stateless, context provides state
- Easy to test and reason about

### 5. Lambda as Microservices
- Each agent = separate Lambda function
- Function tools invoke other Lambdas
- Enables independent scaling and deployment

---

## Coaching Model: Proactive vs Reactive

### Primary Mode: Proactive Weekly Analysis

The AI coach operates like a real coach - monitoring your progress automatically and adjusting your plan as needed.

**How it works:**
1. **Every Monday at 6 AM**: EventBridge triggers weekly analysis for all active users
2. **14-day trend analysis**: Pulls last 2 weeks of data (weight, workouts, sleep, nutrition)
3. **Issue detection**: Identifies plateaus, anomalies, overtraining signals
4. **Automatic adjustments**: Updates meal/training plans if needed
5. **Store results**: User can view analysis and changes in dashboard

**Why 14 days?**
- Daily weight fluctuates due to water retention, sodium intake, hormones
- Workout performance varies with sleep, stress, recovery
- 7-14 days is minimum timeframe to detect true trends
- Matches real-world coaching check-in frequency

**User experience:**
- User's job: Log data consistently
- Agent's job: Monitor trends, detect issues, adjust plans
- User just follows the updated plan without diagnosis/thinking

### Secondary Mode: On-Demand Chat

Users can still ask questions anytime for:
- Exercise form tips
- Meal substitutions
- Motivation and encouragement
- Understanding why changes were made
- Specific scenarios (e.g., "I have a wedding next month")

But NOT needed for routine plan adjustments - those happen automatically.

---

## Proposed Architecture

### Agent Structure

```
┌──────────────────────────────────────────────────────────────────┐
│                TWO INDEPENDENT AGENT FLOWS                       │
└──────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════
 FLOW 1: Weekly Nutrition Analysis (Scheduled - EventBridge)
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────┐
│     EventBridge Scheduler (Every Monday 6 AM)        │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         Nutrition Specialist Agent                   │
│  (Deterministic - Pure Python, No AI)               │
│  FOR EACH ACTIVE USER:                              │
│  1. Pull last 14 days of data                       │
│      - Weight logs                                  │
│      - Body composition logs (skinfolds/waist/BF%)  │
│      - Nutrition logs                               │
│      - Workout logs (for bulk assessment)           │
│  2. Calculate trends (deterministic)                │
│      - Weight trend (weekly rate %)                 │
│      - Body composition trend                       │
│      - Average calorie intake                       │
│  3. Apply nutrition algorithm (pure Python)         │
│      - Estimate maintenance calories                │
│      - Calculate optimal deficit/surplus            │
│      - Detect body recomposition                    │
│      - Make calorie/macro recommendations           │
│  4. Store weekly analysis                           │
│  5. Update nutrition plan (if needed)               │
│  6. Flag for communication                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │ weekly_analyses │
              │ active_plans    │
              │   (nutrition)   │
              │communication_pending: true│
              └────────┬────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────┐
│     EventBridge Scheduler (Monday 6:05 AM)          │
│     Triggers after Nutrition/Training complete      │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         Communication Specialist Agent               │
│  (AI-Powered - Uses Bedrock Claude)                 │
│  FOR EACH USER WITH PENDING COMMUNICATION:          │
│  1. Read nutrition recommendation                   │
│  2. Read training summary                           │
│  3. Gather user history (streak, achievements)      │
│  4. Generate personalized message (AI)              │
│      - Acknowledge progress                         │
│      - Explain nutrition changes                    │
│      - Review training performance                  │
│      - Motivate for upcoming week                   │
│  5. Store communication                             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌─────────────────────┐
              │weekly_communications │
              └─────────────────────┘


═══════════════════════════════════════════════════════════════════
 FLOW 2: Session-to-Session Training (Event-Driven - Post Workout)
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────┐
│   User logs workout via /api/workouts/log           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│   Backend saves workout + invokes Training Agent    │
│   (async Lambda invocation - don't block user)     │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│       Training Specialist Agent                      │
│  FOR EACH EXERCISE in workout:                      │
│  1. Get exercise config (progression model, etc)    │
│  2. Analyze first set vs rep target                 │
│  3. Apply Linear/Rep Range progression rules        │
│  4. Prescribe next session (weight, reps, action)   │
│  5. Detect plateaus/regressions                     │
│  6. Update user_exercises table                     │
│  7. Store training recommendation                   │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌─────────────────────┐
              │   user_exercises     │
              │ (next_session update)│
              │                      │
              │training_recommendations│
              └─────────────────────┘


═══════════════════════════════════════════════════════════════════
 Function Tools Layer (Shared)
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────┐
│  Nutrition Tools:                                   │
│  - calculate_tdee()                                 │
│  - calculate_macros()                               │
│  - analyze_weight_trend(days=14)                    │
│  - analyze_body_composition_trend(days=14)          │
│  - estimate_maintenance_calories()                  │
│  - calculate_optimal_deficit()                      │
│  - calculate_optimal_surplus()                      │
│                                                     │
│  Training Tools:                                    │
│  - apply_linear_progressive_rules()                 │
│  - apply_rep_range_rules()                          │
│  - detect_plateau()                                 │
│  - detect_regression()                              │
│  - calculate_plateau_breaker_weight()               │
│  - suggest_progression_model_switch()               │
│  - calculate_1rm()                                  │
└─────────────────────────────────────────────────────┘
```

---

## Agent Coordination and Conflict Resolution

When both nutrition and training agents recommend changes, the system uses these principles:

### Conflict Scenarios

**Scenario 1: Competing Energy Demands**
- **Nutrition Agent**: "Reduce calories by 300 (plateau detected)"
- **Training Agent**: "Add training volume (ready for progression)"
- **Resolution**: Prioritize based on user's primary goal
  - If goal is "lose_weight": Apply nutrition recommendation, defer training increase
  - If goal is "build_muscle": Apply training recommendation, use smaller deficit

**Scenario 2: Recovery vs Performance**
- **Nutrition Agent**: "Increase calories (losing too fast, risk muscle loss)"
- **Training Agent**: "Reduce volume (overtraining detected)"
- **Resolution**: Apply both - prioritize recovery
  - Increase calories AND reduce volume
  - User in negative adaptation spiral, needs both interventions

**Scenario 3: No Conflict**
- **Nutrition Agent**: "Maintain current calories (body recomp happening)"
- **Training Agent**: "Progress squat weight (hit targets consistently)"
- **Resolution**: Apply both changes independently

### Coordination Principles

1. **User's Primary Goal** - Stored in `user_profiles.goal` ("lose_weight", "build_muscle", "maintain")
2. **Severity Ranking** - Some issues take priority (overtraining > plateau)
3. **Conservative Approach** - When in doubt, make one change at a time
4. **Track Adjustment History** - Prevent over-correction by checking recent changes

---

## Integration with Existing Fitness App

### Current Architecture
Your app currently has:
- **Frontend**: Next.js with React
- **Backend**: FastAPI Lambda (`/backend`)
- **Database**: DynamoDB tables (user_profiles, nutrition_logs, workout_logs, body_logs, etc.)
- **API**: REST endpoints for CRUD operations

### Integration Points

For detailed schema and API specifications, see:
- [Nutrition Agent Spec](./agents/NUTRITION_AGENT_SPEC.md) - Weekly analysis, deterministic algorithm, DynamoDB schema
- [Training Agent Spec](./agents/TRAINING_AGENT_SPEC.md) - Session-to-session progression, exercise configuration
- [Communication Agent Spec](./agents/COMMUNICATION_AGENT_SPEC.md) - AI-powered weekly summaries, personalized messaging

#### EventBridge Scheduled Rule
```python
# terraform/eventbridge.tf

resource "aws_cloudwatch_event_rule" "weekly_analysis" {
  name                = "fitness-weekly-analysis"
  description         = "Trigger weekly progress analysis for all active users"
  schedule_expression = "cron(0 6 ? * MON *)"  # Every Monday at 6 AM UTC
}

resource "aws_cloudwatch_event_target" "weekly_analysis" {
  rule      = aws_cloudwatch_event_rule.weekly_analysis.name
  target_id = "WeeklyAnalysisLambda"
  arn       = aws_lambda_function.weekly_analyzer.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weekly_analyzer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly_analysis.arn
}
```

#### Lambda Deployment Structure

```
terraform/
  lambda_ai_agents.tf  # New file for AI agent Lambdas
  eventbridge.tf       # EventBridge cron rules

ai_agents/  # Renamed from alex_backend
  nutrition_specialist/  # Weekly (deterministic - pure Python)
    lambda_handler.py
    algorithm.py        # Pure Python implementation of Tables 1-3
    tools.py
  training_specialist/   # Event-driven (deterministic - pure Python)
    lambda_handler.py
    algorithm.py
    tools.py
  communication_specialist/  # Weekly (AI-powered - Bedrock)
    lambda_handler.py
    agent.py           # AI agent for message generation
    prompts.py
  orchestrator/          # On-demand chat (AI-powered - future)
    lambda_handler.py
    agent.py
    prompts.py
  shared/
    context.py
    models.py          # Pydantic models for structured outputs
    db_client.py
    trend_analysis.py  # Shared trend calculation functions (deterministic)
```

---

## Development & Testing Strategy

### Key Principle: Build for Manual Triggering First

The agents are designed to work independently of how they're triggered. This allows you to:
- **Develop and test anytime** (not just Monday 6 AM or post-workout)
- **No code changes** needed to switch from manual to scheduled
- **Keep manual triggers available** in production for debugging

### Development Phase: Manual Triggering

#### Option 1: AWS CLI (Recommended)

```bash
# Test with specific user
aws lambda invoke \
  --function-name fitness-nutrition-specialist \
  --payload '{"user_ids": ["user_123"]}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# Test with all users (production simulation)
aws lambda invoke \
  --function-name fitness-nutrition-specialist \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  response.json

# View results
cat response.json | jq '.'
```

### Production Phase: Add Scheduling

When ready for production, add EventBridge - **no Lambda code changes needed**. Use a feature flag to enable/disable scheduling:

```hcl
# terraform/variables.tf
variable "enable_weekly_schedule" {
  description = "Enable EventBridge schedule for weekly analysis"
  type        = bool
  default     = false  # Start disabled
}
```

---

## Deployment Considerations

### Cost Estimates

**Weekly Nutrition Analysis (Primary Cost):**
- Lambda invocations: 1 per user per week
- Bedrock Claude costs: ~$0.03-0.05 per user per week
- **Monthly cost for 1000 users: ~$165/month**

**Training Analysis (Event-Driven):**
- Lambda invocations: ~3-4 per user per week (post-workout)
- Smaller token usage (simpler algorithm)
- **Monthly cost for 1000 users: ~$40/month**

**Total: ~$205/month for 1000 users**
- Much more cost-effective than human coaches ($100+ per client/month)
- Cost scales linearly with users
- Pay only for actual AI usage, not idle time

### Observability
- CloudWatch logs for each Lambda invocation
- Store weekly analysis results in DynamoDB for audit trail
- Track plan change history
- Monitor EventBridge execution metrics
- Set up CloudWatch alarms for Lambda failures

### Scalability
- Lambda auto-scales, no infrastructure management
- EventBridge handles scheduling for all users
- Parallel processing possible for large user bases
- DynamoDB handles high read/write throughput

---

## Key Advantages of This Architecture

### 1. Proactive Coaching (Not Reactive)
- User doesn't need to diagnose problems themselves
- Agent automatically detects plateaus and anomalies
- Weekly rhythm matches real coaching cadence
- Reduces cognitive load for users

### 2. Data-Driven with Noise Filtering
- 14-day trend analysis filters out daily fluctuations
- Avoids over-reacting to water retention, poor sleep, etc.
- Statistical approach to plateau detection
- Minimum data requirements prevent premature adjustments

### 3. Transparent Plan Adjustments
- Users see exactly what changed and why
- Reasoning is stored and displayed
- Plan version history for accountability
- Builds trust through transparency

### 4. Separation of Concerns
- Each agent has one job, easier to test and improve
- Nutrition and training agents operate independently
- Specialists focus on domain-specific recommendations

### 5. Scalability
- Lambda auto-scales, no infrastructure management
- EventBridge handles scheduling for all users
- Parallel processing possible for large user bases

### 6. Cost Efficiency
- ~$0.04 per user per week for AI coaching
- Pay only for actual AI usage, not idle time
- 100x cheaper than human coaches

### 7. Intelligent Conflict Resolution
- Detects when recommendations conflict (e.g., cut calories vs add volume)
- Makes trade-offs based on user's primary goal
- Coordinates multi-domain adjustments

### 8. Extensibility
- Easy to add new specialists (e.g., injury prevention, supplement timing)
- New specialist agents can be added independently
- Clear interfaces between agents

### 9. Type Safety & Reliability
- Pydantic models ensure structured, validated outputs
- Specialist algorithms are independently testable with fixed inputs
- Clear contracts between orchestrator and specialists

### 10. Observability
- Each agent is independently traceable
- Weekly analysis results stored for audit
- Plan change history preserved

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Set up `ai_agents/` directory structure
- [ ] Create shared models and context wrappers
- [ ] Add DynamoDB tables: `weekly_analyses`, `active_plans`, `weekly_communications`, `user_exercises`, `training_recommendations`
- [ ] Update `body_logs` table schema to support skinfolds, circumferences, and body fat tracking

### Phase 2: Nutrition Specialist Agent (Week 2-3)
See [Nutrition Agent Spec](./agents/NUTRITION_AGENT_SPEC.md) for complete implementation details
- [ ] Implement Nutrition Specialist Lambda (deterministic - pure Python)
- [ ] Create nutrition function tools (trend analysis, calculations)
- [ ] Implement evidence-based nutrition algorithm (Tables 1-3)
- [ ] Add EventBridge cron rule for Monday 6:00 AM
- [ ] Test with sample users (unit tests for deterministic logic)

### Phase 3: Training Specialist (Event-Driven) (Week 4)
See [Training Agent Spec](./agents/TRAINING_AGENT_SPEC.md) for complete implementation details
- [ ] Create exercise configuration UI
- [ ] Implement Training Specialist agent (event-driven, post-workout)
- [ ] Create training function tools
- [ ] Update `/api/workouts/log` endpoint to invoke Training Agent asynchronously
- [ ] Test session-to-session progression rules

### Phase 4: Communication Specialist Agent (Week 5)
See [Communication Agent Spec](./agents/COMMUNICATION_AGENT_SPEC.md) for complete implementation details
- [ ] Implement Communication Specialist Lambda (AI-powered)
- [ ] Create AI prompt for personalized weekly summaries
- [ ] Implement user history analysis (streaks, achievements)
- [ ] Add EventBridge cron rule for Monday 6:05 AM
- [ ] Test message generation quality

### Phase 5: Frontend Integration (Week 6)
- [ ] Build Weekly Analysis Dashboard (displays communication messages)
- [ ] Create API endpoints for viewing weekly communications
- [ ] Add body composition logging UI (skinfolds, waist, photos)
- [ ] Add training prescription UI (display next session recommendation)
- [ ] Show user metrics (streak, achievements, progress)

### Phase 6: On-Demand Chat (Week 7) (Secondary)
- [ ] Implement Coach Orchestrator agent for Q&A
- [ ] Add `coach_jobs` DynamoDB table
- [ ] Create `/api/coach/ask` endpoint
- [ ] Build chat UI component

### Phase 7: Polish & Demo Prep (Week 8)
- [ ] Add observability (CloudWatch logs, metrics)
- [ ] Performance optimization
- [ ] Create demo scenarios with realistic sample data
- [ ] Prepare presentation materials

---

## Comparison: ALEX Financial Planner vs Fitness Coach

| Aspect | ALEX (Financial) | Fitness Coach |
|--------|------------------|---------------|
| **Orchestrator** | Planner | Coach Orchestrator (optional) |
| **Specialists** | Tagger, Reporter, Charter, Retirement, Researcher | Nutrition, Training |
| **Tools** | Market insights, price updates | TDEE calc, 1RM calc, trend analysis |
| **Data Source** | Aurora PostgreSQL | DynamoDB |
| **Conflict Type** | Data validation | Competing recommendations |
| **Output** | Portfolio report + charts | Coaching advice + action plan |
| **Trigger** | User request | Weekly scheduled + post-workout events |

---

## Next Steps

1. **Review Agent Specifications**: Read detailed specs for each agent:
   - [Nutrition Agent Spec](./agents/NUTRITION_AGENT_SPEC.md) - Complete algorithm, tools, and schema
   - [Training Agent Spec](./agents/TRAINING_AGENT_SPEC.md) - Progression models, rules, and API integration

2. **Set up project structure** - Create `ai_agents/` directory

3. **Choose MVP scope** - Weekly analysis + Nutrition + Training specialists

4. **Begin implementation** - Start with nutrition agent or training agent based on priority
