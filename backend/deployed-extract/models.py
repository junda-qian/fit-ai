"""
Data models for tracking system

This file defines the structure of all data we'll store.
Pydantic models provide:
- Type safety (catches bugs early)
- Automatic validation (ensures data is correct)
- API documentation (FastAPI uses these to generate docs)
"""
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict
from datetime import datetime, date, time
from uuid import uuid4


# ==================== User Profile ====================
# Stores the results from Energy Calculator (targets & body metrics)

class UserProfile(BaseModel):
    """
    User's fitness targets from Energy Calculator

    This stores all the calculated values like:
    - Daily calorie target
    - Macro targets (protein, carbs, fats)
    - BMR (Basal Metabolic Rate)
    - TDEE (Total Daily Energy Expenditure)
    """
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
    """
    Request model for creating user profile

    This is what the frontend sends to the backend.
    Notice it doesn't include 'id' or timestamps - those are auto-generated.
    """
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
# Stores the generated workout plan from Workout Planner

class Exercise(BaseModel):
    """Single exercise in a workout plan"""
    name: str
    sets: int
    reps: str  # e.g., "6-8", "10-12"
    intensity: Optional[int] = None  # % of 1RM (e.g., 60, 70, 80) - optional for backward compatibility
    rpe: float  # Rate of Perceived Exertion (1-10)
    muscle_group: str
    day: str  # e.g., "Upper A", "Lower B", "Push Day"


class WorkoutPlan(BaseModel):
    """
    User's workout plan from Workout Planner

    This stores the entire workout program:
    - Plan name (e.g., "Upper/Lower Split")
    - All exercises with sets/reps
    - Whether it's currently active
    """
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
# Stores daily meal logs

class FoodItem(BaseModel):
    """
    Individual food item in a meal

    Example:
    {
      "name": "Banana",
      "amount": "1 medium",
      "calories": 105,
      "protein": 1.3,
      "carbs": 27,
      "fats": 0.4,
      "fdc_id": 173944
    }
    """
    name: str
    amount: str  # e.g., "100g", "1 medium", "1 cup"
    calories: float
    protein: float
    carbs: float
    fats: float
    fdc_id: Optional[int] = None  # USDA FoodData Central ID (for tracking which DB entry)


class NutritionLog(BaseModel):
    """
    Single meal/snack entry

    This represents one meal (breakfast, lunch, etc.)
    Contains multiple food items and their totals
    """
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
# Stores completed workout sessions

class ExerciseSet(BaseModel):
    """
    Single set in a workout

    Example: Bench Press - Set 1: 8 reps @ 185 lbs
    """
    reps: int
    weight: float  # in lbs or kg
    rpe: Optional[float] = 7.0  # 1-10 scale, optional (defaults to 7)


class WorkoutExercise(BaseModel):
    """
    Exercise performed in a workout

    Example:
    {
      "name": "Bench Press",
      "sets": [
        {"reps": 8, "weight": 185, "rpe": 7.5},
        {"reps": 8, "weight": 185, "rpe": 8},
        {"reps": 7, "weight": 185, "rpe": 8.5}
      ]
    }
    """
    name: str
    sets: List[ExerciseSet]


class WorkoutLog(BaseModel):
    """
    Completed workout session

    This represents one complete workout (e.g., "Upper Body A")
    """
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
# Stores body measurements and weight

class BodyLog(BaseModel):
    """
    Body measurements and weight tracking

    Supports multiple body composition tracking methods:
    1. Skinfold measurements (PREFERRED) - Most reliable for trend detection
    2. Circumference measurements - Simple and reliable alternative
    3. Body fat % estimates - Least reliable but acceptable
    4. Progress photos - Visual tracking

    Used for tracking weight, body composition, and measurements over time
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str
    date: date
    weight: float  # in kg or lbs

    # Body Composition Method 1: Skinfold Measurements (PREFERRED) ⭐
    # Measures subcutaneous fat thickness directly in millimeters
    # Most reliable for detecting fat mass trends (not affected by hydration)
    skinfolds: Optional[Dict[str, float]] = None  # {tricep: 12.0, abdomen: 18.0, thigh: 17.0, ...}
    skinfold_sum: Optional[float] = None  # Auto-calculated sum of all skinfold sites (mm)

    # Body Composition Method 2: Circumference Measurements (ALTERNATIVE)
    # Simple measurements with tape measure
    waist_cm: Optional[float] = None  # At navel level, morning, empty stomach
    hips_cm: Optional[float] = None
    neck_cm: Optional[float] = None  # For Navy method BF% calculation
    chest_cm: Optional[float] = None
    bicep_cm: Optional[float] = None
    thigh_cm: Optional[float] = None

    # Body Composition Method 3: Body Fat % Estimate (FALLBACK)
    # Less reliable due to measurement error, but still useful
    body_fat_pct: Optional[float] = None
    body_fat_method: Optional[str] = None  # "jackson_pollock_3", "jackson_pollock_7", "navy", "bia_scale", "dexa", "visual"

    # Body Composition Method 4: Progress Photos (OPTIONAL)
    # For visual tracking and AI analysis
    photo_front: Optional[str] = None  # S3 URL or local path
    photo_side: Optional[str] = None
    photo_back: Optional[str] = None

    # Legacy field (deprecated, use specific fields above)
    measurements: Optional[Dict[str, float]] = None  # Generic measurements dict (for backward compatibility)

    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode='after')
    def calculate_skinfold_sum(self):
        """Auto-calculate skinfold_sum if skinfolds are provided but sum is not"""
        if self.skinfolds and not self.skinfold_sum:
            self.skinfold_sum = sum(self.skinfolds.values())
        return self


class BodyLogCreate(BaseModel):
    """
    Request model for creating body log

    All body composition fields are optional - user can track with any combination:
    - Just weight
    - Weight + skinfolds
    - Weight + waist circumference
    - Weight + body fat %
    - Full tracking with all methods
    """
    user_id: str
    date: date
    weight: float

    # Skinfold measurements (preferred method)
    skinfolds: Optional[Dict[str, float]] = None
    skinfold_sum: Optional[float] = None  # Can be provided or auto-calculated

    # Circumference measurements
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    neck_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    bicep_cm: Optional[float] = None
    thigh_cm: Optional[float] = None

    # Body fat percentage
    body_fat_pct: Optional[float] = None
    body_fat_method: Optional[str] = None

    # Progress photos
    photo_front: Optional[str] = None
    photo_side: Optional[str] = None
    photo_back: Optional[str] = None

    # Legacy/generic measurements
    measurements: Optional[Dict[str, float]] = None

    notes: Optional[str] = None

    @model_validator(mode='after')
    def calculate_skinfold_sum(self):
        """Auto-calculate skinfold_sum if skinfolds are provided but sum is not"""
        if self.skinfolds and not self.skinfold_sum:
            self.skinfold_sum = sum(self.skinfolds.values())
        return self


# ==================== Daily Summary ====================
# Pre-computed daily aggregation for fast dashboard loads

class DailySummary(BaseModel):
    """
    Pre-computed daily aggregation

    Why we need this:
    - Dashboard needs to load fast
    - Instead of summing all meals every time, we pre-compute totals
    - Updated whenever a new log is added
    """
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
# Models for USDA API responses

class USDAFood(BaseModel):
    """
    Parsed food from USDA API

    This is the cleaned/simplified version of USDA data
    """
    fdc_id: int
    description: str
    calories: float
    protein: float
    carbs: float
    fats: float
    serving_size: str
    serving_unit: str


class FoodSearchResult(BaseModel):
    """
    Search results from USDA API

    This is what our food search endpoint returns
    """
    query: str
    total_results: int
    foods: List[USDAFood]
