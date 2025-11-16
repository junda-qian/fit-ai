# Fitness AI Agent Architecture
## Multi-Agent System with Tools

Inspired by ALEX Financial Planner's multi-agent architecture, adapted for fitness coaching.

---

## Executive Summary

This document outlines a **hybrid multi-agent AI fitness coaching system** that combines deterministic algorithms with AI-powered communication:

**Core Architecture:**
- **Deterministic Decision-Making**: Nutrition and Training agents use pure Python algorithms (fast, reliable, testable)
- **AI-Powered Communication**: Communication and Coach agents use AI for natural language (flexible, engaging)
- **Proactive Monitoring**: Weekly automated analysis of user progress
- **Event-Driven Training**: Session-to-session progression after each workout
- **AWS Lambda Deployment**: Serverless, auto-scaling microservices
- **14-Day Trend Analysis**: Filters out daily noise (water retention, sleep variance)

**Four Specialized Agents:**
1. **Nutrition Specialist** (Deterministic - Pure Python) - Weekly scheduled
2. **Training Specialist** (Deterministic - Pure Python) - Post-workout event-driven
3. **Communication Specialist** (AI - Bedrock Claude) - Weekly scheduled
4. **Coach Orchestrator** (AI - OpenAI SDK) - On-demand conversational Q&A

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

## Key Design Principles

### 1. Hybrid Architecture: Deterministic Core + AI Communication Layer

**Critical decisions are deterministic:**
- Nutrition adjustments use evidence-based tables (deficit/surplus calculations)
- Training progression follows algorithmic rules (linear/rep range progression)
- Fast execution (<100ms per user), zero cost for decisions
- 100% testable, predictable, and explainable

**User communication is AI-powered:**
- Translates technical recommendations into personalized messages
- Handles natural language Q&A
- Adapts tone and detail level to user preferences
- Cost-effective (~$0.02-0.05 per user per week)

### 2. Structured Output with Pydantic
- Use Pydantic models for validated, structured agent outputs
- Field validators enforce business rules
- Type safety across the entire system

### 3. Independent Agent Deployment
- Each agent = separate AWS Lambda function
- Agents don't depend on each other for execution
- Can be developed, tested, and deployed independently
- Enables independent scaling

### 4. Clear Separation of Concerns
- **Nutrition Specialist**: Makes nutrition decisions
- **Training Specialist**: Makes training decisions
- **Communication Specialist**: Explains decisions to users
- **Coach Orchestrator**: Answers user questions (read-only)

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
│  (Deterministic - Pure Python, NO AI)               │
│  FOR EACH ACTIVE USER:                              │
│  1. Pull last 14 days of data                       │
│      - Weight logs                                  │
│      - Body composition logs (SKINFOLDS preferred)  │
│      - Nutrition logs                               │
│      - Workout logs (for bulk assessment)           │
│  2. Calculate trends (deterministic)                │
│      - Weight trend (weekly rate %)                 │
│      - Body composition trend (skinfold sum)        │
│      - Average calorie intake                       │
│  3. Apply nutrition algorithm (Tables 1-3)          │
│      - Estimate maintenance calories                │
│      - Calculate optimal deficit/surplus by BF%     │
│      - Detect body recomposition                    │
│      - Make calorie/macro recommendations           │
│  4. Store weekly analysis                           │
│  5. Update nutrition plan (if needed)               │
│  6. Flag for communication (communication_pending)  │
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
│  (Deterministic - Pure Python, NO AI)               │
│  FOR EACH EXERCISE in workout:                      │
│  1. Get exercise config (progression model, etc)    │
│  2. Analyze first set vs rep target                 │
│  3. Apply progression rules (algorithmic):          │
│      - Linear Progressive: Hit reps → add weight    │
│      - Rep Range: Hit reps → add weight, else reps  │
│  4. Prescribe next session (weight, reps, action)   │
│  5. Detect plateaus/regressions                     │
│  6. Implement reactive deloads/plateau breakers     │
│  7. Update user_exercises table                     │
│  8. Store training recommendation                   │
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
 FLOW 3: On-Demand Conversational Coaching (User-Initiated)
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────┐
│   User asks question via /api/coach/ask             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│         Coach Orchestrator Agent                     │
│  (AI-Powered - OpenAI SDK with Function Calling)    │
│  1. Understand user question (natural language)     │
│  2. Dynamically call function tools:                │
│      - get_user_profile()                           │
│      - get_weekly_analysis()                        │
│      - get_nutrition_logs()                         │
│      - get_workout_logs()                           │
│      - get_body_logs()                              │
│      - get_nutrition_recommendation()               │
│      - get_training_status()                        │
│  3. Synthesize information from multiple sources    │
│  4. Generate personalized, educational response     │
│  5. Support multi-turn conversations                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
              ┌─────────────────┐
              │   User receives  │
              │ natural language │
              │    response      │
              └─────────────────┘


═══════════════════════════════════════════════════════════════════
 Function Tools Layer (Shared)
═══════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────┐
│  Nutrition Tools (Deterministic):                   │
│  - calculate_tdee()                                 │
│  - calculate_macros()                               │
│  - analyze_weight_trend(days=14)                    │
│  - analyze_body_composition_trend(days=14)          │
│  - estimate_maintenance_calories()                  │
│  - calculate_optimal_deficit()                      │
│  - calculate_optimal_surplus()                      │
│                                                     │
│  Training Tools (Deterministic):                    │
│  - apply_linear_progressive_rules()                 │
│  - apply_rep_range_rules()                          │
│  - detect_plateau()                                 │
│  - detect_regression()                              │
│  - calculate_plateau_breaker_weight()               │
│  - suggest_progression_model_switch()               │
│  - calculate_1rm()                                  │
│                                                     │
│  Data Retrieval Tools (for Coach Orchestrator):     │
│  - get_user_profile()                               │
│  - get_nutrition_logs(days)                         │
│  - get_workout_logs(days, exercise)                 │
│  - get_body_logs(days)                              │
│  - get_weekly_analysis(week)                        │
│  - get_nutrition_recommendation()                   │
│  - get_training_status(exercise)                    │
│  - analyze_progress(metric, timeframe)              │
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

For detailed implementation specifications, see:
- [Nutrition Agent Spec](./agents/NUTRITION_AGENT_SPEC.md) - Weekly analysis, deterministic algorithm (Tables 1-3), skinfold tracking, DynamoDB schema
- [Training Agent Spec](./agents/TRAINING_AGENT_SPEC.md) - Session-to-session progression, Linear Progressive & Rep Range models, exercise configuration
- [Communication Agent Spec](./agents/COMMUNICATION_AGENT_SPEC.md) - AI-powered weekly summaries with Bedrock Claude, personalized messaging, achievement tracking
- [Coach Orchestrator Spec](./agents/COACH_ORCHESTRATOR_SPEC.md) - Conversational AI with OpenAI SDK, function calling, natural language Q&A

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

ai_agents/
  nutrition_specialist/     # Weekly (deterministic - pure Python)
    lambda_handler.py
    algorithm.py            # Pure Python implementation of Tables 1-3
    tools.py
    test_algorithm.py       # Unit tests for deterministic logic
  training_specialist/      # Event-driven (deterministic - pure Python)
    lambda_handler.py
    algorithm.py            # Linear Progressive & Rep Range algorithms
    tools.py
    test_algorithm.py       # Unit tests for progression rules
  communication_specialist/ # Weekly (AI-powered - Bedrock Claude)
    lambda_handler.py
    agent.py                # Bedrock Claude agent for message generation
    prompts.py              # System prompts for personalized communication
  coach_orchestrator/       # On-demand (AI-powered - OpenAI SDK)
    lambda_handler.py
    agent.py                # OpenAI SDK conversation logic
    tools.py                # Function tool definitions
    prompts.py              # System prompts for coaching
    test_coach.py           # Tests for conversation flow
  shared/
    context.py
    models.py               # Pydantic models for structured outputs
    db_client.py            # Database interface (see DATABASE_CLIENT_INTERFACE.md)
    trend_analysis.py       # Shared trend calculation functions (deterministic)
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

**Weekly Nutrition Analysis:**
- Lambda invocations: 1 per user per week
- **AI Cost: $0** (deterministic - pure Python)
- Lambda compute: ~$0.0001 per user per week
- **Monthly cost for 1000 users: ~$0.40/month**

**Training Analysis (Event-Driven):**
- Lambda invocations: ~3-4 per user per week (post-workout)
- **AI Cost: $0** (deterministic - pure Python)
- Lambda compute: ~$0.0003 per user per week
- **Monthly cost for 1000 users: ~$1.20/month**

**Communication Specialist (AI-Powered):**
- Lambda invocations: 1 per user per week
- Bedrock Claude costs: ~$0.02 per user per week
- **Monthly cost for 1000 users: ~$80/month**

**Coach Orchestrator (AI-Powered, On-Demand):**
- Usage: ~4 conversations per user per month
- OpenAI GPT-4 Turbo: ~$0.048 per conversation
- **Monthly cost for 1000 users: ~$192/month**

**Total: ~$273/month for 1000 active users**
- Critical decisions are FREE (deterministic)
- AI cost only for user communication and Q&A
- Much cheaper than human coaches ($100+ per client/month)
- Cost scales linearly with users

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

### 1. Hybrid Architecture: Best of Both Worlds
- **Deterministic core** for critical decisions (nutrition, training) = Fast, reliable, testable, FREE
- **AI communication layer** for user experience = Personalized, engaging, motivating
- Clear separation prevents AI hallucinations from affecting plan adjustments

### 2. Proactive Coaching (Not Reactive)
- User doesn't need to diagnose problems themselves
- Agents automatically detect plateaus and anomalies
- Weekly rhythm matches real coaching cadence
- Reduces cognitive load for users

### 3. Evidence-Based & Deterministic
- Nutrition algorithm implements peer-reviewed tables (optimal deficit by body fat %)
- Training progression follows proven programming principles
- 100% testable, reproducible, and explainable
- No AI "black box" for critical decisions

### 4. Data-Driven with Noise Filtering
- 14-day trend analysis filters out daily fluctuations
- Skinfold measurements provide reliable fat loss tracking (preferred over body fat % alone)
- Avoids over-reacting to water retention, poor sleep, etc.
- Minimum data requirements prevent premature adjustments

### 5. Transparent Plan Adjustments
- Users see exactly what changed and why
- Reasoning is stored and displayed
- Plan version history for accountability
- Builds trust through transparency

### 6. Separation of Concerns
- **Nutrition Specialist**: Makes nutrition decisions
- **Training Specialist**: Makes training decisions
- **Communication Specialist**: Explains decisions to users
- **Coach Orchestrator**: Answers questions (read-only)
- Each agent has one job, easier to test and improve

### 7. Scalability
- Lambda auto-scales, no infrastructure management
- EventBridge handles scheduling for all users
- Parallel processing possible for large user bases
- DynamoDB handles high throughput

### 8. Cost Efficiency
- Critical decisions are FREE (deterministic algorithms)
- AI cost only for user communication (~$0.27 per user per month)
- Pay only for actual AI usage, not idle time
- 100x cheaper than human coaches

### 9. Natural Language Interface
- Coach Orchestrator provides conversational Q&A
- Users ask questions in plain English
- AI dynamically calls specialist functions
- Educational explanations build user knowledge

### 10. Extensibility
- Easy to add new specialists (e.g., injury prevention, sleep optimization)
- New specialist agents can be added independently
- Clear function tool interfaces
- Coach Orchestrator automatically gains access to new capabilities

### 11. Type Safety & Reliability
- Pydantic models ensure structured, validated outputs
- Deterministic algorithms are unit-testable with fixed inputs
- Clear contracts between agents
- No runtime surprises

### 12. Observability
- Each agent is independently traceable
- Weekly analysis results stored for audit
- Plan change history preserved
- CloudWatch logs for all Lambda invocations

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

### Phase 6: Coach Orchestrator (Week 7)
See [Coach Orchestrator Spec](./agents/COACH_ORCHESTRATOR_SPEC.md) for complete implementation details
- [ ] Implement Coach Orchestrator agent with OpenAI SDK
- [ ] Create function tools for data retrieval and specialist calls
- [ ] Set up conversation state management
- [ ] Create `/api/coach/ask` endpoint
- [ ] Build chat UI component
- [ ] Test multi-turn conversations

### Phase 7: Polish & Demo Prep (Week 8)
- [ ] Add observability (CloudWatch logs, metrics)
- [ ] Performance optimization
- [ ] Create demo scenarios with realistic sample data
- [ ] Prepare presentation materials

---

## Comparison: ALEX Financial Planner vs Fitness Coach

| Aspect | ALEX (Financial) | Fitness Coach |
|--------|------------------|---------------|
| **Orchestrator** | Planner (AI-powered) | Coach Orchestrator (AI-powered with OpenAI SDK) |
| **Specialists** | Tagger, Reporter, Charter, Retirement, Researcher (AI) | Nutrition (Deterministic), Training (Deterministic), Communication (AI) |
| **Decision Making** | AI reasoning for all decisions | Hybrid: Deterministic for critical decisions, AI for communication |
| **Tools** | Market insights, price updates | TDEE calc, 1RM calc, trend analysis, body composition tracking |
| **Data Source** | Aurora PostgreSQL | DynamoDB |
| **Conflict Type** | Data validation | Competing recommendations (calorie vs volume adjustments) |
| **Output** | Portfolio report + charts | Weekly analysis + personalized coaching messages + next session prescriptions |
| **Trigger** | User request | Weekly scheduled + post-workout events + on-demand chat |
| **Cost per User** | Higher (all AI) | Lower (deterministic core, AI only for UX) |

---

## Agent Specifications

For complete implementation details, see:

1. **[Nutrition Specialist Agent](./agents/NUTRITION_AGENT_SPEC.md)**
   - Weekly scheduled (EventBridge - Mondays 6:00 AM)
   - Deterministic algorithm (Pure Python - NO AI)
   - Evidence-based Tables 1-3 for deficit/surplus calculation
   - Skinfold-based body composition tracking
   - Body recomposition detection

2. **[Training Specialist Agent](./agents/TRAINING_AGENT_SPEC.md)**
   - Event-driven (post-workout)
   - Deterministic progression models (Pure Python - NO AI)
   - Linear Progressive and Rep Range progression
   - Plateau/regression detection
   - Reactive deloads and plateau breakers

3. **[Communication Specialist Agent](./agents/COMMUNICATION_AGENT_SPEC.md)**
   - Weekly scheduled (EventBridge - Mondays 6:05 AM)
   - AI-powered (Bedrock Claude)
   - Translates technical recommendations into personalized messages
   - Achievement tracking and motivation
   - Multi-language ready

4. **[Coach Orchestrator Agent](./agents/COACH_ORCHESTRATOR_SPEC.md)**
   - On-demand conversational Q&A
   - AI-powered (OpenAI SDK with function calling)
   - Natural language interface to fitness system
   - Multi-turn conversations
   - Educational explanations

---

## Next Steps

1. **Review detailed agent specifications** (linked above)
2. **Set up project structure** - Create `ai_agents/` directory
3. **Choose MVP scope** - Recommend starting with Nutrition + Training specialists (deterministic, cost-free)
4. **Begin implementation** - Follow the implementation roadmap (Phase 1-7)
