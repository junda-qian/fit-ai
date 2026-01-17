# DynamoDB Explained - For Beginners

## What is DynamoDB?

Imagine a massive, infinitely expandable filing cabinet that:
- **Never runs out of space** - automatically grows as you add more files
- **Never slows down** - retrieves files in milliseconds even with billions of documents
- **Never crashes** - AWS maintains and backs it up automatically
- **Charges you only when you use it** - no monthly fees when idle

**DynamoDB** is Amazon's fully managed NoSQL database service. It's like a super-powered spreadsheet in the cloud that can handle massive amounts of data without you ever worrying about servers, backups, or scaling.

## Traditional Database vs DynamoDB

### Traditional SQL Database (PostgreSQL, MySQL):
```
Think of a traditional database like a library:
- Fixed tables with rigid columns (like library catalog cards)
- Everything has a strict structure
- Requires a database server (you manage it)
- Slows down as data grows (need to upgrade hardware)
- Complex queries with JOINs across tables
```

### DynamoDB (NoSQL):
```
Think of DynamoDB like Google Drive with folders:
- Flexible data structure (JSON documents)
- Each item can have different fields
- No servers to manage (AWS handles everything)
- Stays fast no matter how much data you have
- Simple queries by key (super fast lookups)
```

## Real-World Analogy

**Traditional SQL Database:**
You own a filing cabinet. When it fills up, you buy a bigger cabinet. You organize everything yourself. If the cabinet breaks, you lose data unless you manually backed it up.

**DynamoDB:**
You rent space in a magical, self-expanding filing cabinet. AWS automatically:
- Adds more drawers when you need them
- Backs up everything
- Retrieves files in milliseconds
- Charges you only for files stored and retrieved

## Why Use DynamoDB?

### 1. Zero Server Management
- No installation, no configuration, no updates
- AWS handles everything behind the scenes
- You just store and retrieve data

### 2. Automatic Scaling
- Handles 10 requests/second or 10 million requests/second
- No performance degradation as data grows
- No capacity planning needed

### 3. Pay-Per-Use Pricing
- **Pay-per-request** model (no idle costs)
- Only pay when you read/write data
- Perfect for side projects and startups

### 4. Blazing Fast Performance
- Single-digit millisecond response times
- Consistent performance at any scale
- Optimized for key-value lookups

### 5. Built-in Features
- Automatic backups (point-in-time recovery)
- Encryption at rest
- Global replication (optional)
- Streams for real-time processing

### 6. Serverless-Friendly
- Perfect companion for AWS Lambda
- No connection pooling issues
- Works seamlessly in serverless architectures

## How FitTracker AI Uses DynamoDB

The fitness app stores **all user data** in DynamoDB across **9 tables**:

### The 9 Tables:

```
1. user_profiles          ─┐
2. workout_plans          ─┤
3. nutrition_logs         ─┤
4. workout_logs           ─┼─► All fitness data in DynamoDB
5. body_logs              ─┤
6. daily_summaries        ─┤
7. user_exercises         ─┤
8. training_recommendations ┤
9. training_progress_summaries ┘
```

### Data Flow Example:

```
User logs breakfast:
    ↓
POST /api/nutrition/logs
    ↓
FastAPI server (Lambda)
    ↓
db.insert("nutrition_logs", {...})
    ↓
DynamoDB Table: health-chatbot-dev-nutrition_logs
    ↓
Data saved instantly ✅
```

---

## The 9 Tables Explained

### 1. **user_profiles** - User Account Information

**What it stores:**
Your personal info, body stats, and daily nutrition targets.

**Example data:**
```json
{
  "user_id": "demo_user_90day",
  "name": "Demo User",
  "age": 30,
  "sex": "male",
  "height_cm": 180,
  "body_weight_kg": 85.0,
  "body_fat_pct": 20.0,
  "goal": "lose_weight",
  "training_status": "intermediate",
  "target_calories": 2200,
  "target_protein": 170.0,
  "target_carbs": 220.0,
  "target_fats": 73.0,
  "bmr": 1850.0,
  "tdee": 2640.0,
  "activity_level": 1.4,
  "created_at": "2024-10-01T00:00:00",
  "updated_at": "2024-12-31T10:30:00"
}
```

**Primary Key:** `user_id`

**Use case:**
- Dashboard displays your daily targets (calories, protein, carbs, fats)
- Energy calculator saves your results here
- One profile per user

**Real-world analogy:** Your membership card at a gym with all your personal info.

---

### 2. **workout_plans** - AI-Generated Workout Programs

**What it stores:**
Your current workout program created by the AI workout planner.

**Example data:**
```json
{
  "id": "uuid-12345",
  "user_id": "demo_user_90day",
  "plan_name": "4-Day Upper/Lower Split",
  "active": true,
  "frequency_per_week": 4,
  "days": [
    {
      "day_name": "Upper Body A",
      "exercises": [
        {
          "name": "Bench Press",
          "sets": 4,
          "reps": 8,
          "rest_seconds": 180,
          "muscle_group": "chest"
        },
        {
          "name": "Bent Over Row",
          "sets": 4,
          "reps": 8,
          "muscle_group": "back"
        }
      ]
    }
  ],
  "created_at": "2024-12-01T09:00:00"
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdIndex` (allows "find all plans for this user")

**Use case:**
- Workout planner saves AI-generated plans
- Workout logging shows exercises from your active plan
- You can only have 1 active plan at a time

**Real-world analogy:** Your personal trainer's written workout program.

---

### 3. **nutrition_logs** - Daily Food Intake

**What it stores:**
Every meal you log (breakfast, lunch, dinner, snacks).

**Example data:**
```json
{
  "id": "uuid-67890",
  "user_id": "demo_user_90day",
  "date": "2024-12-31",
  "meal_type": "breakfast",
  "time": "08:00:00",
  "calories": 450,
  "protein": 30.0,
  "carbs": 45.0,
  "fats": 15.0,
  "food_items": [
    {
      "name": "Oatmeal",
      "amount": "1 cup",
      "calories": 150,
      "protein": 5.0,
      "carbs": 27.0,
      "fats": 3.0
    },
    {
      "name": "Banana",
      "amount": "1 medium",
      "calories": 105,
      "protein": 1.3,
      "carbs": 27.0,
      "fats": 0.4
    },
    {
      "name": "Protein Powder",
      "amount": "1 scoop",
      "calories": 120,
      "protein": 24.0,
      "carbs": 3.0,
      "fats": 1.5
    }
  ],
  "created_at": "2024-12-31T08:15:00"
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdDateIndex` (hash key: `user_id`, range key: `date`)

**Why the index matters:**
Without index: "Search through all nutrition logs in the world to find yours" (slow)
With index: "Get all nutrition logs for user_123 on 2024-12-31" (instant)

**Use case:**
- Nutrition tracking page logs each meal
- Dashboard sums up daily calories/macros
- Nutrition agent analyzes 14 days of eating patterns

**Real-world analogy:** Your food diary or MyFitnessPal log.

---

### 4. **workout_logs** - Completed Training Sessions

**What it stores:**
Every workout you complete with all exercises, sets, reps, and weights.

**Example data:**
```json
{
  "id": "uuid-11111",
  "user_id": "demo_user_90day",
  "date": "2024-12-31",
  "workout_name": "Upper Body A",
  "exercises": [
    {
      "name": "Bench Press",
      "sets": [
        {"reps": 8, "weight": 80.0, "rpe": 7.5},
        {"reps": 8, "weight": 80.0, "rpe": 8.0},
        {"reps": 7, "weight": 80.0, "rpe": 9.0},
        {"reps": 6, "weight": 80.0, "rpe": 9.5}
      ]
    },
    {
      "name": "Bent Over Row",
      "sets": [
        {"reps": 10, "weight": 70.0, "rpe": 7.0},
        {"reps": 10, "weight": 70.0, "rpe": 8.0},
        {"reps": 9, "weight": 70.0, "rpe": 8.5}
      ]
    }
  ],
  "duration_minutes": 65,
  "notes": "Felt strong today, added 2.5kg to bench",
  "completed": true,
  "created_at": "2024-12-31T17:30:00"
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdDateIndex`

**Use case:**
- Workout tracking page logs each session
- Training agent analyzes performance to recommend weight increases
- Progress charts show strength gains over time

**Real-world analogy:** Your gym logbook with every workout recorded.

---

### 5. **body_logs** - Body Weight & Measurements

**What it stores:**
Daily weigh-ins and weekly body composition measurements.

**Example data:**
```json
{
  "id": "uuid-22222",
  "user_id": "demo_user_90day",
  "date": "2024-12-31",
  "weight": 83.5,
  "skinfolds": {
    "tricep": 9.6,
    "abdomen": 20.0,
    "thigh": 14.4,
    "suprailiac": 16.0,
    "subscapular": 12.0,
    "chest": 6.4,
    "midaxillary": 1.6
  },
  "skinfold_sum": 80.0,
  "created_at": "2024-12-31T07:00:00"
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdDateIndex`

**Use case:**
- Body tracking page logs daily weight
- Weekly skinfold measurements (calipers)
- Nutrition agent uses weight trends to adjust calorie targets

**Real-world analogy:** Your bathroom scale readings written in a notebook.

---

### 6. **daily_summaries** - Aggregated Daily Stats

**What it stores:**
Pre-calculated daily totals for fast dashboard loading.

**Example data:**
```json
{
  "id": "uuid-33333",
  "user_id": "demo_user_90day",
  "date": "2024-12-31",
  "total_calories": 2150,
  "total_protein": 168.5,
  "total_carbs": 215.0,
  "total_fats": 70.0,
  "workouts_completed": 1,
  "weight": 83.5,
  "created_at": "2024-12-31T20:00:00",
  "updated_at": "2024-12-31T20:00:00"
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdDateIndex`

**Why this exists:**
Instead of summing 3 meals every time you load the dashboard:
```
Without daily_summaries:
  1. Query all nutrition_logs for today
  2. Sum calories, protein, carbs, fats (slow)

With daily_summaries:
  1. Query one document (instant)
```

**Use case:**
- Dashboard shows today's totals
- Calendar view shows historical data
- Updated every time you log food or workouts

**Real-world analogy:** Your daily fitness summary in Apple Health or Google Fit.

---

### 7. **user_exercises** - Exercise Configuration & Progression

**What it stores:**
Your personal progression settings for each exercise.

**Example data:**
```json
{
  "id": "uuid-44444",
  "user_id": "demo_user_90day",
  "exercise_name": "Bench Press",
  "progression_model": "linear",
  "rep_target": 8,
  "num_sets": 4,
  "available_increments": [1.25, 2.5, 5.0],
  "selected_increment": 2.5,
  "current_weight": 80.0,
  "last_successful_weight": 77.5,
  "plateau_count": 0,
  "next_session": {
    "weight": 82.5,
    "target_reps": 8,
    "action": "increase",
    "message": "Increase to 82.5kg x 8 reps",
    "reasoning": "Hit 8 reps on all sets last session - time to progress!"
  },
  "exercise_type": "compound",
  "created_at": "2024-10-01T00:00:00",
  "updated_at": "2024-12-31T17:30:00"
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdIndex`

**Progression Models:**
1. **Linear Progressive:** Add weight when you hit reps (e.g., 5x5)
2. **Rep Range:** Progress through rep range (e.g., 3x8-12 before adding weight)

**Use case:**
- Training agent analyzes your workout log
- Compares actual performance vs expected
- Generates next session recommendations (add weight, deload, etc.)

**Real-world analogy:** Your personal training plan with progression rules.

---

### 8. **training_recommendations** - AI Coaching Advice

**What it stores:**
Personalized training recommendations generated by the Training Agent.

**Example data:**
```json
{
  "id": "uuid-55555",
  "user_id": "demo_user_90day",
  "exercise_name": "Bench Press",
  "created_at": "2024-12-31T17:35:00",
  "recommendation_type": "progression",
  "action": "increase_weight",
  "current_weight": 80.0,
  "recommended_weight": 82.5,
  "reasoning": "You hit 8 reps on all 4 sets with RPE 8-9. This indicates you're ready for a 2.5kg increase.",
  "confidence": "high",
  "next_steps": [
    "Warm up thoroughly with 50kg x 10, 65kg x 6",
    "Work sets: 82.5kg x 8 reps x 4 sets",
    "Target RPE: 8-9 (2-3 reps in reserve)",
    "If you can't hit 8 reps, drop back to 80kg"
  ]
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdCreatedAtIndex` (hash key: `user_id`, range key: `created_at`)

**Use case:**
- Generated after every workout log
- Displayed in workout tracking page ("Next Session" section)
- Helps users know exactly what to do next

**Real-world analogy:** Your coach's notes after watching your workout.

---

### 9. **training_progress_summaries** - Weekly Progress Reports

**What it stores:**
Weekly training analysis generated by the Training Specialist Agent.

**Example data:**
```json
{
  "id": "uuid-66666",
  "user_id": "demo_user_90day",
  "week": "2024-W52",
  "week_start_date": "2024-12-25",
  "week_end_date": "2024-12-31",
  "sessions_completed": 4,
  "sessions_planned": 4,
  "compliance_rate": 100.0,
  "total_volume": 32500.0,
  "exercises_progressed": [
    {
      "exercise": "Bench Press",
      "old_weight": 77.5,
      "new_weight": 80.0,
      "change_pct": 3.2
    }
  ],
  "exercises_plateaued": [],
  "exercises_deloaded": [],
  "overall_assessment": "Excellent week! All sessions completed with good progression on upper body.",
  "recommendations": [
    "Continue current progression on all exercises",
    "Focus on recovery - sleep 8+ hours",
    "Maintain protein intake at 170g/day"
  ],
  "created_at": "2024-12-31T06:00:00"
}
```

**Primary Key:** `id`
**Global Secondary Index:** `UserIdWeekIndex` (hash key: `user_id`, range key: `week`)

**Use case:**
- Generated every Monday by scheduled Training Agent
- Shows weekly training trends
- Identifies plateaus and suggests deloads

**Real-world analogy:** Your coach's weekly performance review.

---

## How DynamoDB Queries Work

### Primary Keys (Lightning-Fast Lookups)

Every table has a **primary key** that uniquely identifies each item.

**Two types:**

1. **Simple Primary Key (Partition Key only)**
   - Example: `user_profiles` uses `user_id`
   - Query: "Get profile for user_123" → instant lookup

2. **Composite Primary Key (Partition Key + Sort Key)**
   - Example: `nutrition_logs` uses `id` (partition) + `date` (sort)
   - Query: "Get all nutrition logs for user_123 sorted by date"

### Global Secondary Indexes (GSI) - Fast Searches

**Problem:** DynamoDB is ONLY fast when querying by primary key.

**Example problem:**
```
Table: nutrition_logs
Primary Key: id (random UUID)

Query: "Get all nutrition logs for user_123"
❌ Without index: Must SCAN entire table (slow, expensive)
✅ With index: Instant lookup using UserIdDateIndex
```

**How indexes work:**

```
Original Table (nutrition_logs):
id (primary key)       user_id      date         calories
-------------------------------------------------------------
uuid-111               user_123     2024-12-31   2150
uuid-222               user_456     2024-12-31   1800
uuid-333               user_123     2024-12-30   2200

Global Secondary Index (UserIdDateIndex):
user_id (hash key)     date (sort key)      id
-------------------------------------------------------------
user_123               2024-12-30           uuid-333
user_123               2024-12-31           uuid-111
user_456               2024-12-31           uuid-222
```

Now you can query: "Get all logs for user_123 between 2024-12-01 and 2024-12-31" → instant!

### Index Summary for Each Table:

| Table | Primary Key | Global Secondary Index |
|-------|-------------|------------------------|
| user_profiles | `user_id` | None (no queries needed) |
| workout_plans | `id` | `UserIdIndex` (hash: `user_id`) |
| nutrition_logs | `id` | `UserIdDateIndex` (hash: `user_id`, range: `date`) |
| workout_logs | `id` | `UserIdDateIndex` (hash: `user_id`, range: `date`) |
| body_logs | `id` | `UserIdDateIndex` (hash: `user_id`, range: `date`) |
| daily_summaries | `id` | `UserIdDateIndex` (hash: `user_id`, range: `date`) |
| user_exercises | `id` | `UserIdIndex` (hash: `user_id`) |
| training_recommendations | `id` | `UserIdCreatedAtIndex` (hash: `user_id`, range: `created_at`) |
| training_progress_summaries | `id` | `UserIdWeekIndex` (hash: `user_id`, range: `week`) |

---

## The Database Adapter Pattern

The app uses an **adapter pattern** to support both JSON files (local dev) and DynamoDB (production).

### The Interface (Common Methods)

Both `JSONDatabase` and `DynamoDBAdapter` provide the same 5 methods:

```python
db.insert(collection, document)     # Add new item
db.find_one(collection, query)      # Get single item
db.find(collection, query)          # Get multiple items
db.update(collection, query, data)  # Update items
db.delete(collection, query)        # Remove items
```

### Local Development (JSON Files)

```python
# database.py decides which to use
USE_DYNAMODB = os.getenv('USE_DYNAMODB', 'false').lower() == 'true'

if USE_DYNAMODB:
    db = DynamoDBAdapter()
else:
    db = JSONDatabase(data_dir="data/tracking")
```

**JSON files on your computer:**
```
data/tracking/
├── user_profiles.json
├── workout_plans.json
├── nutrition_logs.json
└── workout_logs.json
```

**Why use JSON locally?**
- No AWS setup required
- Easy to debug (just open the file)
- Instant testing
- Free

### Production (DynamoDB)

```bash
export USE_DYNAMODB=true
export DYNAMODB_USER_PROFILES=health-chatbot-dev-user_profiles
export DYNAMODB_WORKOUT_PLANS=health-chatbot-dev-workout_plans
# ... etc
```

**Same code, different backend!**

```python
# This works with both JSON and DynamoDB
profile = db.find_one("user_profiles", {"user_id": "demo_user"})
```

---

## Real-World Usage Examples

### Example 1: User Logs Breakfast

**Frontend:**
```javascript
POST /api/nutrition/logs
{
  "user_id": "demo_user",
  "date": "2024-12-31",
  "meal_type": "breakfast",
  "time": "08:00:00",
  "calories": 450,
  "protein": 30.0,
  "carbs": 45.0,
  "fats": 15.0,
  "food_items": [...]
}
```

**Backend (server.py):**
```python
@app.post("/api/nutrition/logs")
async def create_nutrition_log(log: NutritionLogCreate):
    # 1. Insert nutrition log
    log_dict = NutritionLog(**log.dict()).dict()
    db.insert("nutrition_logs", log_dict)

    # 2. Update daily summary
    summary = db.find_one("daily_summaries", {
        "user_id": log.user_id,
        "date": log.date
    })

    if summary:
        # Add to existing totals
        summary["total_calories"] += log.calories
        summary["total_protein"] += log.protein
        db.update("daily_summaries", {"id": summary["id"]}, summary)
    else:
        # Create new summary
        db.insert("daily_summaries", {...})
```

**DynamoDB adapter (dynamodb_adapter.py):**
```python
def insert(self, collection: str, document: Dict) -> Dict:
    table = self._get_table(collection)  # Get DynamoDB table
    item = self._convert_to_dynamodb(document)  # Convert floats to Decimal
    table.put_item(Item=item)  # Save to DynamoDB
    return document
```

**Result:**
- Nutrition log saved to `nutrition_logs` table
- Daily summary updated in `daily_summaries` table
- Dashboard instantly shows updated calorie count

---

### Example 2: Get Last 14 Days of Nutrition

**Frontend:**
```javascript
GET /api/nutrition/logs?user_id=demo_user&start_date=2024-12-17&end_date=2024-12-31
```

**Backend:**
```python
@app.get("/api/nutrition/logs")
async def get_nutrition_logs(user_id: str, start_date: date, end_date: date):
    # Get all logs for this user
    all_logs = db.find("nutrition_logs", {"user_id": user_id})

    # Filter by date range
    filtered_logs = [
        log for log in all_logs
        if start_date <= datetime.fromisoformat(log["date"]).date() <= end_date
    ]

    return sorted(filtered_logs, key=lambda x: x["date"])
```

**DynamoDB adapter:**
```python
def find(self, collection: str, query: Dict) -> List[Dict]:
    table = self._get_table(collection)

    # Use UserIdDateIndex for fast query
    response = table.query(
        IndexName="UserIdDateIndex",
        KeyConditionExpression=Key('user_id').eq(query['user_id'])
    )

    items = [self._convert_from_dynamodb(item) for item in response['Items']]
    return items
```

**DynamoDB Query:**
```
Table: health-chatbot-dev-nutrition_logs
Index: UserIdDateIndex
Condition: user_id = "demo_user"
Result: Returns ALL nutrition logs for this user (instant)
```

**Performance:**
- Without index: Scan 100,000 nutrition logs → 5 seconds
- With index: Query user's 300 logs → 50 milliseconds

---

### Example 3: Dashboard Loads Today's Summary

**Frontend:**
```javascript
GET /api/summary/daily?user_id=demo_user&date=2024-12-31
```

**Backend:**
```python
@app.get("/api/summary/daily")
async def get_daily_summary(user_id: str, date: str):
    summary = db.find_one("daily_summaries", {
        "user_id": user_id,
        "date": date
    })

    if not summary:
        # Create empty summary if doesn't exist
        summary = {
            "user_id": user_id,
            "date": date,
            "total_calories": 0,
            "total_protein": 0,
            "workouts_completed": 0
        }

    return summary
```

**DynamoDB Query:**
```
Table: health-chatbot-dev-daily_summaries
Index: UserIdDateIndex
Condition: user_id = "demo_user" AND date = "2024-12-31"
Result: One document (instant)
```

**Why this is fast:**
- Reads 1 pre-calculated document instead of summing 10+ nutrition logs
- Uses composite index (user_id + date) for instant lookup
- Response time: ~10 milliseconds

---

## Data Type Conversions (Python ↔ DynamoDB)

DynamoDB uses special data types. The adapter handles conversions automatically.

### Python to DynamoDB:

```python
def _convert_to_dynamodb(self, data: Dict) -> Dict:
    """
    Python float → DynamoDB Decimal
    Python datetime → ISO string
    """
    return json.loads(json.dumps(data, default=str), parse_float=Decimal)
```

**Example:**
```python
# Python object
{
  "calories": 2150.5,        # float
  "created_at": datetime.now()  # datetime
}

# Converted to DynamoDB
{
  "calories": Decimal("2150.5"),    # Decimal
  "created_at": "2024-12-31T10:30:00"  # string
}
```

### DynamoDB to Python:

```python
def _convert_from_dynamodb(self, data: Dict) -> Dict:
    """
    DynamoDB Decimal → Python float
    """
    return json.loads(json.dumps(data, cls=DecimalEncoder))
```

**Why?**
- DynamoDB doesn't support native floats (uses Decimal for precision)
- Python JSON doesn't support Decimal (needs conversion)
- The adapter handles this transparently

---

## Cost Structure

DynamoDB has two pricing models:

### 1. On-Demand (Pay-per-Request) ← FitTracker uses this

**What you pay for:**
- **Writes:** $1.25 per million write requests
- **Reads:** $0.25 per million read requests
- **Storage:** $0.25 per GB per month

**Example monthly cost for small app:**
```
User activity:
- 10 nutrition logs/day = 300 writes/month
- 10 workout logs/month = 10 writes
- 100 dashboard loads = 100 reads
- 1 GB storage

Cost:
- Writes: 310 × $1.25/million = $0.0004
- Reads: 100 × $0.25/million = $0.00002
- Storage: 1 GB × $0.25 = $0.25

Total: ~$0.25/month
```

**Perfect for:**
- Side projects
- Startups
- Unpredictable traffic
- Development/testing

### 2. Provisioned Capacity (Monthly Commitment)

**What you pay for:**
- Reserve read/write capacity units per month
- Cheaper if you have predictable, steady traffic
- Requires capacity planning

**Example:**
- 5 WCU (write capacity units) = $3.65/month
- 5 RCU (read capacity units) = $0.73/month
- Total: ~$4.38/month (cheaper at high volume)

**Perfect for:**
- Production apps with steady traffic
- Predictable workloads
- Large-scale applications

**FitTracker uses on-demand because:**
- Sporadic usage (users log food occasionally)
- No idle costs when inactive
- Scales automatically during traffic spikes

---

## DynamoDB vs Other Databases

| Feature | DynamoDB | PostgreSQL | MongoDB | MySQL |
|---------|----------|------------|---------|-------|
| **Type** | NoSQL (Key-Value) | SQL (Relational) | NoSQL (Document) | SQL (Relational) |
| **Scaling** | Automatic | Manual (sharding) | Manual (sharding) | Manual (replication) |
| **Management** | Fully managed | Self-managed | Self-managed | Self-managed |
| **Pricing** | Pay-per-use | Server costs | Server costs | Server costs |
| **Setup** | Zero (just create table) | Install, configure | Install, configure | Install, configure |
| **Performance** | Sub-10ms always | Varies with load | Varies with load | Varies with load |
| **Schema** | Flexible (schemaless) | Rigid (tables) | Flexible (schemaless) | Rigid (tables) |
| **Queries** | Key-based (simple) | Complex SQL (JOINs) | Rich queries | Complex SQL (JOINs) |
| **Best For** | Serverless apps | Complex queries | Flexible data | Traditional apps |

**When to use DynamoDB:**
- Building serverless apps (AWS Lambda)
- Need automatic scaling
- Want zero server management
- Simple key-value queries
- Unpredictable traffic patterns

**When NOT to use DynamoDB:**
- Need complex JOINs across tables
- Require ad-hoc queries (analytics)
- Want traditional SQL
- Need ACID transactions across tables

---

## Development Workflow: JSON → DynamoDB

### Local Development (JSON Files)

```bash
# backend/.env
USE_DYNAMODB=false

# Start server
cd backend
uv run uvicorn server:app --reload
```

**Result:**
- Data saved to `data/tracking/*.json`
- Easy to inspect and debug
- No AWS credentials needed
- Instant testing

### Testing on AWS (DynamoDB)

```bash
# Deploy to AWS
./scripts/deploy.sh dev

# Lambda environment variables automatically set:
USE_DYNAMODB=true
DYNAMODB_USER_PROFILES=health-chatbot-dev-user_profiles
DYNAMODB_NUTRITION_LOGS=health-chatbot-dev-nutrition_logs
# ... etc
```

**Result:**
- Same code runs on AWS Lambda
- Data saved to DynamoDB tables
- Production-ready

**The beauty:**
```python
# This line works in BOTH environments
profile = db.find_one("user_profiles", {"user_id": "demo_user"})

# Local dev: Reads data/tracking/user_profiles.json
# AWS Lambda: Queries DynamoDB table
```

---

## Sample Data Generation

The app includes a script to generate realistic 90-day fitness data.

**Script:** `scripts/insert_sample_data_to_dynamodb.py`

**What it creates:**
```
Demo User (demo_user_90day):
├── 1 user profile (goals, targets, stats)
├── 10 exercise configurations (progression rules)
├── 91 body logs (daily weight + weekly skinfolds)
├── ~200 nutrition logs (2-3 meals/day, 80% compliance)
├── ~50 workout logs (4x/week training)
└── 91 daily summaries (pre-calculated totals)
```

**Realistic features:**
- Weight loss progression (~0.5% per week)
- Weekend calorie spikes (cheat meals)
- Occasional missed workouts (90% compliance)
- Progressive overload in strength training
- Noisy weight data (water retention)
- Plateau simulation (week 5-6)

**Usage:**
```bash
python scripts/insert_sample_data_to_dynamodb.py
```

**Why this is useful:**
- Test the app with realistic data
- Demo the nutrition and training analyzers
- See how AI agents analyze trends
- Validate queries and performance

---

## Security & Backup Features

### 1. Encryption at Rest

All DynamoDB tables are encrypted using AWS-managed keys.

**Terraform configuration:**
```hcl
resource "aws_dynamodb_table" "tracking_tables" {
  server_side_encryption {
    enabled = true
  }
}
```

**What this means:**
- Data is encrypted on AWS servers
- Automatic (no configuration needed)
- Meets compliance requirements

### 2. Point-in-Time Recovery (PITR)

Can restore your database to any moment in the past 35 days.

**Terraform configuration:**
```hcl
resource "aws_dynamodb_table" "tracking_tables" {
  point_in_time_recovery {
    enabled = true
  }
}
```

**Example:**
```
Oops! I accidentally deleted all data at 10:30 AM.

Solution:
1. Go to DynamoDB console
2. Select "Restore to point in time"
3. Choose 10:29 AM
4. Create restored table
5. All data back! ✅
```

### 3. IAM Access Control

Only Lambda function can access DynamoDB tables.

**Terraform configuration:**
```hcl
resource "aws_iam_role_policy" "lambda_dynamodb" {
  policy = jsonencode({
    Statement = [{
      Effect = "Allow"
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ]
      Resource = [aws_dynamodb_table.tracking_tables["*"].arn]
    }]
  })
}
```

**What this means:**
- Only authorized Lambda function can read/write
- No public access
- Follows principle of least privilege

### 4. Audit Logging (CloudTrail)

All DynamoDB operations are logged.

**What gets logged:**
- Who accessed the data
- What operation (read/write/delete)
- When it happened
- From which IP address

**Use case:**
- Security audits
- Compliance requirements
- Debugging access issues

---

## Common Operations

### Create a New Item

```python
from database import db

# Insert user profile
db.insert("user_profiles", {
    "user_id": "new_user_123",
    "name": "John Doe",
    "age": 25,
    "target_calories": 2500,
    "created_at": datetime.now().isoformat()
})
```

### Read a Single Item

```python
# Get user profile
profile = db.find_one("user_profiles", {"user_id": "new_user_123"})

if profile:
    print(f"Target calories: {profile['target_calories']}")
else:
    print("Profile not found")
```

### Read Multiple Items

```python
# Get all nutrition logs for today
logs = db.find("nutrition_logs", {
    "user_id": "new_user_123",
    "date": "2024-12-31"
})

total_calories = sum(log["calories"] for log in logs)
print(f"Total calories today: {total_calories}")
```

### Update an Item

```python
# Update user's target calories
db.update(
    "user_profiles",
    {"user_id": "new_user_123"},
    {"target_calories": 2800, "updated_at": datetime.now().isoformat()}
)
```

### Delete an Item

```python
# Delete a nutrition log
db.delete("nutrition_logs", {"id": "uuid-12345"})
```

---

## Performance Optimization Tips

### 1. Use Indexes for Queries

**Bad (slow):**
```python
# Scans entire table
all_logs = db.find("nutrition_logs", {"user_id": "user_123"})
```

**Good (fast):**
```python
# Uses UserIdDateIndex
all_logs = db.find("nutrition_logs", {"user_id": "user_123"})
# Adapter automatically uses the index ✅
```

### 2. Pre-Calculate Aggregates

**Bad (slow):**
```python
# Sum calories every time dashboard loads
logs = db.find("nutrition_logs", {"user_id": "user_123", "date": "2024-12-31"})
total_calories = sum(log["calories"] for log in logs)
```

**Good (fast):**
```python
# Read pre-calculated summary
summary = db.find_one("daily_summaries", {"user_id": "user_123", "date": "2024-12-31"})
total_calories = summary["total_calories"]
```

### 3. Limit Date Ranges

**Bad (expensive):**
```python
# Queries entire year (365 days × 3 meals = 1,095 items)
logs = db.find("nutrition_logs", {"user_id": "user_123"})
```

**Good (cheap):**
```python
# Queries only last 7 days (21 items)
logs = db.find("nutrition_logs", {"user_id": "user_123"})
recent_logs = [log for log in logs if log["date"] >= "2024-12-24"]
```

### 4. Batch Writes

**Bad (slow):**
```python
# 10 separate write requests
for i in range(10):
    db.insert("nutrition_logs", {...})
```

**Good (fast):**
```python
# 1 batch write request (DynamoDB supports batch operations)
# Note: Current adapter doesn't implement batch writes, but could be added
```

---

## Troubleshooting Common Issues

### Issue 1: "Table not found"

**Error:**
```
An error occurred (ResourceNotFoundException) when calling the PutItem operation:
Requested resource not found
```

**Cause:** DynamoDB table doesn't exist or wrong table name.

**Solution:**
```bash
# Check environment variables
echo $DYNAMODB_USER_PROFILES

# Should output: health-chatbot-dev-user_profiles

# If empty, run Terraform
cd terraform
terraform apply
```

---

### Issue 2: "ValidationException: One or more parameter values were invalid"

**Error:**
```
ValidationException: One or more parameter values were invalid:
Type mismatch for key user_id expected: S actual: N
```

**Cause:** Wrong data type for key (e.g., passing number instead of string).

**Solution:**
```python
# Bad
db.find_one("user_profiles", {"user_id": 123})  # Number ❌

# Good
db.find_one("user_profiles", {"user_id": "123"})  # String ✅
```

---

### Issue 3: "AccessDeniedException"

**Error:**
```
AccessDeniedException: User is not authorized to perform: dynamodb:PutItem
```

**Cause:** Lambda IAM role doesn't have DynamoDB permissions.

**Solution:**
```bash
# Check Terraform IAM policy
cd terraform
terraform plan | grep lambda_dynamodb

# Ensure policy includes PutItem, GetItem, Query, etc.
```

---

### Issue 4: Slow Queries

**Problem:** Queries taking 3-5 seconds.

**Cause:** Using Scan instead of Query (no index).

**Solution:**
```python
# Check if query uses index
# DynamoDB adapter should use UserIdDateIndex for user_id queries

# If still slow, check CloudWatch metrics:
# - Scan operations should be 0
# - Query operations should be high
```

---

## Summary

**DynamoDB** is a fully managed, serverless NoSQL database perfect for the FitTracker AI app because:

1. **Zero Management** - No servers, no maintenance, AWS handles everything
2. **Automatic Scaling** - Handles 10 or 10 million requests/second
3. **Pay-per-Use** - Only pay when you use it (~$0.25/month for small apps)
4. **Lightning Fast** - Sub-10ms response times at any scale
5. **Built-in Backups** - Point-in-time recovery for 35 days
6. **Serverless-Friendly** - Perfect for AWS Lambda

**The 9 Tables:**
1. **user_profiles** - User account info and daily targets
2. **workout_plans** - AI-generated workout programs
3. **nutrition_logs** - Every meal logged (breakfast, lunch, dinner, snacks)
4. **workout_logs** - Completed training sessions with sets/reps/weights
5. **body_logs** - Daily weight and weekly body measurements
6. **daily_summaries** - Pre-calculated daily totals (fast dashboard loading)
7. **user_exercises** - Exercise progression configurations
8. **training_recommendations** - AI coaching advice after each workout
9. **training_progress_summaries** - Weekly training performance reports

**Key Concepts:**
- **Primary Keys** - Unique identifiers for instant lookups
- **Global Secondary Indexes** - Fast queries by user_id + date
- **Adapter Pattern** - Same code works with JSON (local) and DynamoDB (production)
- **Data Conversions** - Automatic Python ↔ DynamoDB type conversions

**Cost Example:**
- Small app: ~$0.25/month (on-demand pricing)
- Medium app: ~$5/month (1,000 users, moderate activity)
- Large app: ~$50/month (10,000 users, high activity)

Think of DynamoDB as **"Google Sheets in the cloud, but infinitely scalable and with millisecond response times."** You describe your data structure once (tables), and AWS handles all the infrastructure, scaling, and reliability forever!
