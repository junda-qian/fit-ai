# Tracking System Implementation Guide

## Overview

This document provides a **step-by-step guide** to implement the complete tracking system for Fit AI, including USDA FoodData Central API integration for food logging.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: USDA API Setup](#phase-1-usda-api-setup)
3. [Phase 2: Backend - Data Models & Database](#phase-2-backend---data-models--database)
4. [Phase 3: Backend - API Endpoints](#phase-3-backend---api-endpoints)
5. [Phase 4: Backend - Food Database Integration](#phase-4-backend---food-database-integration)
6. [Phase 5: Frontend - Save Calculator & Planner Results](#phase-5-frontend---save-calculator--planner-results)
7. [Phase 6: Frontend - Tracking Dashboard](#phase-6-frontend---tracking-dashboard)
8. [Phase 7: Frontend - Nutrition Logging](#phase-7-frontend---nutrition-logging)
9. [Phase 8: Frontend - Workout Logging](#phase-8-frontend---workout-logging)
10. [Phase 9: Progress Views & Charts](#phase-9-progress-views--charts)
11. [Testing & Deployment](#testing--deployment)

---

## Prerequisites

### Tools Needed
- ✅ Python 3.12+ (backend)
- ✅ Node.js 18+ (frontend)
- ✅ Git (version control)
- ✅ USDA API key (free)
- ✅ Database choice: Start with local JSON files, migrate to DynamoDB later

### Knowledge Requirements
- Basic Python (FastAPI)
- Basic React/TypeScript
- REST API concepts
- Git branching

---

## Phase 1: USDA API Setup

### Step 1.1: Get Your Free USDA API Key

1. **Visit USDA FoodData Central:**
   - Go to: https://fdc.nal.usda.gov/api-guide.html
   - Click "Get API Key" or go to: https://fdc.nal.usda.gov/api-key-signup.html

2. **Sign Up:**
   - Enter your email address
   - Agree to terms
   - Submit

3. **Check Email:**
   - You'll receive an API key instantly
   - Copy the key (format: `xxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

4. **Add to Environment Variables:**
   ```bash
   # In backend/.env
   USDA_API_KEY=your-api-key-here
   ```

### Step 1.2: Test the API

Test with curl:
```bash
curl "https://api.nal.usda.gov/fdc/v1/foods/search?api_key=YOUR_KEY&query=banana"
```

Expected response:
```json
{
  "totalHits": 100,
  "foods": [
    {
      "fdcId": 173944,
      "description": "Bananas, raw",
      "dataType": "Survey (FNDDS)",
      "foodNutrients": [
        {
          "nutrientId": 1003,
          "nutrientName": "Protein",
          "value": 1.09,
          "unitName": "G"
        },
        {
          "nutrientId": 1005,
          "nutrientName": "Carbohydrate, by difference",
          "value": 22.84,
          "unitName": "G"
        }
      ]
    }
  ]
}
```

---

## Phase 2: Backend - Data Models & Database

### Step 2.1: Choose Database Strategy

**For MVP (Recommended):**
Use **local JSON files** stored in `backend/data/tracking/`

**For Production:**
Migrate to **DynamoDB** or **PostgreSQL**

### Step 2.2: Create Data Models

**File:** `backend/models.py`

```python
"""
Data models for tracking system
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date, time
from uuid import UUID, uuid4


# ==================== User Profile ====================

class UserProfile(BaseModel):
    """User's fitness targets from calculator"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    target_calories: int
    target_protein: float
    target_carbs: float
    target_fats: float
    bmr: float
    tdee: float
    activity_level: float
    goal: str  # "bulk", "cut", "maintain"
    body_weight_kg: float
    body_fat_pct: float
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserProfileCreate(BaseModel):
    """Request model for creating user profile"""
    user_id: str
    target_calories: int
    target_protein: float
    target_carbs: float
    target_fats: float
    bmr: float
    tdee: float
    activity_level: float
    goal: str
    body_weight_kg: float
    body_fat_pct: float


# ==================== Workout Plans ====================

class Exercise(BaseModel):
    """Single exercise in a workout plan"""
    name: str
    sets: int
    reps: str  # e.g., "6-8", "10-12"
    rpe: float  # Rate of Perceived Exertion
    muscle_group: str
    day: str  # e.g., "Upper A", "Lower B"


class WorkoutPlan(BaseModel):
    """User's workout plan from planner"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    plan_name: str
    description: str
    frequency: str  # e.g., "4x/week"
    exercises: List[Exercise]
    duration_weeks: int
    active: bool = True
    generated_at: datetime = Field(default_factory=datetime.now)
    deactivated_at: Optional[datetime] = None


class WorkoutPlanCreate(BaseModel):
    """Request model for creating workout plan"""
    user_id: str
    plan_name: str
    description: str
    frequency: str
    exercises: List[Dict]  # Will be converted to Exercise objects
    duration_weeks: int


# ==================== Nutrition Logging ====================

class FoodItem(BaseModel):
    """Individual food item in a meal"""
    name: str
    amount: str  # e.g., "100g", "1 medium"
    calories: float
    protein: float
    carbs: float
    fats: float
    fdc_id: Optional[int] = None  # USDA FoodData Central ID


class NutritionLog(BaseModel):
    """Single meal/snack entry"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    date: date
    meal_type: str  # "breakfast", "lunch", "dinner", "snack"
    time: time
    calories: float
    protein: float
    carbs: float
    fats: float
    food_items: List[FoodItem]
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class NutritionLogCreate(BaseModel):
    """Request model for creating nutrition log"""
    user_id: str
    date: date
    meal_type: str
    time: time
    calories: float
    protein: float
    carbs: float
    fats: float
    food_items: List[Dict]  # Will be converted to FoodItem objects
    notes: Optional[str] = None


# ==================== Workout Logging ====================

class ExerciseSet(BaseModel):
    """Single set in a workout"""
    reps: int
    weight: float  # in lbs or kg
    rpe: float  # 1-10 scale


class WorkoutExercise(BaseModel):
    """Exercise performed in a workout"""
    name: str
    sets: List[ExerciseSet]


class WorkoutLog(BaseModel):
    """Completed workout session"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    date: date
    workout_name: str
    exercises: List[WorkoutExercise]
    duration_minutes: int
    notes: Optional[str] = None
    completed: bool = True
    created_at: datetime = Field(default_factory=datetime.now)


class WorkoutLogCreate(BaseModel):
    """Request model for creating workout log"""
    user_id: str
    date: date
    workout_name: str
    exercises: List[Dict]
    duration_minutes: int
    notes: Optional[str] = None
    completed: bool = True


# ==================== Body Logs ====================

class BodyLog(BaseModel):
    """Body measurements and weight tracking"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    date: date
    weight: float  # in kg or lbs
    body_fat_pct: Optional[float] = None
    measurements: Optional[Dict[str, float]] = None  # chest, waist, arms, etc.
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class BodyLogCreate(BaseModel):
    """Request model for creating body log"""
    user_id: str
    date: date
    weight: float
    body_fat_pct: Optional[float] = None
    measurements: Optional[Dict[str, float]] = None
    notes: Optional[str] = None


# ==================== Daily Summary ====================

class DailySummary(BaseModel):
    """Pre-computed daily aggregation"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fats: float
    workouts_completed: int
    weight: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ==================== USDA Food Database ====================

class USDAFood(BaseModel):
    """Parsed food from USDA API"""
    fdc_id: int
    description: str
    calories: float
    protein: float
    carbs: float
    fats: float
    serving_size: str
    serving_unit: str


class FoodSearchResult(BaseModel):
    """Search results from USDA API"""
    query: str
    total_results: int
    foods: List[USDAFood]
```

### Step 2.3: Create Database Helper

**File:** `backend/database.py`

```python
"""
Simple JSON file-based database for MVP
Will be replaced with DynamoDB/PostgreSQL in production
"""
import json
import os
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pathlib import Path


class JSONDatabase:
    """Simple file-based database using JSON"""

    def __init__(self, data_dir: str = "data/tracking"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create separate files for each collection
        self.collections = {
            "user_profiles": self.data_dir / "user_profiles.json",
            "workout_plans": self.data_dir / "workout_plans.json",
            "nutrition_logs": self.data_dir / "nutrition_logs.json",
            "workout_logs": self.data_dir / "workout_logs.json",
            "body_logs": self.data_dir / "body_logs.json",
            "daily_summaries": self.data_dir / "daily_summaries.json",
        }

        # Initialize empty collections if they don't exist
        for collection_file in self.collections.values():
            if not collection_file.exists():
                self._write_file(collection_file, [])

    def _read_file(self, file_path: Path) -> List[Dict]:
        """Read JSON file"""
        with open(file_path, 'r') as f:
            return json.load(f)

    def _write_file(self, file_path: Path, data: List[Dict]):
        """Write JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def insert(self, collection: str, document: Dict) -> Dict:
        """Insert a document"""
        file_path = self.collections[collection]
        data = self._read_file(file_path)
        data.append(document)
        self._write_file(file_path, data)
        return document

    def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        """Find single document"""
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        for doc in data:
            if all(doc.get(k) == v for k, v in query.items()):
                return doc
        return None

    def find(self, collection: str, query: Dict) -> List[Dict]:
        """Find multiple documents"""
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        results = []
        for doc in data:
            if all(doc.get(k) == v for k, v in query.items()):
                results.append(doc)
        return results

    def update(self, collection: str, query: Dict, update: Dict) -> bool:
        """Update documents"""
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        updated = False
        for doc in data:
            if all(doc.get(k) == v for k, v in query.items()):
                doc.update(update)
                doc['updated_at'] = datetime.now().isoformat()
                updated = True

        if updated:
            self._write_file(file_path, data)
        return updated

    def delete(self, collection: str, query: Dict) -> int:
        """Delete documents"""
        file_path = self.collections[collection]
        data = self._read_file(file_path)

        original_length = len(data)
        data = [doc for doc in data if not all(doc.get(k) == v for k, v in query.items())]

        self._write_file(file_path, data)
        return original_length - len(data)


# Global database instance
db = JSONDatabase()
```

---

## Phase 3: Backend - API Endpoints

### Step 3.1: Add Tracking Endpoints to server.py

**File:** `backend/server.py` (add these routes)

```python
from models import (
    UserProfile, UserProfileCreate,
    WorkoutPlan, WorkoutPlanCreate,
    NutritionLog, NutritionLogCreate,
    WorkoutLog, WorkoutLogCreate,
    BodyLog, BodyLogCreate,
    DailySummary
)
from database import db
from datetime import date, datetime, timedelta


# ==================== User Profile Endpoints ====================

@app.post("/api/user-profile", response_model=UserProfile)
async def create_user_profile(profile: UserProfileCreate):
    """Save user's targets from energy calculator"""
    try:
        # Check if profile already exists
        existing = db.find_one("user_profiles", {"user_id": profile.user_id})

        if existing:
            # Update existing profile
            profile_dict = profile.dict()
            profile_dict['updated_at'] = datetime.now().isoformat()
            db.update("user_profiles", {"user_id": profile.user_id}, profile_dict)
            return UserProfile(**profile_dict, id=existing['id'], created_at=existing['created_at'])
        else:
            # Create new profile
            profile_obj = UserProfile(**profile.dict())
            profile_dict = profile_obj.dict()
            profile_dict = json.loads(json.dumps(profile_dict, default=str))
            db.insert("user_profiles", profile_dict)
            return profile_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user-profile/{user_id}")
async def get_user_profile(user_id: str):
    """Get user's profile and targets"""
    try:
        profile = db.find_one("user_profiles", {"user_id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Workout Plan Endpoints ====================

@app.post("/api/workout-plan", response_model=WorkoutPlan)
async def create_workout_plan(plan: WorkoutPlanCreate):
    """Save workout plan from planner"""
    try:
        # Deactivate any existing active plans
        db.update(
            "workout_plans",
            {"user_id": plan.user_id, "active": True},
            {"active": False, "deactivated_at": datetime.now().isoformat()}
        )

        # Create new active plan
        plan_obj = WorkoutPlan(**plan.dict())
        plan_dict = plan_obj.dict()
        plan_dict = json.loads(json.dumps(plan_dict, default=str))
        db.insert("workout_plans", plan_dict)
        return plan_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workout-plan/{user_id}/active")
async def get_active_workout_plan(user_id: str):
    """Get user's currently active workout plan"""
    try:
        plan = db.find_one("workout_plans", {"user_id": user_id, "active": True})
        if not plan:
            raise HTTPException(status_code=404, detail="No active workout plan found")
        return plan
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workout-plan/{user_id}/all")
async def get_all_workout_plans(user_id: str):
    """Get all workout plans for user (history)"""
    try:
        plans = db.find("workout_plans", {"user_id": user_id})
        # Sort by generated_at descending
        plans.sort(key=lambda x: x['generated_at'], reverse=True)
        return plans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Nutrition Logging Endpoints ====================

@app.post("/api/nutrition/logs", response_model=NutritionLog)
async def create_nutrition_log(log: NutritionLogCreate):
    """Log a meal or snack"""
    try:
        log_obj = NutritionLog(**log.dict())
        log_dict = log_obj.dict()
        log_dict = json.loads(json.dumps(log_dict, default=str))
        db.insert("nutrition_logs", log_dict)

        # Update daily summary
        await _update_daily_summary(log.user_id, log.date)

        return log_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/nutrition/logs")
async def get_nutrition_logs(
    user_id: str,
    start_date: date,
    end_date: date
):
    """Get nutrition logs for date range (max 31 days)"""
    try:
        # Validate date range
        if (end_date - start_date).days > 31:
            raise HTTPException(status_code=400, detail="Max 31 days per request")

        # Find logs in date range
        all_logs = db.find("nutrition_logs", {"user_id": user_id})

        # Filter by date range
        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]

        # Sort by date and time
        filtered_logs.sort(key=lambda x: (x['date'], x['time']), reverse=True)

        return {
            "logs": filtered_logs,
            "total_count": len(filtered_logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Workout Logging Endpoints ====================

@app.post("/api/workout/logs", response_model=WorkoutLog)
async def create_workout_log(log: WorkoutLogCreate):
    """Log a workout session"""
    try:
        log_obj = WorkoutLog(**log.dict())
        log_dict = log_obj.dict()
        log_dict = json.loads(json.dumps(log_dict, default=str))
        db.insert("workout_logs", log_dict)

        # Update daily summary
        await _update_daily_summary(log.user_id, log.date)

        return log_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workout/logs")
async def get_workout_logs(
    user_id: str,
    start_date: date,
    end_date: date
):
    """Get workout logs for date range (max 31 days)"""
    try:
        # Validate date range
        if (end_date - start_date).days > 31:
            raise HTTPException(status_code=400, detail="Max 31 days per request")

        # Find logs in date range
        all_logs = db.find("workout_logs", {"user_id": user_id})

        # Filter by date range
        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]

        # Sort by date
        filtered_logs.sort(key=lambda x: x['date'], reverse=True)

        return {
            "logs": filtered_logs,
            "total_count": len(filtered_logs)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Body Logging Endpoints ====================

@app.post("/api/body/logs", response_model=BodyLog)
async def create_body_log(log: BodyLogCreate):
    """Log body weight and measurements"""
    try:
        log_obj = BodyLog(**log.dict())
        log_dict = log_obj.dict()
        log_dict = json.loads(json.dumps(log_dict, default=str))
        db.insert("body_logs", log_dict)

        # Update daily summary
        await _update_daily_summary(log.user_id, log.date)

        return log_obj
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/body/logs")
async def get_body_logs(
    user_id: str,
    start_date: date,
    end_date: date
):
    """Get body logs for date range"""
    try:
        all_logs = db.find("body_logs", {"user_id": user_id})

        # Filter by date range
        filtered_logs = [
            log for log in all_logs
            if start_date <= datetime.fromisoformat(log['date']).date() <= end_date
        ]

        # Sort by date
        filtered_logs.sort(key=lambda x: x['date'], reverse=True)

        return filtered_logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Summary Endpoints ====================

@app.get("/api/summary/daily")
async def get_daily_summary(user_id: str, date: date):
    """Get aggregated summary for a specific day"""
    try:
        # Check if summary exists
        summary = db.find_one("daily_summaries", {"user_id": user_id, "date": date.isoformat()})

        if not summary:
            # Compute summary if it doesn't exist
            summary = await _compute_daily_summary(user_id, date)

        # Get user profile for targets
        profile = db.find_one("user_profiles", {"user_id": user_id})

        if profile:
            summary['targets'] = {
                "calories": profile['target_calories'],
                "protein": profile['target_protein'],
                "carbs": profile['target_carbs'],
                "fats": profile['target_fats']
            }

            # Calculate progress percentages
            summary['progress'] = {
                "calories_pct": round((summary['total_calories'] / profile['target_calories']) * 100) if profile['target_calories'] > 0 else 0,
                "protein_pct": round((summary['total_protein'] / profile['target_protein']) * 100) if profile['target_protein'] > 0 else 0,
                "carbs_pct": round((summary['total_carbs'] / profile['target_carbs']) * 100) if profile['target_carbs'] > 0 else 0,
                "fats_pct": round((summary['total_fats'] / profile['target_fats']) * 100) if profile['target_fats'] > 0 else 0,
            }

        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary/weekly")
async def get_weekly_summary(
    user_id: str,
    start_date: date,
    end_date: date
):
    """Get aggregated summary for a week"""
    try:
        # Get all daily summaries in range
        all_summaries = db.find("daily_summaries", {"user_id": user_id})

        summaries_in_range = [
            s for s in all_summaries
            if start_date <= datetime.fromisoformat(s['date']).date() <= end_date
        ]

        if not summaries_in_range:
            return {
                "week_start": start_date.isoformat(),
                "week_end": end_date.isoformat(),
                "avg_calories": 0,
                "avg_protein": 0,
                "avg_carbs": 0,
                "avg_fats": 0,
                "training_days": 0,
                "weight_change": 0,
                "weight_start": None,
                "weight_end": None
            }

        days_count = len(summaries_in_range)

        # Calculate averages
        avg_calories = sum(s['total_calories'] for s in summaries_in_range) / days_count
        avg_protein = sum(s['total_protein'] for s in summaries_in_range) / days_count
        avg_carbs = sum(s['total_carbs'] for s in summaries_in_range) / days_count
        avg_fats = sum(s['total_fats'] for s in summaries_in_range) / days_count
        training_days = sum(s['workouts_completed'] for s in summaries_in_range)

        # Get weight change
        weights = [s['weight'] for s in summaries_in_range if s.get('weight')]
        weight_start = weights[0] if weights else None
        weight_end = weights[-1] if weights else None
        weight_change = (weight_end - weight_start) if (weight_start and weight_end) else 0

        return {
            "week_start": start_date.isoformat(),
            "week_end": end_date.isoformat(),
            "avg_calories": round(avg_calories, 1),
            "avg_protein": round(avg_protein, 1),
            "avg_carbs": round(avg_carbs, 1),
            "avg_fats": round(avg_fats, 1),
            "training_days": training_days,
            "weight_change": round(weight_change, 2),
            "weight_start": weight_start,
            "weight_end": weight_end
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Helper Functions ====================

async def _compute_daily_summary(user_id: str, target_date: date) -> Dict:
    """Compute daily summary from logs"""
    # Get all nutrition logs for the day
    nutrition_logs = db.find("nutrition_logs", {"user_id": user_id})
    day_nutrition = [
        log for log in nutrition_logs
        if datetime.fromisoformat(log['date']).date() == target_date
    ]

    # Get all workout logs for the day
    workout_logs = db.find("workout_logs", {"user_id": user_id})
    day_workouts = [
        log for log in workout_logs
        if datetime.fromisoformat(log['date']).date() == target_date
    ]

    # Get weight for the day
    body_logs = db.find("body_logs", {"user_id": user_id})
    day_body = [
        log for log in body_logs
        if datetime.fromisoformat(log['date']).date() == target_date
    ]

    # Aggregate
    total_calories = sum(log['calories'] for log in day_nutrition)
    total_protein = sum(log['protein'] for log in day_nutrition)
    total_carbs = sum(log['carbs'] for log in day_nutrition)
    total_fats = sum(log['fats'] for log in day_nutrition)
    workouts_completed = len([w for w in day_workouts if w.get('completed', False)])
    weight = day_body[0]['weight'] if day_body else None

    summary = {
        "user_id": user_id,
        "date": target_date.isoformat(),
        "total_calories": total_calories,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fats": total_fats,
        "workouts_completed": workouts_completed,
        "weight": weight,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    return summary


async def _update_daily_summary(user_id: str, target_date: date):
    """Update or create daily summary"""
    summary = await _compute_daily_summary(user_id, target_date)

    # Check if summary exists
    existing = db.find_one("daily_summaries", {
        "user_id": user_id,
        "date": target_date.isoformat()
    })

    if existing:
        db.update(
            "daily_summaries",
            {"user_id": user_id, "date": target_date.isoformat()},
            summary
        )
    else:
        summary['id'] = str(uuid4())
        db.insert("daily_summaries", summary)
```

---

## Phase 4: Backend - Food Database Integration

### Step 4.1: Create USDA API Wrapper

**File:** `backend/food_database.py`

```python
"""
USDA FoodData Central API integration
"""
import os
import requests
from typing import List, Optional
from dotenv import load_dotenv
from models import USDAFood, FoodSearchResult

load_dotenv()

USDA_API_KEY = os.getenv("USDA_API_KEY")
USDA_BASE_URL = "https://api.nal.usda.gov/fdc/v1"


class FoodDatabase:
    """Wrapper for USDA FoodData Central API"""

    def __init__(self, api_key: str = USDA_API_KEY):
        self.api_key = api_key
        self.base_url = USDA_BASE_URL

    def search_foods(self, query: str, page_size: int = 10) -> FoodSearchResult:
        """
        Search for foods in USDA database

        Args:
            query: Search term (e.g., "banana", "chicken breast")
            page_size: Number of results to return (default 10)

        Returns:
            FoodSearchResult with parsed foods
        """
        url = f"{self.base_url}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"]
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Parse results
            foods = []
            for food in data.get("foods", []):
                parsed_food = self._parse_food(food)
                if parsed_food:
                    foods.append(parsed_food)

            return FoodSearchResult(
                query=query,
                total_results=data.get("totalHits", 0),
                foods=foods
            )

        except requests.exceptions.RequestException as e:
            print(f"USDA API error: {e}")
            return FoodSearchResult(query=query, total_results=0, foods=[])

    def _parse_food(self, food_data: dict) -> Optional[USDAFood]:
        """Parse USDA food data into our model"""
        try:
            # Extract basic info
            fdc_id = food_data.get("fdcId")
            description = food_data.get("description", "Unknown Food")

            # Extract nutrients
            nutrients = food_data.get("foodNutrients", [])

            # Map nutrient IDs to values
            nutrient_map = {}
            for nutrient in nutrients:
                nutrient_id = nutrient.get("nutrientId")
                value = nutrient.get("value", 0)
                nutrient_map[nutrient_id] = value

            # USDA Nutrient IDs:
            # 1008 = Energy (kcal)
            # 1003 = Protein
            # 1005 = Carbohydrate
            # 1004 = Total Fat

            calories = nutrient_map.get(1008, 0)
            protein = nutrient_map.get(1003, 0)
            carbs = nutrient_map.get(1005, 0)
            fats = nutrient_map.get(1004, 0)

            # Get serving size (default to 100g)
            serving_size = food_data.get("servingSize", 100)
            serving_unit = food_data.get("servingSizeUnit", "g")

            return USDAFood(
                fdc_id=fdc_id,
                description=description,
                calories=round(calories, 1),
                protein=round(protein, 1),
                carbs=round(carbs, 1),
                fats=round(fats, 1),
                serving_size=str(serving_size),
                serving_unit=serving_unit
            )

        except Exception as e:
            print(f"Error parsing food: {e}")
            return None


# Global instance
food_db = FoodDatabase()
```

### Step 4.2: Add Food Search Endpoint

**File:** `backend/server.py` (add this route)

```python
from food_database import food_db
from models import FoodSearchResult

@app.get("/api/food/search", response_model=FoodSearchResult)
async def search_foods(query: str, page_size: int = 10):
    """
    Search USDA FoodData Central database

    Args:
        query: Food name to search (e.g., "banana", "chicken")
        page_size: Number of results (default 10, max 50)

    Returns:
        List of matching foods with nutrition info
    """
    try:
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

        if page_size > 50:
            page_size = 50

        results = food_db.search_foods(query, page_size)
        return results

    except HTTPException:
        raise
    except Exception as e:
        print(f"Food search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Phase 5: Frontend - Save Calculator & Planner Results

### Step 5.1: Update Energy Calculator Component

**File:** `frontend/components/energy-calculator.tsx`

Add "Save & Continue" button after results:

```tsx
// Add this state at the top
const [saving, setSaving] = useState(false);
const [saved, setSaved] = useState(false);

// Add this function
const handleSaveAndContinue = async () => {
  if (!results) return;

  setSaving(true);

  try {
    // Generate a user ID (in production, this would come from auth)
    const userId = localStorage.getItem('user_id') || generateUserId();
    localStorage.setItem('user_id', userId);

    // Prepare profile data
    const profileData = {
      user_id: userId,
      target_calories: results.average_target_energy_intake,
      target_protein: results.macro_targets.protein_grams,
      target_carbs: results.macro_targets.carbs_grams,
      target_fats: results.macro_targets.fat_grams,
      bmr: results.cunningham_bmr,
      tdee: results.maintenance_energy_intake,
      activity_level: parseFloat(inputs.physical_activity_factor),
      goal: parseFloat(inputs.energy_balance_factor) > 1 ? 'bulk' :
            parseFloat(inputs.energy_balance_factor) < 1 ? 'cut' : 'maintain',
      body_weight_kg: parseFloat(inputs.bodyweight_kg),
      body_fat_pct: parseFloat(inputs.body_fat_percentage)
    };

    // Save to backend
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/user-profile`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileData)
    });

    if (!response.ok) throw new Error('Failed to save profile');

    setSaved(true);

    // Navigate to workout planner after 1 second
    setTimeout(() => {
      window.location.href = '/workout-planner';
    }, 1000);

  } catch (error) {
    console.error('Error saving profile:', error);
    alert('Failed to save targets. Please try again.');
  } finally {
    setSaving(false);
  }
};

// Helper function
function generateUserId() {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Add this button after the target energy intake display
{results && (
  <div className="mt-6 flex gap-3">
    <button
      onClick={() => setResults(null)}
      className="flex-1 bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
    >
      Recalculate
    </button>
    <button
      onClick={handleSaveAndContinue}
      disabled={saving || saved}
      className="flex-1 bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
    >
      {saving ? 'Saving...' : saved ? '✓ Saved! Redirecting...' : 'Save & Continue →'}
    </button>
  </div>
)}
```

### Step 5.2: Update Workout Planner Component

**File:** `frontend/components/workout-planner.tsx`

Add "Start This Plan" button after plan generation:

```tsx
// Add this state at the top
const [saving, setSaving] = useState(false);
const [planSaved, setPlanSaved] = useState(false);

// Add this function after plan is generated
const handleStartPlan = async () => {
  if (!plan) return;

  setSaving(true);

  try {
    const userId = localStorage.getItem('user_id');
    if (!userId) {
      alert('Please complete the Energy Calculator first');
      window.location.href = '/calculator';
      return;
    }

    // Prepare plan data
    const planData = {
      user_id: userId,
      plan_name: plan.plan_name || 'My Workout Plan',
      description: plan.description || 'Personalized workout program',
      frequency: `${inputs.training_days_per_week}x/week`,
      exercises: plan.exercises || [],
      duration_weeks: 8
    };

    // Save to backend
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/workout-plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(planData)
    });

    if (!response.ok) throw new Error('Failed to save plan');

    setPlanSaved(true);

    // Navigate to tracking dashboard after 1 second
    setTimeout(() => {
      window.location.href = '/tracking/dashboard';
    }, 1000);

  } catch (error) {
    console.error('Error saving plan:', error);
    alert('Failed to save workout plan. Please try again.');
  } finally {
    setSaving(false);
  }
};

// Add this button after plan is displayed
{plan && (
  <div className="mt-6 flex gap-3">
    <button
      onClick={handleRegenerate}
      className="flex-1 bg-gray-500 text-white py-3 rounded-lg font-semibold hover:bg-gray-600 transition-colors"
    >
      Generate New Plan
    </button>
    <button
      onClick={handleStartPlan}
      disabled={saving || planSaved}
      className="flex-1 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
    >
      {saving ? 'Saving...' : planSaved ? '✓ Plan Started! Redirecting...' : 'Start This Plan →'}
    </button>
  </div>
)}
```

---

## Phase 6: Frontend - Tracking Dashboard

### Step 6.1: Create Dashboard Page

**File:** `frontend/app/tracking/dashboard/page.tsx`

```tsx
'use client';

import { useState, useEffect } from 'react';
import { TrendingUp, Flame, Dumbbell, Scale } from 'lucide-react';

interface DailySummary {
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fats: number;
  workouts_completed: number;
  weight: number | null;
  targets?: {
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
  };
  progress?: {
    calories_pct: number;
    protein_pct: number;
    carbs_pct: number;
    fats_pct: number;
  };
}

interface WorkoutPlan {
  plan_name: string;
  frequency: string;
  description: string;
}

export default function TrackingDashboard() {
  const [summary, setSummary] = useState<DailySummary | null>(null);
  const [workoutPlan, setWorkoutPlan] = useState<WorkoutPlan | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const userId = localStorage.getItem('user_id');
      if (!userId) {
        window.location.href = '/calculator';
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const today = new Date().toISOString().split('T')[0];

      // Fetch daily summary
      const summaryRes = await fetch(
        `${apiUrl}/api/summary/daily?user_id=${userId}&date=${today}`
      );
      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSummary(summaryData);
      }

      // Fetch active workout plan
      const planRes = await fetch(
        `${apiUrl}/api/workout-plan/${userId}/active`
      );
      if (planRes.ok) {
        const planData = await planRes.json();
        setWorkoutPlan(planData);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const today = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            📊 Dashboard
          </h1>
          <p className="text-gray-600">{today}</p>
        </div>

        {/* Today's Progress Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Nutrition Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Flame className="w-6 h-6 text-orange-600" />
              <h2 className="text-xl font-bold text-gray-800">Nutrition</h2>
            </div>

            {summary?.targets ? (
              <>
                <div className="mb-4">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-gray-600">Calories</span>
                    <span className="text-sm font-semibold text-gray-800">
                      {summary.total_calories} / {summary.targets.calories}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-orange-500 h-3 rounded-full transition-all"
                      style={{ width: `${Math.min(summary.progress?.calories_pct || 0, 100)}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Protein:</span>
                    <span className="font-semibold">{summary.total_protein}g / {summary.targets.protein}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Carbs:</span>
                    <span className="font-semibold">{summary.total_carbs}g / {summary.targets.carbs}g</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Fats:</span>
                    <span className="font-semibold">{summary.total_fats}g / {summary.targets.fats}g</span>
                  </div>
                </div>

                <button className="w-full mt-4 bg-orange-600 text-white py-2 rounded-lg hover:bg-orange-700 transition-colors">
                  + Log Meal
                </button>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No targets set</p>
                <a
                  href="/calculator"
                  className="text-blue-600 hover:underline"
                >
                  Complete Energy Calculator →
                </a>
              </div>
            )}
          </div>

          {/* Workout Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Dumbbell className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-800">Workout</h2>
            </div>

            {workoutPlan ? (
              <>
                <div className="mb-4">
                  <p className="text-sm text-gray-600">Active Plan:</p>
                  <p className="font-semibold text-gray-800">{workoutPlan.plan_name}</p>
                  <p className="text-sm text-gray-500">{workoutPlan.frequency}</p>
                </div>

                {summary && summary.workouts_completed > 0 ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
                    <p className="text-green-800 font-semibold">✅ Completed today</p>
                  </div>
                ) : (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-4">
                    <p className="text-gray-600">⏳ Not logged yet</p>
                  </div>
                )}

                <button className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  + Log Workout
                </button>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No active plan</p>
                <a
                  href="/workout-planner"
                  className="text-blue-600 hover:underline"
                >
                  Create Workout Plan →
                </a>
              </div>
            )}
          </div>

          {/* Weight Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center gap-2 mb-4">
              <Scale className="w-6 h-6 text-purple-600" />
              <h2 className="text-xl font-bold text-gray-800">Weight</h2>
            </div>

            {summary?.weight ? (
              <>
                <div className="text-center py-6">
                  <p className="text-4xl font-bold text-gray-800">{summary.weight}</p>
                  <p className="text-gray-600 mt-1">kg</p>
                </div>

                <button className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors">
                  Update Weight
                </button>
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No weight logged today</p>
                <button className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors">
                  + Log Weight
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-600" />
            This Week
          </h2>
          <div className="text-center text-gray-500 py-8">
            Weekly summary coming soon...
          </div>
        </div>
      </div>
    </div>
  );
}
```

### Step 6.2: Add Navigation Link

**File:** `frontend/components/navigation.tsx`

Add tracking dashboard link:

```tsx
<a
  href="/tracking/dashboard"
  className={`px-4 py-2 rounded-lg transition-colors ${
    currentPath === '/tracking/dashboard'
      ? 'bg-blue-600 text-white'
      : 'bg-white text-gray-700 hover:bg-gray-50'
  }`}
>
  📊 Dashboard
</a>
```

---

## Phase 7: Frontend - Nutrition Logging

**File:** `frontend/app/tracking/nutrition/page.tsx`

This will be the food logging interface with USDA search - **implementation continues in next phase...**

---

## Phase 8: Frontend - Workout Logging

**File:** `frontend/app/tracking/workouts/page.tsx`

Workout logging interface - **implementation continues...**

---

## Phase 9: Progress Views & Charts

Charts and analytics views - **implementation continues...**

---

## Testing & Deployment

### Local Testing Checklist

- [ ] USDA API key works
- [ ] User profile saves correctly
- [ ] Workout plan saves correctly
- [ ] Dashboard displays targets
- [ ] Food search returns results
- [ ] Nutrition logging works
- [ ] Workout logging works
- [ ] Daily summary calculates correctly

### Production Deployment

1. **Backend:**
   - Deploy updated Lambda function
   - Set USDA_API_KEY environment variable
   - Migrate from JSON files to DynamoDB

2. **Frontend:**
   - Update API URLs for production
   - Build and deploy to S3/CloudFront

---

## Next Steps

After completing this implementation:

1. ✅ Add charts and progress visualization
2. ✅ Implement body weight tracking
3. ✅ Add photo uploads for progress pics
4. ✅ Build historical data views
5. ✅ Implement AI Coach Agents (Phase 3)

---

**Document Version:** 1.0
**Created:** 2025-10-17
**Purpose:** Step-by-step implementation guide for tracking system with USDA API
